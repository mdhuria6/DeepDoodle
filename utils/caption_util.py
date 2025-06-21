from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple, TypedDict, Literal, Optional
import os

from models.caption import Caption 
from models.caption_style_metadata import CaptionStyleMetadata


# --- Text Formatting and Wrapping ---
def format_caption_text(caption: Caption) -> str:
    """Formats the caption text by prepending speaker/type and handling newlines."""
    text = caption.get('text', '').replace('\\n', '\n')
    speaker = caption.get('speaker')
    caption_type = caption.get('type', 'caption')

    if caption_type == "dialogue" and speaker:
        return f"{speaker}: {text}"
    elif caption_type == "sfx":
        return f"SFX: {text}" # Assuming SFX text itself is the effect
    elif caption_type == "narrator" and speaker:
        return f"{speaker}: {text}"
    elif caption_type == "narration":
        return f"Narrator: {text}"
    elif caption_type == "caption" and speaker:
        return f"{speaker}: {text}"
    elif caption_type == "caption":
        return text
    elif speaker: # Fallback for other types with a speaker
        return f"{speaker} ({caption_type}): {text}"
    else: # Fallback for other types, no speaker
        return f"{caption_type.upper()}: {text}"

def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, max_height: int, line_spacing: int, default_font_size_for_metric: int) -> Tuple[List[str], int]:
    """Wraps text to fit within max_width and tries to respect max_height.
    Returns a list of lines and the calculated total height of the wrapped text block.
    """
    final_lines: List[str] = []
    if not text or max_width <= 0 or max_height <= 0:
        return final_lines, 0

    effective_max_width = max_width * 0.98
    _font_size_fallback = default_font_size_for_metric
    if hasattr(font, 'size') and isinstance(font.size, (int, float)) and font.size > 0:
        _font_size_fallback = font.size

    try:
        char_bbox_Ay = font.getbbox("Ay") # Use characters with ascenders/descenders
        single_line_render_height = char_bbox_Ay[3] - char_bbox_Ay[1]
        if single_line_render_height <= 0: # Safety check
            single_line_render_height = _font_size_fallback
    except Exception: # Broad exception for any font metric issues
        single_line_render_height = _font_size_fallback
    
    if single_line_render_height <= 0: # Final safety
        single_line_render_height = _font_size_fallback


    initial_segments = text.split('\n')
    current_accumulated_height = 0
    lines_wrapped_count = 0

    for segment in initial_segments:
        if not segment.strip(): # Handle empty lines (e.g. double newlines in input)
            height_of_empty_line = single_line_render_height
            required_spacing = line_spacing if lines_wrapped_count > 0 else 0
            if current_accumulated_height + required_spacing + height_of_empty_line <= max_height:
                if lines_wrapped_count > 0: current_accumulated_height += line_spacing
                final_lines.append("")
                current_accumulated_height += height_of_empty_line
                lines_wrapped_count += 1
            else:
                break # Cannot fit this empty line
            continue

        words = segment.split(' ')
        current_line_text = ""
        for word_idx, word in enumerate(words):
            word_to_add = (" " + word) if current_line_text else word # Add space if not first word on line

            if font.getlength(current_line_text + word_to_add) <= effective_max_width:
                current_line_text += word_to_add
            else: # Word doesn't fit, current_line_text is complete (if it has content)
                if current_line_text:
                    required_spacing = line_spacing if lines_wrapped_count > 0 else 0
                    if current_accumulated_height + required_spacing + single_line_render_height <= max_height:
                        if lines_wrapped_count > 0: current_accumulated_height += line_spacing
                        final_lines.append(current_line_text)
                        current_accumulated_height += single_line_render_height
                        lines_wrapped_count += 1
                    else:
                        current_accumulated_height = max_height + 1; break # Mark as overflow and stop segment
                
                current_line_text = word # Start new line with the current word
                # If the word itself is too long, truncate it (basic truncation)
                while font.getlength(current_line_text) > effective_max_width:
                    if len(current_line_text) <= 1: break # Avoid infinite loop
                    current_line_text = current_line_text[:-1]
            
            if current_accumulated_height > max_height: break # Break from word loop if overflow

        # Add the last line of the current segment if it has content and fits
        if current_accumulated_height <= max_height and current_line_text:
            required_spacing = line_spacing if lines_wrapped_count > 0 else 0
            if current_accumulated_height + required_spacing + single_line_render_height <= max_height:
                if lines_wrapped_count > 0: current_accumulated_height += line_spacing
                final_lines.append(current_line_text)
                current_accumulated_height += single_line_render_height
                lines_wrapped_count += 1
            else: # This final part of segment makes it too tall
                current_accumulated_height = max_height + 1 # Mark as overflow

        if current_accumulated_height > max_height: break # Break from segment loop if overflow

    # If text was truncated due to height, add ellipsis to the last fitting line
    if current_accumulated_height > max_height and final_lines:
        last_line = final_lines[-1]
        ellipsis = "..."
        # Check if ellipsis can be added without exceeding width
        if font.getlength(last_line + ellipsis) <= effective_max_width:
            final_lines[-1] = last_line + ellipsis
        else: # Shorten last line to make space for ellipsis
            while len(last_line) > 0 and font.getlength(last_line + ellipsis) > effective_max_width:
                last_line = last_line[:-1]
            if last_line or font.getlength(ellipsis) <= effective_max_width : # If line became empty, just put ellipsis
                 final_lines[-1] = last_line + ellipsis if last_line else ellipsis

    final_calculated_height = 0
    if final_lines:
        num_lines = len(final_lines)
        final_calculated_height = (num_lines * single_line_render_height) + (max(0, num_lines - 1) * line_spacing)
        final_calculated_height = min(final_calculated_height, max_height) # Cap at max_height
    return final_lines, final_calculated_height

# --- Image and Font Handling ---
def load_panel_image(image_path: str, panel_width: int, panel_height: int, style_config: CaptionStyleMetadata) -> Tuple[Image.Image, ImageDraw.Draw, bool]:
    """Loads the panel image. Returns the image, its drawing context, and a flag indicating if it's an error image."""
    try:
        img = Image.open(image_path).convert("RGBA")
        return img, ImageDraw.Draw(img), False
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        img = Image.new("RGBA", (panel_width, panel_height), "red") # Create a red error image
        draw = ImageDraw.Draw(img)
        try:
            # Use a basic font for error message, attempt configured font first
            error_font = ImageFont.truetype(style_config['font_path'], 20)
        except IOError:
            error_font = ImageFont.load_default() # Absolute fallback
        draw.text((10, 10), f"Error: Missing {os.path.basename(image_path)}", fill="white", font=error_font)
        return img, draw, True # True indicates it's an error image

def _try_load_font(font_path: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
    """Attempts to load a font with RAQM, falling back to basic layout."""
    try:
        return ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.RAQM)
    except ImportError: # Pillow lacks RAQM
        # print(f"Info: RAQM not supported by Pillow. Falling back to basic layout for {font_path} size {size}.")
        pass # Fall through to basic
    except OSError as e_os: # libraqm might be missing or problematic
        print(f"Warning: RAQM OSError for {font_path} at size {size} ({e_os}). Trying basic.")
    except IOError: # Font file not found or unreadable at RAQM stage
        print(f"Error: Font file {font_path} not found/unreadable for RAQM, size {size}. Trying basic.")
        # Do not return None yet, try basic layout
    except Exception as e_raqm: # Other RAQM errors
        print(f"Warning: RAQM failed for {font_path} at size {size} ({e_raqm}). Trying basic.")

    # Basic layout fallback
    try:
        return ImageFont.truetype(font_path, size)
    except IOError: # Still failed with basic
        # This is a more definitive failure for this font_path and size
        print(f"Error: Font file {font_path} still not found/unreadable (basic fallback) for size {size}.")
        return None
    except Exception as e_basic:
        print(f"Error loading {font_path} with basic layout (fallback) for size {size}: {e_basic}.")
        return None

def determine_font_and_layout(
    captions_data: List[Caption],
    text_area_width: int,
    max_block_height_px: int,
    style_config: CaptionStyleMetadata,
    panel_idx_for_logging: int = -1
) -> Tuple[Optional[ImageFont.FreeTypeFont], List[Dict]]:
    """
    Determines the optimal font size and prepares wrapped text lines for all captions.
    Returns the chosen font and a list of dictionaries, each containing wrapped lines and original caption data.
    """
    current_font_size = style_config['max_font_size']
    final_font: Optional[ImageFont.FreeTypeFont] = None
    all_wrapped_captions_for_final_font: List[Dict] = []

    while current_font_size >= style_config['min_font_size']:
        font_to_test = _try_load_font(style_config['font_path'], current_font_size)
        if not font_to_test:
            # print(f"Panel {panel_idx_for_logging+1}: Failed to load main font at size {current_font_size}. Trying smaller.")
            current_font_size -= 1
            continue

        current_block_total_height = 0
        temp_wrapped_captions_for_this_size = []
        possible_to_fit_all = True

        for caption_idx, caption_data_item in enumerate(captions_data):
            formatted_text = format_caption_text(caption_data_item)
            if not formatted_text.strip(): # Handle empty/whitespace-only captions
                temp_wrapped_captions_for_this_size.append({'text_lines': [], 'text_height': 0, 'original_caption': caption_data_item})
                continue

            wrapped_lines, text_height_from_wrap = wrap_text(
                formatted_text, font_to_test, text_area_width, max_block_height_px, # Pass max_block_height_px to wrap_text
                style_config['line_spacing'], style_config['default_font_size']
            )

            if not wrapped_lines and formatted_text: # Text exists but couldn't be wrapped
                possible_to_fit_all = False
                break
            
            bubble_height_for_this_caption = text_height_from_wrap + 2 * style_config['caption_padding']
            current_block_total_height += bubble_height_for_this_caption
            
            # Add margin between bubbles if this is not the first bubble AND it has content
            if temp_wrapped_captions_for_this_size and temp_wrapped_captions_for_this_size[-1]['text_lines'] and wrapped_lines:
                 current_block_total_height += style_config['caption_margin']
            
            temp_wrapped_captions_for_this_size.append({
                'text_lines': wrapped_lines,
                'text_height': text_height_from_wrap,
                'original_caption': caption_data_item
            })

        if not possible_to_fit_all:
            current_font_size -= 1
            continue # Try smaller font size

        if current_block_total_height <= max_block_height_px:
            final_font = font_to_test
            all_wrapped_captions_for_final_font = temp_wrapped_captions_for_this_size
            break # Found a good fit
        else:
            current_font_size -= 1
            # If this was the last attempt (min_font_size) and we still don't have a final_font,
            # use this font and its layout, even if it overflows.
            if current_font_size < style_config['min_font_size'] and not final_font:
                final_font = font_to_test
                all_wrapped_captions_for_final_font = temp_wrapped_captions_for_this_size
                print(f"Warning: Panel {panel_idx_for_logging+1}: Text might overflow with custom font at min size {style_config['min_font_size']}. Block height: {current_block_total_height} > max: {max_block_height_px}")
                break


    if not final_font: # Custom font failed at all sizes or wasn't loadable at all
        print(f"Panel {panel_idx_for_logging+1}: Custom font '{style_config['font_path']}' failed or too large at all tried sizes. Using Pillow's default font.")
        try:
            final_font = ImageFont.load_default()
        except IOError:
            print(f"CRITICAL: Panel {panel_idx_for_logging+1}: ImageFont.load_default() failed. Cannot draw text.")
            return None, [] # Cannot proceed

        # Re-wrap with default font
        all_wrapped_captions_for_final_font = []
        # current_block_total_height_default = 0 # Recalculate for default font
        for caption_data_item in captions_data:
            formatted_text = format_caption_text(caption_data_item)
            if not formatted_text.strip():
                 all_wrapped_captions_for_final_font.append({'text_lines': [], 'text_height': 0, 'original_caption': caption_data_item})
                 continue

            wrapped_lines, text_height_from_wrap = wrap_text(
                formatted_text, final_font, text_area_width, max_block_height_px, # Pass max_block_height_px
                style_config['line_spacing'], style_config['default_font_size'] # default_font_size for metrics
            )
            
            if not wrapped_lines and formatted_text: # Truncate if default font still doesn't fit
                first_line_segment = formatted_text.split('\n')[0]
                temp_text = ""
                for char_idx, char_val in enumerate(first_line_segment):
                    # Use getlength for default font as well
                    if final_font.getlength(temp_text + char_val) <= text_area_width:
                        temp_text += char_val
                    else: break
                processed_line = temp_text + "..." if len(temp_text) < len(first_line_segment) else temp_text
                wrapped_lines = [processed_line] if processed_line else ["..."] # Ensure there's at least an ellipsis
                
                if wrapped_lines and wrapped_lines[0]:
                    bbox = final_font.getbbox(wrapped_lines[0])
                    text_height_from_wrap = (bbox[3] - bbox[1]) if bbox else final_font.size
                else: text_height_from_wrap = 0


            all_wrapped_captions_for_final_font.append({
                'text_lines': wrapped_lines,
                'text_height': text_height_from_wrap,
                'original_caption': caption_data_item
            })
            # Note: Height check for default font is implicitly handled by wrap_text's max_height.
            # We are not re-evaluating total block height here for default font for simplicity,
            # as the primary goal is to render *something*.

    return final_font, all_wrapped_captions_for_final_font

# --- Drawing ---
def draw_caption_bubbles(
    draw: ImageDraw.Draw,
    font: ImageFont.FreeTypeFont,
    wrapped_captions_info: List[Dict], 
    panel_height: int,
    style_config: CaptionStyleMetadata
) -> None:
    """Draws all caption bubbles and text onto the image."""
    # print(f"DEBUG [caption_utils.draw_caption_bubbles]: style_config received: border_color='{style_config.get('border_color')}', border_width={style_config.get('border_width')}") # DEBUG print

    actual_block_height = 0
    non_empty_caption_count_for_drawing = 0
    for idx, info in enumerate(wrapped_captions_info):
        if info['text_lines']: # Only consider captions that will be drawn
            actual_block_height += (info['text_height'] + 2 * style_config['caption_padding'])
            # Add margin if not the first visible bubble
            if non_empty_caption_count_for_drawing > 0: # Add margin if not the first visible bubble
                actual_block_height += style_config['caption_margin']
            non_empty_caption_count_for_drawing += 1
        
    # Position the entire block from the bottom of the panel
    current_bubble_top_y = panel_height - actual_block_height - style_config['caption_margin']

    for info in wrapped_captions_info:
        original_caption_data = info['original_caption']
        wrapped_lines = info['text_lines']
        text_height_from_wrap = info['text_height']

        if not wrapped_lines: # Skip if no lines to draw (e.g. empty caption)
            continue

        caption_type = original_caption_data.get("type", "dialogue")
        
        max_line_width = 0
        if wrapped_lines:
            for line in wrapped_lines:
                line_width = font.getlength(line)
                if line_width > max_line_width:
                    max_line_width = line_width
        
        bg_width = max_line_width + 2 * style_config['caption_padding']
        bg_height = text_height_from_wrap + 2 * style_config['caption_padding']

        bg_x0 = style_config['caption_margin']
        bg_y0 = current_bubble_top_y
        bg_x1 = bg_x0 + bg_width
        bg_y1 = bg_y0 + bg_height

        # Draw background
        current_border_color = style_config.get('border_color')
        current_border_width = style_config.get('border_width', 0)

        if caption_type == "dialogue":
            # print(f"DEBUG [caption_utils.draw_caption_bubbles]: Drawing DIALOGUE bubble. Outline: '{current_border_color}', Width: {current_border_width}") # DEBUG print
            draw.rounded_rectangle(
                (bg_x0, bg_y0, bg_x1, bg_y1),
                radius=style_config['caption_corner_radius'],
                fill=style_config['caption_background_color'],
                outline=current_border_color,
                width=current_border_width
            )
        elif caption_type == "narration":
            # print(f"DEBUG [caption_utils.draw_caption_bubbles]: Drawing NARRATOR bubble. Outline: '{current_border_color}', Width: {current_border_width}") # DEBUG print
            draw.rectangle( # Narrator boxes are typically rectangular
                (bg_x0, bg_y0, bg_x1, bg_y1),
                fill=style_config['caption_background_color'], # Use specific narrator background
                outline=current_border_color,
                width=current_border_width
            )
        elif caption_type == "sfx":
            # Give SFX a background for better visibility, using caption_background_color for now
            # print(f"DEBUG [caption_utils.draw_caption_bubbles]: Drawing SFX bubble. Outline: '{current_border_color}', Width: {current_border_width}") # DEBUG print
            draw.rounded_rectangle( # Or draw.rectangle if a different shape is preferred for SFX
                (bg_x0, bg_y0, bg_x1, bg_y1),
                radius=style_config['caption_corner_radius'], # Can be adjusted if SFX needs different styling
                fill=style_config['caption_background_color'], # Using dialogue background for now
                outline=current_border_color,
                width=current_border_width
            )
        elif caption_type == "caption": # Generic caption, give it a background too
            draw.rectangle(
                (bg_x0, bg_y0, bg_x1, bg_y1),
                fill=style_config['caption_background_color'],
                outline=current_border_color,
                width=current_border_width
            )
        # else:
            # For any other unhandled caption types, no background is drawn by default.
            # Consider adding a default background if all types should have one.
            # print(f"DEBUG: Caption type '{caption_type}' has no explicit background drawing rule.")


        font_to_use = font
        text_color_to_use = style_config['caption_text_color']
        
        
        # Draw text lines
        text_draw_x = bg_x0 + style_config['caption_padding']
        current_line_y_start_in_bubble = bg_y0 + style_config['caption_padding']

        for line_idx, line_text in enumerate(wrapped_lines):
            # Calculate y_position for this line's top
            # The 'lt' anchor means the (x,y) is the top-left of the text's bounding box.
            # Pillow's font.getbbox() includes space below baseline (descent) and above cap height (internal leading).
            # font.getmask(line).getbbox() might give tighter box for the glyphs themselves.
            # For simplicity, we'll position based on cumulative height of previous lines.
            
            y_pos_for_line_top = current_line_y_start_in_bubble
            if line_idx > 0:
                # Estimate height of previous line for spacing.
                # Using getbbox for previous line to get its rendered height.
                prev_line_bbox = font_to_use.getbbox(wrapped_lines[line_idx-1])
                prev_line_h = (prev_line_bbox[3] - prev_line_bbox[1]) if prev_line_bbox else font_to_use.size
                current_line_y_start_in_bubble += prev_line_h + style_config['line_spacing']
                y_pos_for_line_top = current_line_y_start_in_bubble
            
            # For precise top alignment of the first line with padding, adjust by ascent if needed,
            # but 'lt' anchor usually handles this well if y_pos_for_line_top is the desired top.
            # line_actual_bbox = font_to_use.getbbox(line_text)
            # y_draw_pos = y_pos_for_line_top - (line_actual_bbox[1] if line_actual_bbox else 0) # Adjust by y-offset of bbox
            
            draw.text((text_draw_x, y_pos_for_line_top),
                      line_text,
                      fill=text_color_to_use,
                      font=font_to_use,
                      anchor="lt" 
                     )
        
        # Advance current_bubble_top_y for the next bubble
        current_bubble_top_y += (bg_height + style_config['caption_margin'])
