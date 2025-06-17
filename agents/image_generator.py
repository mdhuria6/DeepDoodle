import os
from PIL import Image, ImageDraw
import json
import base64
import boto3
from botocore.exceptions import ClientError
import requests

from configs import (
    RAW_PANELS_DIR, USE_BEDROCK_IMAGE_GENERATION,
    BEDROCK_AWS_REGION, BEDROCK_IMAGE_MODEL_ID, HUGGINGFACE_API_TOKEN
)

from models.comic_generation_state import ComicGenerationState

import random

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
    img_w = max(1, target_w)
    img_h = max(1, target_h)
    img = Image.new('RGB', (img_w, img_h), color='white')
    img = _draw_grid(img, grid_spacing=50, line_color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0), (img_w-1, img_h-1)], outline="black", width=1)
    img.save(image_path)
    print(f"   > Saved placeholder image to: {image_path}")

def _generate_image_with_huggingface(
    prompt: str, 
    target_w: int, 
    target_h: int, 
    image_path: str,
    api_token: str
):
    """Generates an image using Hugging Face Inference API and saves it."""
    print(f"   > Attempting to generate COLORFUL image with Hugging Face API.")
    print(f'   > Prompt: "{prompt[:150]}..."')
    
    # Use a different model that's better for colorful illustrations
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    # Strong negative prompt to prevent text and ensure color
    negative_prompt = ("text, words, letters, speech bubbles, dialogue, captions, writing, typography, "
                      "signs, labels, watermarks, logos, comic text, manga text, speech balloons, "
                      "thought bubbles, black and white, monochrome, grayscale, panels within image, "
                      "comic page layout, multiple panels, grid layout")
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": target_w,
            "height": target_h,
            "num_inference_steps": 30,
            "guidance_scale": 9.0,
            "negative_prompt": negative_prompt
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            with open(image_path, "wb") as f:
                f.write(response.content)
            print(f"   > Successfully generated colorful image from Hugging Face to: {image_path}")
        else:
            print(f"Error from Hugging Face API: {response.status_code} - {response.text}")
            print("   > Falling back to placeholder image.")
            _generate_placeholder_image(target_w, target_h, image_path)

    except Exception as e:
        print(f"Error during Hugging Face image generation: {e}")
        print("   > Falling back to placeholder image.")
        _generate_placeholder_image(target_w, target_h, image_path)

def _generate_image_with_bedrock(
    prompt: str, 
    target_w: int, 
    target_h: int, 
    image_path: str, 
    model_id: str, 
    aws_region: str
):
    """Generates an image using AWS Bedrock and saves it."""
    print(f"   > Attempting to generate COLORFUL image with Bedrock. Model: {model_id}")
    print(f'   > Prompt: "{prompt[:150]}..."')
    
    bedrock = boto3.client(service_name='bedrock-runtime', region_name=aws_region)

    request_body = {}
    if "amazon.titan-image-generator-v1" in model_id:
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
                "negativeText": ("text, words, letters, speech bubbles, dialogue, captions, writing, "
                               "typography, signs, labels, watermarks, logos, comic text, manga text, "
                               "speech balloons, thought bubbles, black and white, monochrome, grayscale, "
                               "panels within image, comic page layout, multiple panels")
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "quality": "premium", 
                "height": target_h,
                "width": target_w,
                "cfgScale": 9.0, 
                "seed": None
            }
        }
    elif "stability.stable-diffusion" in model_id:
        request_body = {
            "text_prompts": [
                {"text": prompt, "weight": 1.0},
                {"text": ("text, words, letters, speech bubbles, dialogue, captions, writing, "
                         "typography, signs, labels, watermarks, logos, comic text, manga text, "
                         "speech balloons, thought bubbles, black and white, monochrome, grayscale, "
                         "panels within image, comic page layout, multiple panels, grid layout, "
                         "photorealistic, photography, 3D render"), "weight": -1.0}
            ],
            "cfg_scale": 12,
            "steps": 50,
            "seed": random.randint(0, 1000000),
        }
    else:
        raise ValueError(f"Unsupported Bedrock model ID: {model_id}")

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
        print(f"   > Successfully generated colorful image from Bedrock to: {image_path}")

    except Exception as e:
        print(f"Error during Bedrock image generation: {e}")
        print("   > Falling back to placeholder image.")
        _generate_placeholder_image(target_w, target_h, image_path)

def image_generator(state: ComicGenerationState) -> dict:
    """
    Generates a clean, colorful image for the current panel (NO TEXT OR SPEECH BUBBLES).
    """
    panel_index = state['current_panel_index']
    panel_layout_details = state['panel_layout_details']
    panel_prompts = state.get("panel_prompts", [])

    if not panel_prompts or panel_index >= len(panel_prompts):
        print(f"Error: No prompt found for panel {panel_index + 1}.")
        current_panel_prompt = "Colorful children's illustration, no text"
    else:
        current_panel_prompt = panel_prompts[panel_index]
    
    current_panel_layout = None
    for detail in panel_layout_details:
        if detail['panel_index'] == panel_index:
            current_panel_layout = detail
            break
    
    if not current_panel_layout:
        print(f"Warning: No layout details for panel {panel_index + 1}. Using 512x512.")
        target_w, target_h = 512, 512
    else:
        target_w = current_panel_layout['target_generation_width']
        target_h = current_panel_layout['target_generation_height']

    print(f"---AGENT: Image Generator (Panel {panel_index + 1}) - COLORFUL VISUAL ONLY---")
    print(f"   > Generating clean colorful image: {target_w}x{target_h}")

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
    elif HUGGINGFACE_API_TOKEN:
        _generate_image_with_huggingface(
            prompt=current_panel_prompt,
            target_w=target_w,
            target_h=target_h,
            image_path=image_path,
            api_token=HUGGINGFACE_API_TOKEN
        )
    else:
        print(f"   > No API tokens. Generating colorful placeholder ({target_w}x{target_h})...")
        _generate_placeholder_image(target_w, target_h, image_path)

    paths = state.get("panel_image_paths") or []
    return {
        "panel_image_paths": paths + [image_path], 
        "current_panel_index": panel_index + 1
    }
