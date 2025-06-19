from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Dict, Tuple, Optional

from models.caption import Caption
from models.caption_style_metadata import CaptionStyleMetadata

from utils import draw_caption_bubbles
 
from models.comic_generation_state import ComicGenerationState
from utils import caption_util 
from configs import (
    CAPTIONED_PANELS_DIR, SIZED_PANELS_DIR, BUNDLED_FONT_PATH,
    CAPTION_BACKGROUND_COLOR, CAPTION_TEXT_COLOR, CAPTION_PADDING,
    CAPTION_MARGIN, MAX_CAPTION_HEIGHT_RATIO, MAX_FONT_SIZE, # Added MAX_FONT_SIZE
    DEFAULT_FONT_SIZE, MIN_FONT_SIZE,
    LINE_SPACING, NARRATOR_BACKGROUND_COLOR, CAPTION_CORNER_RADIUS,
    SFX_TEXT_COLOR, SFX_FONT_PATH # Assuming these might be in global config
)


def add_texts_to_image(
    image_path: str,
    captions_data: List[Caption], # Use the Caption TypedDict from models
    panel_width: int,
    panel_height: int,
    panel_idx_for_logging: int = -1
) -> Image.Image:
    """
    Adds formatted text captions to an image using utility functions.
    Returns a PIL Image object with captions drawn.
    """
    # 1. Create CaptionStyleMetadata from global config constants
    style_config = CaptionStyleMetadata(
        font_path=BUNDLED_FONT_PATH,
        max_font_size=MAX_FONT_SIZE,
        min_font_size=MIN_FONT_SIZE,
        default_font_size=DEFAULT_FONT_SIZE,
        line_spacing=LINE_SPACING,
        caption_margin=CAPTION_MARGIN,
        caption_padding=CAPTION_PADDING,
        max_caption_height_ratio=MAX_CAPTION_HEIGHT_RATIO,
        caption_background_color=CAPTION_BACKGROUND_COLOR,
        narrator_background_color=NARRATOR_BACKGROUND_COLOR,
        caption_text_color=CAPTION_TEXT_COLOR,
        caption_corner_radius=CAPTION_CORNER_RADIUS,
        sfx_text_color=SFX_TEXT_COLOR, 
        sfx_font_path=SFX_FONT_PATH,
        border_color="black",
        border_width=1  # Changed from 3 back to 1
    )

    # 2. Load image (or error fallback)
    img, draw, is_error_image = caption_util.load_panel_image(
        image_path, panel_width, panel_height, style_config
    )

    if is_error_image or not captions_data:
        return img # Return error image or original if no captions

    # 3. Determine font and layout
    text_area_width = panel_width - 2 * style_config['caption_margin'] - 2 * style_config['caption_padding']
    max_block_height_px = int(panel_height * style_config['max_caption_height_ratio'])

    final_font, all_wrapped_captions_info = caption_util.determine_font_and_layout(
        captions_data,
        text_area_width,
        max_block_height_px,
        style_config,
        panel_idx_for_logging
    )

    if not final_font or not all_wrapped_captions_info:
        print(f"Warning: Panel {panel_idx_for_logging+1}: Could not determine font or layout. Returning image as is.")
        return img 

    # 4. Draw captions onto the image
    draw_caption_bubbles(
        draw,
        final_font,
        all_wrapped_captions_info,
        panel_height,
        style_config
    )

    return img


def captioner(state: ComicGenerationState) -> dict:
    """Node 6: Adds captions to each sized panel image."""
    print(f"---AGENT: Captioner---")

    sized_panel_paths = state.get("sized_panel_image_paths", [])
    scenes_data = state.get("scenes", []) 
    layout_style = state.get("layout_style", "grid_2x2")

    if not sized_panel_paths:
        print("Error: No sized panel paths found in state for captioner.")
        return {"panel_images_with_captions_paths": [], "scenes": scenes_data, "layout_style": layout_style}

    os.makedirs(CAPTIONED_PANELS_DIR, exist_ok=True)
    
    panel_images_with_captions_paths = []

    for idx, sized_panel_path in enumerate(sized_panel_paths):
        if idx >= len(scenes_data):
            print(f"Skipping captioning for panel {idx+1} as no corresponding scene data found.")
            continue

        panel_captions: List[Caption] = scenes_data[idx].get('captions', [])
        
        try:
            with Image.open(sized_panel_path) as temp_img:
                panel_width, panel_height = temp_img.size
        except FileNotFoundError:
            print(f"Error: Sized panel image not found at {sized_panel_path}. Skipping for panel {idx+1}.")
            continue
        except Exception as e:
            print(f"Error opening sized panel image {sized_panel_path}: {e}. Skipping for panel {idx+1}.")
            continue

        print(f"   > Adding captions to panel {idx + 1} (Image: {os.path.basename(sized_panel_path)}), Captions: {len(panel_captions)}")
        
        captioned_image = add_texts_to_image(
            sized_panel_path,
            panel_captions, 
            panel_width,
            panel_height,
            panel_idx_for_logging=idx
        )

        base_name = os.path.basename(sized_panel_path)
        name, _ = os.path.splitext(base_name)
        output_filename = f"{name}_captioned.png"
        output_path_captioned = os.path.join(CAPTIONED_PANELS_DIR, output_filename)
        
        try:
            captioned_image.save(output_path_captioned, "PNG")
            panel_images_with_captions_paths.append(output_path_captioned)
            print(f"     > Saved captioned panel to: {output_path_captioned}")
        except Exception as e:
            print(f"Error saving captioned image {output_path_captioned}: {e}")

    print("cdfdvdfv",{
        "panel_images_with_captions_paths": panel_images_with_captions_paths,
        "scenes": scenes_data,
        "layout_style": layout_style
    })
    return {
        "panel_images_with_captions_paths": panel_images_with_captions_paths,
        "scenes": scenes_data,
        "layout_style": layout_style
    }

