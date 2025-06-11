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

def wrap_text(text, font, max_width):
    """Wraps text to fit within max_width."""
    lines = []
    if not text:
        return lines
    
    words = text.split()
    current_line = words[0] if words else ""

    for word in words[1:]:
        # Check width with the new word
        if hasattr(font, "getbbox"): # TrueType
            bbox = font.getbbox(current_line + " " + word)
            width = bbox[2] - bbox[0]
        else: # Bitmap
            width = font.getlength(current_line + " " + word)
            
        if width <= max_width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def add_text_to_image(image_path: str, text: str, output_path: str):
    """
    Adds text to an image with wrapping and padding, simulating a speech bubble or caption.
    Saves the modified image to output_path.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        font_size = 16 # Reduced font size
        padding = 8   # Reduced padding
        bubble_margin = 8 # Reduced margin

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

        # --- Text Wrapping ---
        max_text_width = img.width - (2 * (padding + bubble_margin))
        wrapped_text = "\n".join(wrap_text(text, font, max_text_width))
        
        if not wrapped_text: # Handle empty caption case
            print(f"   > No text provided for caption on {os.path.basename(image_path)}. Saving original.")
            img.save(output_path)
            return

        # --- Calculate text and bubble dimensions ---
        # Use textbbox for more accurate dimensions with multiline text
        # The coordinates are (left, top, right, bottom)
        if hasattr(draw, "multiline_textbbox"): # Pillow 9.2.0+
            text_bbox = draw.multiline_textbbox((0,0), wrapped_text, font=font, spacing=4)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        else: # Fallback for older Pillow or if multiline_textbbox is not available
             # This is less accurate for multiline
            lines = wrapped_text.split('\n')
            text_height = 0
            text_width = 0
            line_spacing = 4 # Approximate
            for line_idx, line in enumerate(lines):
                if hasattr(font, "getbbox"):
                    line_bbox = font.getbbox(line)
                    text_width = max(text_width, line_bbox[2] - line_bbox[0])
                    text_height += (line_bbox[3] - line_bbox[1])
                else: # Bitmap font
                    text_width = max(text_width, font.getlength(line))
                    text_height += font_size # Approximate height
                if line_idx < len(lines) -1:
                    text_height += line_spacing


        bubble_width = text_width + (2 * padding)
        bubble_height = text_height + (2 * padding)

        # --- Position bubble at the bottom center ---
        bubble_x = (img.width - bubble_width) / 2
        bubble_y = img.height - bubble_height - bubble_margin

        # Ensure bubble doesn't go off-screen (e.g. if text is too wide even after wrapping)
        bubble_x = max(bubble_margin, bubble_x)
        if bubble_x + bubble_width > img.width - bubble_margin:
            bubble_width = img.width - (2*bubble_margin) # Shrink bubble to fit
            # Recalculate max_text_width based on new bubble_width if necessary, though wrap_text should handle it.
        
        # --- Draw bubble (rounded rectangle) and text ---
        # For a simple rectangle:
        rect_coords = [(bubble_x, bubble_y), (bubble_x + bubble_width, bubble_y + bubble_height)]
        # To draw with transparency, ensure image is RGBA or use a separate alpha mask
        # For simplicity, we'll draw an opaque rectangle. If you need transparency,
        # you might need to create a temporary RGBA image for the bubble.
        
        # Create a temporary drawing surface for the bubble if alpha is needed for bg_color
        if len(bg_color) == 4 and bg_color[3] < 255:
            bubble_surface = Image.new('RGBA', img.size, (0,0,0,0))
            bubble_draw = ImageDraw.Draw(bubble_surface)
            bubble_draw.rounded_rectangle(rect_coords, radius=10, fill=bg_color)
            img.paste(bubble_surface, (0,0), bubble_surface) # Paste with alpha
            # Redraw on the original image for text
            draw = ImageDraw.Draw(img) 
        else:
            draw.rounded_rectangle(rect_coords, radius=10, fill=bg_color)


        text_x = bubble_x + padding
        text_y = bubble_y + padding
        
        if hasattr(draw, "multiline_text"):
            draw.multiline_text((text_x, text_y), wrapped_text, font=font, fill=text_color, spacing=4)
        else: # Fallback for older Pillow
            lines = wrapped_text.split('\n')
            current_y = text_y
            for line in lines:
                draw.text((text_x, current_y), line, font=font, fill=text_color)
                if hasattr(font, "getbbox"):
                    line_bbox = font.getbbox(line)
                    current_y += (line_bbox[3] - line_bbox[1]) + 4 # 4 is spacing
                else:
                    current_y += font_size + 4


        img.save(output_path)
        print(f"   > Added caption to {os.path.basename(image_path)}, saved to {os.path.basename(output_path)}")

    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
    except Exception as e:
        print(f"Error adding text to image {image_path}: {e}")


def captioner(state: ComicGenerationState) -> dict: # Renamed from caption_agent
    """
    Node: Adds captions/speech bubbles to the generated panel images.
    Operates on each panel image individually. Expects pre-sized panel images.
    """
    print("---AGENT: Caption Agent---")
    panel_images_with_captions_paths = []
    # panel_images_with_captions objects are not strictly needed if paths are primary output
    # and page_composer will load from paths. Consider removing if not used downstream.

    scenes = state.get("scenes", [])
    # Expecting paths to already sized panels from panel_sizer_agent
    sized_panel_image_paths = state.get("sized_panel_image_paths", []) 
    layout_style = state.get("layout_style") # Pass through for page_composer

    if not sized_panel_image_paths:
        print("Error: sized_panel_image_paths not found in state for caption_agent. Cannot add captions.")
        return {
            "panel_images_with_captions_paths": [], 
            "scenes": scenes, 
            "layout_style": layout_style
        }

    if len(scenes) != len(sized_panel_image_paths):
        print(f"Warning: Mismatch between number of scenes ({len(scenes)}) and sized panel images ({len(sized_panel_image_paths)}).")
        min_len = min(len(scenes), len(sized_panel_image_paths))
        # scenes = scenes[:min_len] # Avoid modifying scenes if it's used by other branches
        # sized_panel_image_paths = sized_panel_image_paths[:min_len]
    else:
        min_len = len(scenes)

    output_dir_captions = "output/panels_with_captions"
    os.makedirs(output_dir_captions, exist_ok=True)

    for i in range(min_len):
        scene_data = scenes[i]
        sized_image_path = sized_panel_image_paths[i]
        caption_text = scene_data.get("caption", "")

        base, ext = os.path.splitext(os.path.basename(sized_image_path))
        # Ensure the output filename reflects it's based on a 'sized' image, then captioned
        # e.g., panel_1_sized_captioned.png
        output_filename = f"{base}_captioned{ext}" 
        output_image_path = os.path.join(output_dir_captions, output_filename)

        if not caption_text:
            print(f"   > No caption for panel {i+1} ({os.path.basename(sized_image_path)}). Saving original sized image to caption output dir.")
            try:
                img = Image.open(sized_image_path)
                img.save(output_image_path) # Save the sized image as the "captioned" one
                final_image_path = output_image_path
            except FileNotFoundError:
                print(f"Error: Sized image not found at {sized_image_path} when trying to skip captioning.")
                continue
            except Exception as e:
                print(f"Error saving uncaptioned sized image {sized_image_path}: {e}")
                continue
        else:
            try:
                add_text_to_image(sized_image_path, caption_text, output_image_path)
                final_image_path = output_image_path
            except Exception as e:
                print(f"Error adding caption to {sized_image_path}: {e}. Using original sized image.")
                # Fallback: copy the sized image to the output path if captioning fails
                try:
                    img = Image.open(sized_image_path)
                    img.save(output_image_path)
                    final_image_path = output_image_path
                except Exception as e_save:
                    print(f"Error saving fallback image for {sized_image_path}: {e_save}")
                    continue # Skip this panel if all fails
        
        panel_images_with_captions_paths.append(final_image_path)

    print(f"   > Captions processed. Output paths count: {len(panel_images_with_captions_paths)}")
    return {
        "panel_images_with_captions_paths": panel_images_with_captions_paths,
        "scenes": scenes, # Pass through scenes
        "layout_style": layout_style # Pass through layout_style
    }

