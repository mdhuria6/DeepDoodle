import os
import io
from PIL import Image, ImageDraw
from typing import Optional

from configs import RAW_PANELS_DIR
from models.comic_generation_state import ComicGenerationState
from utils.llm_factory import get_model_client

def _draw_grid(image: Image.Image, grid_spacing: int = 50, line_color="gray"):
    """Draws a grid on the given PIL Image."""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    # Draw vertical lines
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=line_color)
    # Draw horizontal lines
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=line_color)
    return image

def _generate_placeholder_image(target_w: int, target_h: int, image_path: str):
    """Generates and saves a placeholder image with a grid."""
    # Ensure dimensions are at least 1x1 for Image.new
    img_w = max(1, target_w)
    img_h = max(1, target_h)
    img = Image.new('RGB', (img_w, img_h), color='white') # White background
    img = _draw_grid(img, grid_spacing=50, line_color=(200, 200, 200)) # Light gray grid
    # Optionally, draw a border to see exact image extents before sizing
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0), (img_w-1, img_h-1)], outline="black", width=1)
    img.save(image_path)
    print(f"   > Saved placeholder image to: {image_path}")

# --- Negative Prompt --- 
# A general-purpose negative prompt to discourage the model from generating unwanted elements.
NEGATIVE_PROMPT = (
    "nsfw, explicit, nudity, violence, gore, "
    "text, words, letters, characters, writing, signature, watermark, font, typography, "
    "speech bubble, dialogue bubble, caption, comic panel borders, "
    "low quality, blurry, bad anatomy, distorted, poorly drawn, artifacts, ugly, noise"
)

def image_generator(state: ComicGenerationState) -> dict:
    """
    Generates an image for the current panel using the model factory.
    """
    panel_index = state['current_panel_index']
    panel_layout_details = state['panel_layout_details']
    panel_prompts = state.get("panel_prompts", [])
    image_engine = state.get("image_engine", "flux.1-schnell") # Default to a HF model

    if not panel_prompts or panel_index >= len(panel_prompts):
        print(f"Error: No prompt found for panel {panel_index + 1}. Cannot generate image.")
        current_panel_prompt = "Error: Missing prompt"
    else:
        current_panel_prompt = panel_prompts[panel_index] # Get prompt for current panel
    
    current_panel_layout = next((d for d in panel_layout_details if d['panel_index'] == panel_index), None)
    
    if not current_panel_layout:
        print(f"Error: No layout details found for panel {panel_index + 1}. Using default 512x512.")
        target_w, target_h = 512, 512
    else:
        target_w = current_panel_layout['target_generation_width']
        target_h = current_panel_layout['target_generation_height']

    print(f"---AGENT: Image Generator (Panel {panel_index + 1})---")
    print(f"   > Engine: {image_engine}, Size: {target_w}x{target_h}")

    os.makedirs(RAW_PANELS_DIR, exist_ok=True)
    image_path = f"{RAW_PANELS_DIR}/panel_{panel_index + 1}.png"

    try:
        # Get the image generation client from the factory
        image_llm = get_model_client("image", image_engine)

        # Generate the image using the wrapper's method
        generated_image = image_llm.generate_image(
            prompt=current_panel_prompt,
            width=target_w,
            height=target_h,
            negative_prompt=NEGATIVE_PROMPT
        )
        
        generated_image.save(image_path)
        print(f"   > Successfully generated and saved image to: {image_path}")

    except Exception as e:
        print(f"Error during image generation with engine '{image_engine}': {e}")
        print("   > Falling back to placeholder image.")
        _generate_placeholder_image(target_w, target_h, image_path)

    paths = state.get("panel_image_paths") or []
    return {
        "panel_image_paths": paths + [image_path], 
        "current_panel_index": panel_index + 1
    }