import os
from PIL import Image
from models.comic_generation_state import ComicGenerationState # Updated import

def image_generator(state: ComicGenerationState) -> dict:
    """
    Node 4: Generates an image for the current panel based on the created prompt.
    This is a placeholder for an image generation model call.
    """
    panel_index = state['current_panel_index']
    print(f"---AGENT: Image Generator (Panel {panel_index + 1})---")

    # --- Image Generation API Placeholder ---
    # This is where you'd call a service like DALL-E 3, Imagen, or Stable Diffusion.
    # image_bytes = image_generation_api(prompt=state["panel_prompts"][-1])
    # image_path = f"output/panel_{panel_index + 1}.png"
    # with open(image_path, "wb") as f:
    #     f.write(image_bytes)
    # --- End Placeholder ---

    # Placeholder: Create a dummy image with PIL instead of calling a model
    print("   > Generating placeholder image...")
    img = Image.new('RGB', (512, 512), color='darkgray')

    # Ensure output directory exists
    output_dir = "output/panels"
    os.makedirs(output_dir, exist_ok=True)
    image_path = f"{output_dir}/panel_{panel_index + 1}.png"
    img.save(image_path)

    # Add the new image path to our list and increment the counter for the next loop
    paths = state.get("panel_image_paths") or []
    return {
        "panel_image_paths": paths + [image_path], 
        "current_panel_index": panel_index + 1
    }