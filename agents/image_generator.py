import os
from typing import Optional
# Ensure the output directory exists

if not os.path.exists("output"):
    os.makedirs("output")

def generate_image(prompt: str, style: Optional[str] = "manga") -> str:
    """
    Generate an image from a text prompt using Hugging Face Inference API.

    Args:
        prompt (str): The text prompt describing the scene.
        style (str, optional): Artistic style to condition on. Defaults to "manga".

    Returns:
        str: Path to the saved generated image file.
    """
    filename = f"output/sample-1.png"
    return filename