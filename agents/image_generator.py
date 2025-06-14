import os
from PIL import Image
import io
from typing import Optional
from huggingface_hub import InferenceClient

from models.comic_generation_state import ComicGenerationState

# Initialize the HF Inference client (token loaded from environment)
client = InferenceClient(token=os.getenv("HUGGINGFACE_API_TOKEN"))

def generate_image(prompt: str, width: int, height: int, style: Optional[str] = "manga", output_path: Optional[str] = None) -> str:
    """
    Generate an image from a text prompt using Hugging Face Inference API.

    Args:
        prompt (str): The text prompt describing the scene.
        width (int): Target image width.
        height (int): Target image height.
        style (str, optional): Artistic style to condition on. Defaults to "manga".
        output_path (str, optional): Where to save the image. If None, auto-generate.

    Returns:
        str: Path to the saved generated image file.
    """
    full_prompt = f"{prompt}, style: {style}"

    # Call text-to-image model inference
    response = client.text_to_image(full_prompt, width=width, height=height)

    # Handle possible response types
    if isinstance(response, Image.Image):
        img = response
    elif isinstance(response, bytes):
        img = Image.open(io.BytesIO(response))
    else:
        raise RuntimeError("Unexpected response type from Hugging Face Inference API.")

    if output_path is None:
        output_dir = "output/panels"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/generated_{hash(full_prompt) & 0xffffffff:x}.png"
    else:
        filename = output_path
    img.save(filename)
    return filename

def image_generator(state: ComicGenerationState) -> dict:
    """
    Generates an image for the current panel using Hugging Face InferenceClient.
    """
    panel_index = state['current_panel_index']
    panel_layout_details = state['panel_layout_details']
    panel_prompts = state.get("panel_prompts", [])
    style = state.get("style_preset", "manga")

    if not panel_prompts or panel_index >= len(panel_prompts):
        print(f"Error: No prompt found for panel {panel_index + 1}. Cannot generate image.")
        current_panel_prompt = "Error: Missing prompt"
    else:
        current_panel_prompt = panel_prompts[panel_index]

    current_panel_layout = None
    for detail in panel_layout_details:
        if detail['panel_index'] == panel_index:
            current_panel_layout = detail
            break

    if not current_panel_layout:
        print(f"Error: No layout details found for panel {panel_index + 1}. Using default 512x512 for image generation.")
        target_w, target_h = 512, 512
    else:
        target_w = current_panel_layout['target_generation_width']
        target_h = current_panel_layout['target_generation_height']

    print(f"---AGENT: Image Generator (Panel {panel_index + 1})---")
    output_dir = "output/panels"
    os.makedirs(output_dir, exist_ok=True)
    image_path = f"{output_dir}/panel_{panel_index + 1}.png"

    print(f"   > Generating image with HuggingFace InferenceClient ({target_w}x{target_h})...")
    generated_path = generate_image(current_panel_prompt, target_w, target_h, style, output_path=image_path)

    paths = state.get("panel_image_paths") or []
    return {
        "panel_image_paths": paths + [generated_path],
        "current_panel_index": panel_index + 1
    }