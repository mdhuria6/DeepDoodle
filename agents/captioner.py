from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple, TypedDict, Literal, Optional 
import os
import shutil 

from models.comic_generation_state import ComicGenerationState # Import from models
from utils.config import (
    BUNDLED_FONT_PATH, 
    MAX_FONT_SIZE, 
    DEFAULT_FONT_SIZE,
    MIN_FONT_SIZE,
    LINE_SPACING,
    CAPTION_MARGIN, 
    CAPTION_PADDING,
    MAX_CAPTION_HEIGHT_RATIO,
    CAPTION_BACKGROUND_COLOR,
    NARRATOR_BACKGROUND_COLOR,
    CAPTION_TEXT_COLOR,
    CAPTION_CORNER_RADIUS,
    CAPTIONED_PANELS_DIR
)
from models.caption import Caption # Import Caption from models

def format_caption_text(caption: Caption) -> str:
    """Formats the caption text by prepending speaker/type and handling newlines."""
    text = caption['text'].replace('\\\\n', '\\n') # Replace literal '\\\\n' from source to actual newlines
    speaker = caption.get('speaker')
    caption_type = caption.get('type', 'caption') # Default to 'caption' if type is missing

    if caption_type == "dialogue" and speaker:
        return f"{speaker}: {text}"
    elif caption_type == "sfx":
        # SFX might not need a "SFX:" prefix if styling is distinct, but for now:
        return f"SFX: {text}"
    elif caption_type == "narrator" and speaker:
        return f"{speaker}: {text}" # e.g., "Stan Lee: Meanwhile..."
    elif caption_type == "narrator":
        return f"Narrator: {text}"
    elif caption_type == "caption" and speaker: # A general caption attributed to someone
        return f"{speaker}: {text}"
    elif caption_type == "caption": # Unattributed general caption
        return text # Or "Caption: {text}" if explicit prefix is desired
    elif speaker: # Some other type with a speaker
        return f"{speaker} ({caption_type}): {text}"
    else: # Some other type, no speaker
        return f"{caption_type.upper()}: {text}"


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, max_height: int, line_spacing: int) -> Tuple[List[str], int]:
    """Wraps text to fit within max_width and tries to respect max_height.
    Returns a list of lines and the calculated total height of the wrapped text block.
    """
    final_lines: List[str] = []
    if not text or max_width <= 0 or max_height <= 0:
        return final_lines, 0

    # Effective max width with a small buffer
    effective_max_width = max_width * 0.98 # Adjusted buffer slightly

    # Determine a reasonable fallback for line height based on font size
    _font_size_fallback = DEFAULT_FONT_SIZE
    if hasattr(font, 'size') and isinstance(font.size, (int, float)) and font.size > 0:
        _font_size_fallback = font.size

    # Estimate single line render height (ascent + descent)
    try:
        # Using a string with ascenders and descenders for better bbox
        char_bbox_Ay = font.getbbox("Ay")
        single_line_render_height = char_bbox_Ay[3] - char_bbox_Ay[1]
        if single_line_render_height <= 0: # If bbox is weird
            single_line_render_height = _font_size_fallback
    except AttributeError: # Fallback for fonts not supporting getbbox well
        try:
            # getsize often gives width, height of the whole text, not ideal for single line height
            # but can be a fallback if getbbox is not present or fails.
            _, single_line_render_height = font.getsize("A")
            if single_line_render_height <= 0: single_line_render_height = _font_size_fallback
        except AttributeError:
            single_line_render_height = _font_size_fallback
    except Exception:
        single_line_render_height = _font_size_fallback
    
    if single_line_render_height <= 0: # Final check
        single_line_render_height = _font_size_fallback


    # Split text by pre-existing newlines first
    # format_caption_text should have converted literal \\\\n to \\n
    initial_segments = text.split('\n')
    
    current_accumulated_height = 0
    lines_wrapped_count = 0

    for segment in initial_segments:
        if not segment.strip(): # Handle empty lines (e.g. double newlines in input)
            # Check if adding an empty line (height of one line + spacing) exceeds max_height
            height_of_empty_line = single_line_render_height
            required_spacing = line_spacing if lines_wrapped_count > 0 else 0
            
            if current_accumulated_height + required_spacing + height_of_empty_line <= max_height:
                if lines_wrapped_count > 0:
                    current_accumulated_height += line_spacing
                final_lines.append("")
                current_accumulated_height += height_of_empty_line
                lines_wrapped_count += 1
            else:
                # Cannot fit this empty line, so stop further processing
                break 
            continue

        words = segment.split(' ')
        current_line_text = ""
        for i, word in enumerate(words):
            word_to_add = word
            if current_line_text: # Add space if not the first word on this line
                word_to_add = " " + word

            # Check if the current line + new word fits the width
            if font.getlength(current_line_text + word_to_add) <= effective_max_width:
                current_line_text += word_to_add
            else:
                # Word doesn't fit, so current_line_text is complete (if it has content)
                if current_line_text:
                    required_spacing = line_spacing if lines_wrapped_count > 0 else 0
                    if current_accumulated_height + required_spacing + single_line_render_height <= max_height:
                        if lines_wrapped_count > 0:
                            current_accumulated_height += line_spacing
                        final_lines.append(current_line_text)
                        current_accumulated_height += single_line_render_height
                        lines_wrapped_count += 1
                    else:
                        # This line makes it too tall, stop all wrapping
                        current_accumulated_height = max_height + 1 # Mark as overflow
                        break 
                
                # Start new line with the current word
                current_line_text = word
                # If the word itself is too long, truncate it (basic truncation)
                while font.getlength(current_line_text) > effective_max_width:
                    if len(current_line_text) <= 1: break # Avoid infinite loop on single char
                    current_line_text = current_line_text[:-1]
            
            if current_accumulated_height > max_height: break # Break from word loop

        # Add the last line of the current segment if it has content and fits
        if current_accumulated_height <= max_height and current_line_text:
            required_spacing = line_spacing if lines_wrapped_count > 0 else 0
            if current_accumulated_height + required_spacing + single_line_render_height <= max_height:
                if lines_wrapped_count > 0:
                    current_accumulated_height += line_spacing
                final_lines.append(current_line_text)
                current_accumulated_height += single_line_render_height
                lines_wrapped_count += 1
            else:
                # This final part of segment makes it too tall
                current_accumulated_height = max_height + 1 # Mark as overflow

        if current_accumulated_height > max_height: break # Break from segment loop

    # If text was truncated due to height, add ellipsis to the last fitting line
    if current_accumulated_height > max_height and final_lines:
        last_line = final_lines[-1]
        ellipsis = "..."
        # Check if ellipsis can be added without exceeding width
        if font.getlength(last_line + ellipsis) <= effective_max_width:
            final_lines[-1] = last_line + ellipsis
        else:
            # Shorten last line to make space for ellipsis
            while len(last_line) > 0 and font.getlength(last_line + ellipsis) > effective_max_width:
                last_line = last_line[:-1]
            if not last_line and font.getlength(ellipsis) <= effective_max_width : # If line became empty, just put ellipsis
                 final_lines[-1] = ellipsis
            elif last_line :
                 final_lines[-1] = last_line + ellipsis
            # If ellipsis itself is too long (very narrow width), it might not be added or might be truncated by earlier logic.
            # Or, if the last line became empty and ellipsis doesn't fit, the line might be removed or left as is.
            # For simplicity, if last_line + ellipsis doesn't fit after shortening, we might lose the ellipsis.
            # A more robust way would be to ensure the last line is short enough for ellipsis from the start if truncation is likely.

    # Recalculate final height based on actual lines added and their precise render heights if possible
    # For simplicity, current_accumulated_height is a good estimate if single_line_render_height is accurate.
    # If more precision is needed, iterate final_lines, get bbox for each, sum heights + spacings.
    # The current current_accumulated_height already includes spacings.
    
    # The height returned should be the total height occupied by the text block
    # If no lines, height is 0.
    # If lines, it's (num_lines * single_line_render_height) + ((num_lines - 1) * line_spacing)
    # current_accumulated_height should reflect this.
    
    # Ensure returned height is not greater than max_height if truncation occurred.
    # However, the caller might want to know the "would-be" height if not truncated,
    # or the actual height of the truncated text. The current logic aims for the latter.
    
    final_calculated_height = 0
    if final_lines:
        num_lines = len(final_lines)
        final_calculated_height = (num_lines * single_line_render_height) + (max(0, num_lines - 1) * line_spacing)
        final_calculated_height = min(final_calculated_height, max_height) # Cap at max_height

    return final_lines, final_calculated_height


def add_texts_to_image(image_path: str, captions: List[Caption], panel_width: int, panel_height: int, panel_idx_for_logging: int = -1) -> Image.Image:
    """Adds formatted text captions to an image, managing layout and font size dynamically.
    Returns a PIL Image object with captions drawn.
    """
    try:
        img = Image.open(image_path).convert("RGBA")
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        img = Image.new("RGBA", (panel_width, panel_height), "red")
        draw = ImageDraw.Draw(img)
        try:
            error_font = ImageFont.truetype(BUNDLED_FONT_PATH, 20)
        except IOError:
            error_font = ImageFont.load_default()
        draw.text((10, 10), f"Error: Missing {os.path.basename(image_path)}", fill="white", font=error_font)
        return img
        
    draw = ImageDraw.Draw(img)

    if not captions:
        return img

    # --- Configuration ---
    current_font_size = MAX_FONT_SIZE # Start with max font size from config/top of file
    min_font_size = MIN_FONT_SIZE # Use MIN_FONT_SIZE from config

    # Max height for the entire caption block
    max_block_height_px = int(panel_height * MAX_CAPTION_HEIGHT_RATIO)
    
    # Available width for text within a caption bubble, considering panel margins and bubble padding
    text_area_width = panel_width - 2 * CAPTION_MARGIN - 2 * CAPTION_PADDING

    # --- Font Size Adjustment ---
    final_font = None
    all_wrapped_captions_for_final_font = []

    while current_font_size >= min_font_size:
        font_to_test = None
        try:
            # Attempt 1: Bundled font with RAQM
            font_to_test = ImageFont.truetype(BUNDLED_FONT_PATH, current_font_size, layout_engine=ImageFont.Layout.RAQM) # Corrected here
        except ImportError:
            # print(f"Info: Pillow lacks RAQM support. Falling back to basic layout for {BUNDLED_FONT_PATH} at size {current_font_size}.")
            try:
                font_to_test = ImageFont.truetype(BUNDLED_FONT_PATH, current_font_size)
            except IOError: 
                # print(f"Error: Font file {BUNDLED_FONT_PATH} not found/unreadable (basic fallback).")
                font_to_test = None # Mark as failed for this path/size
            except Exception as e_basic_fallback:
                # print(f"Error loading {BUNDLED_FONT_PATH} with basic layout (fallback): {e_basic_fallback}.")
                font_to_test = None
        except IOError: # IOError for BUNDLED_FONT_PATH with RAQM attempt
            # print(f"Error: Font file {BUNDLED_FONT_PATH} not found/unreadable (RAQM attempt). Trying basic layout.")
            try:
                font_to_test = ImageFont.truetype(BUNDLED_FONT_PATH, current_font_size)
            except IOError: 
                # print(f"Error: Font file {BUNDLED_FONT_PATH} still not found/unreadable (basic after RAQM IOError).")
                font_to_test = None
            except Exception as e_basic_after_raqm_io:
                # print(f"Error loading {BUNDLED_FONT_PATH} with basic layout (after RAQM IOError): {e_basic_after_raqm_io}.")
                font_to_test = None
        except OSError as e_os_raqm: # Specifically catch OSError for RAQM, e.g. libraqm not found/functional
            print(f"Warning: RAQM failed for {BUNDLED_FONT_PATH} at size {current_font_size} (OSError: {e_os_raqm}). Trying basic layout.")
            try:
                font_to_test = ImageFont.truetype(BUNDLED_FONT_PATH, current_font_size)
            except IOError:
                # print(f"Error: Font file {BUNDLED_FONT_PATH} not found/unreadable (basic after RAQM OSError).")
                font_to_test = None
            except Exception as e_basic_after_raqm_oserror:
                # print(f"Error loading {BUNDLED_FONT_PATH} with basic layout (after RAQM OSError): {e_basic_after_raqm_oserror}.")
                font_to_test = None
        except Exception as e_other_raqm: # Catch any other unexpected errors from RAQM attempt
            print(f"Warning: RAQM failed unexpectedly for {BUNDLED_FONT_PATH} at size {current_font_size} (Error: {e_other_raqm}). Trying basic layout.")
            try:
                font_to_test = ImageFont.truetype(BUNDLED_FONT_PATH, current_font_size)
            except IOError:
                # print(f"Error: Font file {BUNDLED_FONT_PATH} not found/unreadable (basic after RAQM other error).")
                font_to_test = None
            except Exception as e_basic_after_raqm_other:
                # print(f"Error loading {BUNDLED_FONT_PATH} with basic layout (after RAQM other error): {e_basic_after_raqm_other}.")
                font_to_test = None

        if not font_to_test:
            # BUNDLED_FONT_PATH failed for current_font_size with all attempts (RAQM and basic)
            # OR BUNDLED_FONT_PATH itself had an IOError.
            # Continue to the next smaller font size. If all sizes fail for BUNDLED_FONT_PATH,
            # the `if not final_font:` block after the loop will attempt `ImageFont.load_default()`.
            # print(f"Warning: Could not load font {BUNDLED_FONT_PATH} at size {current_font_size}. Trying smaller size or will use default.")
            current_font_size -= 1
            continue # Go to next iteration of the while loop (try smaller size)

        # --- If font_to_test is successfully loaded, proceed with wrapping and height calculation ---
        current_block_total_height = 0
        temp_wrapped_captions_for_this_size = []
        possible_to_fit_all_at_this_size = True

        for caption_idx, caption_data in enumerate(captions):
            formatted_text = format_caption_text(caption_data)
            if not formatted_text.strip(): 
                temp_wrapped_captions_for_this_size.append(({'text_lines': [], 'text_height': 0, 'original_caption': caption_data}))
                continue

            wrapped_lines, text_height_from_wrap = wrap_text(formatted_text, font_to_test, text_area_width, max_block_height_px, LINE_SPACING)
            
            if not wrapped_lines: 
                possible_to_fit_all_at_this_size = False
                break 

            bubble_height_for_this_caption = text_height_from_wrap + 2 * CAPTION_PADDING
            current_block_total_height += bubble_height_for_this_caption
            
            if caption_idx > 0: 
                current_block_total_height += CAPTION_MARGIN
            
            temp_wrapped_captions_for_this_size.append(({'text_lines': wrapped_lines, 'text_height': text_height_from_wrap, 'original_caption': caption_data}))

        if not possible_to_fit_all_at_this_size:
            current_font_size -= 1 
            continue

        if current_block_total_height <= max_block_height_px:
            final_font = font_to_test
            all_wrapped_captions_for_final_font = temp_wrapped_captions_for_this_size
            break 
        else:
            current_font_size -= 1 
            if current_font_size < min_font_size:
                final_font = font_to_test 
                all_wrapped_captions_for_final_font = temp_wrapped_captions_for_this_size
                break
    
    if not final_font:
        print(f"Error: Could not determine a final font. Using Pillow's default. Panel: {panel_idx_for_logging}")
        try:
            final_font = ImageFont.load_default() 
        except IOError: 
             print(f"CRITICAL: ImageFont.load_default() failed. Cannot draw text. Panel: {panel_idx_for_logging}")
             return img 

        all_wrapped_captions_for_final_font = []
        current_block_total_height = 0 
        for caption_data in captions:
            formatted_text = format_caption_text(caption_data)
            if not formatted_text.strip():
                all_wrapped_captions_for_final_font.append(({'text_lines': [], 'text_height': 0, 'original_caption': caption_data}))
                continue
            wrapped_lines, text_height_from_wrap = wrap_text(formatted_text, final_font, text_area_width, max_block_height_px, LINE_SPACING)
            if not wrapped_lines: 
                first_line = formatted_text.split('\\n')[0]
                temp_text = ""
                for char in first_line:
                    if final_font.getsize(temp_text + char)[0] <= text_area_width:
                        temp_text += char
                    else:
                        break
                wrapped_lines = [temp_text + "..." if len(temp_text) < len(first_line) else temp_text]

                if wrapped_lines:
                    bbox = final_font.getbbox(wrapped_lines[0])
                    text_height_from_wrap = bbox[3] - bbox[1] if bbox else final_font.size 
                else: 
                    text_height_from_wrap = 0

            bubble_height_for_this_caption = text_height_from_wrap + 2 * CAPTION_PADDING
            current_block_total_height += bubble_height_for_this_caption
            if len(all_wrapped_captions_for_final_font) > 0: current_block_total_height += CAPTION_MARGIN
            all_wrapped_captions_for_final_font.append(({'text_lines': wrapped_lines, 'text_height': text_height_from_wrap, 'original_caption': caption_data}))

    # --- Drawing Phase ---
    actual_block_height = 0
    non_empty_caption_count_for_drawing = 0
    for wrapped_caption_info in all_wrapped_captions_for_final_font:
        if wrapped_caption_info['text_lines']:
            actual_block_height += (wrapped_caption_info['text_height'] + 2 * CAPTION_PADDING)
            if non_empty_caption_count_for_drawing > 0:
                actual_block_height += CAPTION_MARGIN
            non_empty_caption_count_for_drawing +=1
        
    current_bubble_top_y = panel_height - actual_block_height - CAPTION_MARGIN 

    for wrapped_caption_info in all_wrapped_captions_for_final_font:
        original_caption_data = wrapped_caption_info['original_caption']
        wrapped_lines = wrapped_caption_info['text_lines']
        text_height_from_wrap = wrapped_caption_info['text_height']

        if not wrapped_lines: 
            continue

        caption_type = original_caption_data.get("type", "dialogue")
        
        max_line_width = 0
        if wrapped_lines:
            for line in wrapped_lines:
                line_bbox = final_font.getbbox(line)
                line_width = line_bbox[2] - line_bbox[0] if line_bbox else 0
                if line_width > max_line_width:
                    max_line_width = line_width
        
        bg_width = max_line_width + 2 * CAPTION_PADDING
        bg_height = text_height_from_wrap + 2 * CAPTION_PADDING

        bg_x0 = CAPTION_MARGIN 
        bg_y0 = current_bubble_top_y
        bg_x1 = bg_x0 + bg_width
        bg_y1 = bg_y0 + bg_height

        if caption_type == "dialogue":
            draw.rounded_rectangle(
                (bg_x0, bg_y0, bg_x1, bg_y1),
                radius=CAPTION_CORNER_RADIUS,
                fill=CAPTION_BACKGROUND_COLOR
            )
        elif caption_type == "narrator":
            draw.rectangle(
                (bg_x0, bg_y0, bg_x1, bg_y1),
                fill=NARRATOR_BACKGROUND_COLOR 
            )
        elif caption_type == "sfx":
            pass 

        text_draw_x = bg_x0 + CAPTION_PADDING
        current_line_y_offset_in_bubble = CAPTION_PADDING # Start drawing text from top padding

        for line_idx, line in enumerate(wrapped_lines):
            y_position_for_line = bg_y0 + current_line_y_offset_in_bubble
            if line_idx > 0:
                 line_bbox_prev = final_font.getbbox(wrapped_caption_info['text_lines'][line_idx-1])
                 prev_line_h = (line_bbox_prev[3] - line_bbox_prev[1]) if line_bbox_prev else final_font.size
                 current_line_y_offset_in_bubble += prev_line_h + LINE_SPACING
                 y_position_for_line = bg_y0 + current_line_y_offset_in_bubble

            # Add stroke for potentially better clarity at small sizes
            draw.text((text_draw_x, y_position_for_line), 
                      line, 
                      fill=CAPTION_TEXT_COLOR, 
                      font=final_font, 
                      anchor="lt"
                     )

        current_bubble_top_y += (bg_height + CAPTION_MARGIN)

    return img

def captioner(state: ComicGenerationState) -> dict:
    """Node 6: Adds captions to each sized panel image."""
    print(f"---AGENT: Captioner---")

    sized_panel_paths = state.get("sized_panel_image_paths", [])
    scenes_data = state.get("scenes", [])
    layout_style = state.get("layout_style", "grid_2x2") # Get layout_style

    if not sized_panel_paths:
        print("Error: No sized panel paths found in state for captioner.")
        return {"panel_images_with_captions_paths": [], "scenes": scenes_data, "layout_style": layout_style}

    if len(sized_panel_paths) != len(scenes_data):
        print(f"Warning: Mismatch between number of sized panels ({len(sized_panel_paths)}) and scenes ({len(scenes_data)}). Captioning based on available panels.")

    # Ensure output directory for captioned panels exists
    os.makedirs(CAPTIONED_PANELS_DIR, exist_ok=True)
    # Clean up the directory before new generation
    # for filename in os.listdir(CAPTIONED_PANELS_DIR):
    #     file_path = os.path.join(CAPTIONED_PANELS_DIR, filename)
    #     try:
    #         if os.path.isfile(file_path) or os.path.islink(file_path):
    #             os.unlink(file_path)
    #         elif os.path.isdir(file_path):
    #             shutil.rmtree(file_path)
    #     except Exception as e:
    #         print(f'Failed to delete {file_path}. Reason: {e}')

    panel_images_with_captions_paths = []

    for idx, sized_panel_path in enumerate(sized_panel_paths):
        if idx >= len(scenes_data):
            print(f"Skipping captioning for panel {idx+1} as no corresponding scene data found.")
            # Optionally, copy the image as-is if no captions are to be added
            # shutil.copy(sized_panel_path, os.path.join(CAPTIONED_PANELS_DIR, os.path.basename(sized_panel_path)))
            # panel_images_with_captions_paths.append(os.path.join(CAPTIONED_PANELS_DIR, os.path.basename(sized_panel_path)))
            continue

        panel_captions = scenes_data[idx].get('captions', [])
        
        # Get panel dimensions from the image itself, as it's already sized
        try:
            with Image.open(sized_panel_path) as temp_img:
                panel_width, panel_height = temp_img.size
        except FileNotFoundError:
            print(f"Error: Sized panel image not found at {sized_panel_path}. Skipping captioning for this panel.")
            continue
        except Exception as e:
            print(f"Error opening sized panel image {sized_panel_path}: {e}. Skipping captioning.")
            continue

        print(f"   > Adding captions to panel {idx + 1} (Image: {os.path.basename(sized_panel_path)}), Captions: {len(panel_captions)}")
        
        # Add text to the *sized* image
        captioned_image = add_texts_to_image(sized_panel_path, panel_captions, panel_width, panel_height, panel_idx_for_logging=idx)

        # Save the image with captions
        base_name = os.path.basename(sized_panel_path)
        name, ext = os.path.splitext(base_name)
        # Ensure the extension is .png for consistency, even if original was .jpg etc.
        output_filename = f"{name}_captioned.png" 
        output_path_captioned = os.path.join(CAPTIONED_PANELS_DIR, output_filename)
        
        try:
            captioned_image.save(output_path_captioned, "PNG")
            panel_images_with_captions_paths.append(output_path_captioned)
            print(f"     > Saved captioned panel to: {output_path_captioned}")
        except Exception as e:
            print(f"Error saving captioned image {output_path_captioned}: {e}")

    return {
        "panel_images_with_captions_paths": panel_images_with_captions_paths,
        "scenes": scenes_data,  # Pass through scenes data
        "layout_style": layout_style # Pass through layout_style
    }

