import os
import io
from PIL import Image, ImageDraw
import json
import base64
import boto3
from botocore.exceptions import ClientError
from typing import Optional
from huggingface_hub import InferenceClient
from configs import (
    RAW_PANELS_DIR, USE_BEDROCK_IMAGE_GENERATION,
    BEDROCK_AWS_REGION, BEDROCK_IMAGE_MODEL_ID, OPENAI_API_KEY
)
from models.comic_generation_state import ComicGenerationState
import random

client = InferenceClient(token=os.getenv("HUGGINGFACE_API_TOKEN"))

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

def _generate_image_with_bedrock(
    prompt: str, 
    target_w: int, 
    target_h: int, 
    image_path: str, 
    model_id: str, 
    aws_region: str
):
    """Generates an image using AWS Bedrock and saves it."""
    print(f"   > Attempting to generate image with Bedrock. Model: {model_id}, Region: {aws_region}")
    print(f'   > Prompt: "{prompt[:100]}..."') # Print a truncated prompt for brevity
    
    bedrock = boto3.client(service_name='bedrock-runtime', region_name=aws_region)

    # Ensure target_w and target_h are within model limits if known,
    # or handle potential errors from the API.
    # For Titan, common sizes are 1024x1024, 512x512, etc.
    # The API might rescale or error if dimensions are not supported.
    # For this example, we pass them directly.

    request_body = {}
    if "amazon.titan-image-generator-v1" in model_id:
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
                "negativeText": "text, words, letters, characters, writing, signature, watermark, font, typography, low quality, blurry, bad anatomy, distorted, poorly drawn, artifacts"
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "standard", 
                "height": target_h,
                "width": target_w,
                "cfgScale": 7.5, 
                "seed": None # Use a specific seed for reproducibility if needed
            }
        }
    elif "stability.stable-diffusion" in model_id: # Example for Stable Diffusion
        request_body = {
            "cfg_scale": 8, # Increased from default (often 7) to encourage stricter prompt adherence
            "steps": 40,  # Slightly reduced from default (often 50) to potentially simplify
            "seed": random.randint(0, 1000000), # Keep seed random for now
            # Add other parameters like style_preset if supported and desired for this model
            # For Stable Diffusion, negative prompts are usually part of the main text_prompts array
            # with negative weights, or a separate parameter if the API supports it.
            # Bedrock's API for Stability atext_prompts with negative weight.
            # Let's add common negative prompts for quality and to avoid text, but not restrict style.
            "text_prompts": [
                {"text": prompt, "weight": 1.0},
                {"text": "text, words, letters, characters, writing, signature, watermark, font, typography, low quality, blurry, bad anatomy, distorted, poorly drawn, artifacts", "weight": -1.0}
            ],
        }
    else:
        raise ValueError(f"Unsupported Bedrock model ID structure for request body: {model_id}")

    body = json.dumps(request_body)

    try:
        response = bedrock.invoke_model(
            body=body, 
            modelId=model_id, 
            accept='application/json', 
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())

        base64_image_data = None
        if "amazon.titan-image-generator-v1" in model_id:
            base64_image_data = response_body.get('images')[0]
        elif "stability.stable-diffusion" in model_id:
            base64_image_data = response_body.get('artifacts')[0].get('base64')
        
        if not base64_image_data:
            raise ValueError("No image data found in Bedrock response.")

        image_bytes = base64.b64decode(base64_image_data)
        
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        print(f"   > Successfully generated and saved image from Bedrock to: {image_path}")

    except Exception as e:
        print(f"Error during Bedrock image generation: {e}")
        print("   > Falling back to placeholder image.")
        _generate_placeholder_image(target_w, target_h, image_path)


def image_generator(state: ComicGenerationState) -> dict:
    """
    Generates an image for the current panel using either AWS Bedrock or a placeholder.
    """
    panel_index = state['current_panel_index']
    panel_layout_details = state['panel_layout_details']
    panel_prompts = state.get("panel_prompts", [])
    style = state.get("style_preset", "manga")

    if not panel_prompts or panel_index >= len(panel_prompts):
        print(f"Error: No prompt found for panel {panel_index + 1}. Cannot generate image.")
        # Decide how to handle this: skip, error, or placeholder with no prompt?
        # For now, let's try to make a placeholder if layout details exist.
        current_panel_prompt = "Error: Missing prompt"
    else:
        current_panel_prompt = panel_prompts[panel_index] # Get prompt for current panel
    
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
    # Note: Target generation dimensions are now logged by the generation functions.

    output_dir = "output/panels"
    os.makedirs(output_dir, exist_ok=True)
    image_path = f"{output_dir}/panel_{panel_index + 1}.png"

    if USE_BEDROCK_IMAGE_GENERATION:
        _generate_image_with_bedrock(
            prompt=current_panel_prompt,
            target_w=target_w,
            target_h=target_h,
            image_path=image_path,
            model_id=BEDROCK_IMAGE_MODEL_ID,
            aws_region=BEDROCK_AWS_REGION
        )
    else:
        # print(f"   > Generating placeholder image with grid ({target_w}x{target_h})...")
        # _generate_placeholder_image(target_w, target_h, image_path)
        print(f"   > Generating image with HuggingFace InferenceClient ({target_w}x{target_h})...")
        generate_image(current_panel_prompt, target_w, target_h, style, output_path=image_path)

    paths = state.get("panel_image_paths") or []
    return {
        "panel_image_paths": paths + [image_path], 
        "current_panel_index": panel_index + 1
    }

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