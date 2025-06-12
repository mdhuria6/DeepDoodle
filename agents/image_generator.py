import os
import torch
from diffusers import StableDiffusionPipeline
from graph.state import ComicGenerationState

# Load model once (globally)
MODEL_ID = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_ID, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

def image_generator(state: ComicGenerationState) -> dict:
    """
    Node 4: Generates a panel image using Stable Diffusion (offline).
    """
    panel_index = state["current_panel_index"]
    prompt = state["panel_prompts"][panel_index]
    print(f"---AGENT: Image Generator (Panel {panel_index + 1})---")
    print(f"   > Generating image with prompt: {prompt[:100]}...")

    try:
        image = pipe(prompt).images[0]

        # Save image
        output_dir = "output/panels"
        os.makedirs(output_dir, exist_ok=True)
        image_path = os.path.join(output_dir, f"panel_{panel_index + 1}.png")
        image.save(image_path)
        print(f"   > Image saved to {image_path}")

    except Exception as e:
        print("❌ Error generating image with Stable Diffusion:", e)
        image_path = "output/placeholder.png"

    return {
        "panel_image_paths": state.get("panel_image_paths", []) + [image_path],
        "current_panel_index": panel_index + 1
    }
