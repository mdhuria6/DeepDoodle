from PIL import Image, ImageDraw, ImageFont
import os
from graph.state import ComicGenerationState
from utils.config import BUNDLED_FONT_PATH # Import from config

try:
    # Test if the bundled font can be loaded
    ImageFont.truetype(BUNDLED_FONT_PATH, 15)
    FONT_PATH = BUNDLED_FONT_PATH
    print(f"Successfully loaded bundled font: {FONT_PATH}")
except IOError:
    print(f"Warning: Bundled font at {BUNDLED_FONT_PATH} not found or is invalid. Falling back to PIL default.")
    FONT_PATH = None # Use PIL default

def wrap_text(text: str, font, max_width: int) -> list[str]:
    """
    Wraps text to fit within max_width.
    Handles pre-existing newlines and uses font.getbbox() for more accurate width calculation.
    """
    final_lines = []
    if not text:
        return final_lines

    # Adjust max_width slightly to create a small buffer for rendering discrepancies
    # This can help prevent text from being cut off if measurement is slightly off.
    effective_max_width = max_width * 0.95 # Use 95% of available width as a buffer

    # Split the input text by pre-existing newlines first
    initial_segments = text.split('\\n')

    for segment in initial_segments:
        if not segment.strip(): # If segment is empty or just whitespace after split
            final_lines.append("") # Preserve the newline as an empty line
            continue

        words = segment.split()
        if not words:
            final_lines.append("") # Preserve the newline if segment had only spaces
            continue

        current_line = words[0]
        for word in words[1:]:
            # Check width with the new word
            try:
                # For TrueType fonts, getbbox is preferred
                bbox = font.getbbox(current_line + " " + word)
                width = bbox[2] - bbox[0] # (right - left) gives width
            except AttributeError:
                # Fallback for basic/bitmap fonts if getbbox is not available
                # This might be less accurate
                width = font.getlength(current_line + " " + word)
            
            if width <= effective_max_width:
                current_line += " " + word
            else:
                final_lines.append(current_line)
                current_line = word
        final_lines.append(current_line) # Add the last line of the current segment
    
    return final_lines

def add_texts_to_image(image_path: str, texts: list[str], output_path: str):
    """
    Adds a list of texts to an image, stacked vertically at the bottom,
    each with wrapping and padding, simulating speech bubbles or captions.
    Saves the modified image to output_path.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        font_size = 12
        padding = 8 # Reduced padding for potentially multiple bubbles
        bubble_margin = 5 # Margin around each bubble
        inter_bubble_spacing = 5 # Spacing between bubbles

        try:
            if FONT_PATH:
                font = ImageFont.truetype(FONT_PATH, font_size)
            else:
                font = ImageFont.load_default()
        except IOError:
            print(f"Warning: Could not load font {FONT_PATH}. Using PIL default.")
            font = ImageFont.load_default()

        text_color = (0, 0, 0) # Black
        bg_color = (255, 255, 255, 200) # White with some transparency

        if not texts or all(not text for text in texts):
            print(f"   > No text provided for captions on {os.path.basename(image_path)}. Saving original.")
            img.save(output_path)
            return

        total_bubbles_height = 0
        bubble_details = []

        # First pass: Calculate dimensions for all text bubbles
        for text in texts:
            if not text: # Skip empty strings in the list
                bubble_details.append(None)
                continue

            max_text_width = img.width - (2 * (padding + bubble_margin))
            wrapped_text_lines = wrap_text(text, font, max_text_width)
            wrapped_text = "\n".join(wrapped_text_lines) # Corrected: Use actual newline character
            
            if not wrapped_text:
                bubble_details.append(None)
                continue

            if hasattr(draw, "multiline_textbbox"):
                text_bbox = draw.multiline_textbbox((0,0), wrapped_text, font=font, spacing=4)
                current_text_width = text_bbox[2] - text_bbox[0]
                current_text_height = text_bbox[3] - text_bbox[1]
            else:
                # Fallback for older Pillow (less accurate for multiline)
                lines = wrapped_text.split('\\n')
                current_text_height = 0
                current_text_width = 0
                line_spacing = 4
                for line_idx, line in enumerate(lines):
                    if hasattr(font, "getbbox"):
                        line_bbox = font.getbbox(line)
                        current_text_width = max(current_text_width, line_bbox[2] - line_bbox[0])
                        current_text_height += (line_bbox[3] - line_bbox[1])
                    else: # Bitmap font
                        current_text_width = max(current_text_width, font.getlength(line))
                        current_text_height += font_size
                    if line_idx < len(lines) -1:
                        current_text_height += line_spacing
            
            current_bubble_width = current_text_width + (2 * padding)
            current_bubble_height = current_text_height + (2 * padding)
            
            bubble_details.append({
                "wrapped_text": wrapped_text,
                "text_width": current_text_width,
                "text_height": current_text_height,
                "bubble_width": current_bubble_width,
                "bubble_height": current_bubble_height
            })
            total_bubbles_height += current_bubble_height
        
        total_bubbles_height += max(0, (len([bd for bd in bubble_details if bd is not None]) - 1)) * inter_bubble_spacing

        # Second pass: Draw bubbles from bottom up
        current_y_offset = img.height - bubble_margin # Start from the bottom of the image

        for detail in reversed(bubble_details): # Iterate from last caption to first for bottom-up placement
            if detail is None:
                continue

            # Position for the current bubble (bottom-center aligned for the stack)
            bubble_x = (img.width - detail["bubble_width"]) / 2
            bubble_y = current_y_offset - detail["bubble_height"]

            # Draw bubble background
            draw.rounded_rectangle(
                (bubble_x, bubble_y, bubble_x + detail["bubble_width"], bubble_y + detail["bubble_height"]),
                radius=5, fill=bg_color
            )

            # Position for text inside the bubble
            text_x = bubble_x + padding
            text_y = bubble_y + padding
            
            # Draw text
            if hasattr(draw, "multiline_text"):
                 draw.multiline_text((text_x, text_y), detail["wrapped_text"], fill=text_color, font=font, spacing=4)
            else: # Fallback for older Pillow
                lines = detail["wrapped_text"].split('\n') # Corrected: Split by actual newline character
                current_line_y = text_y
                for line in lines:
                    draw.text((text_x, current_line_y), line, fill=text_color, font=font)
                    # Approximate line height for advancing
                    if hasattr(font, "getbbox"):
                        line_bbox = font.getbbox(line)
                        current_line_y += (line_bbox[3] - line_bbox[1]) + 4 # 4 is spacing
                    else:
                        current_line_y += font_size + 4


            current_y_offset = bubble_y - inter_bubble_spacing # Move up for the next bubble

        img.save(output_path)
        print(f"   > Image with {len([bd for bd in bubble_details if bd is not None])} captions saved to: {os.path.basename(output_path)}")

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
    except Exception as e:
        print(f"Error adding text to image {image_path}: {e}")


def captioner(state: ComicGenerationState) -> dict: # Renamed from caption_agent
    """
    Node: Adds captions/speech bubbles to the generated panel images.
    Operates on each panel image individually. Expects pre-sized panel images.
    """
    print("---AGENT: Captioner---")
    
    # Expects paths to images that are already sized
    sized_panel_image_paths = state.get("sized_panel_image_paths", [])
    scenes = state.get("scenes", [])
    
    if not sized_panel_image_paths:
        print("   > No sized panel images found. Skipping captioning.")
        return {"panel_images_with_captions_paths": []}

    # Ensure output directory for captioned panels exists
    # output_dir_captioned = "output/panels_with_captions" # Old way
    output_dir_captioned = state.get("output_dirs", {}).get("CAPTIONED_PANELS_DIR")
    if not output_dir_captioned:
        # Fallback if not in state (should be set by config loading)
        from utils.config import CAPTIONED_PANELS_DIR as DEFAULT_CAPTIONED_DIR
        output_dir_captioned = DEFAULT_CAPTIONED_DIR
        print(f"   > Warning: CAPTIONED_PANELS_DIR not found in state, using default: {output_dir_captioned}")
    
    os.makedirs(output_dir_captioned, exist_ok=True)
    
    captioned_image_paths = []

    for i, image_path in enumerate(sized_panel_image_paths):
        if i < len(scenes):
            scene_captions = scenes[i].get("captions", []) # Get list of captions
            if not isinstance(scene_captions, list): # Ensure it's a list
                print(f"   > Warning: Captions for panel {i+1} is not a list: {scene_captions}. Treating as single caption.")
                scene_captions = [str(scene_captions)] if scene_captions else []
        else:
            print(f"   > Warning: No scene data found for panel {i+1}. No caption will be added.")
            scene_captions = []

        base, ext = os.path.splitext(os.path.basename(image_path))
        output_filename = f"{base}_captioned{ext}"
        output_path = os.path.join(output_dir_captioned, output_filename)
        
        # Call the new function that handles a list of texts
        add_texts_to_image(image_path, scene_captions, output_path)
        captioned_image_paths.append(output_path)

    return {"panel_images_with_captions_paths": captioned_image_paths}

