import os
from PIL import Image, ImageDraw # Added ImageDraw
from models.comic_generation_state import ComicGenerationState

def draw_grid(image: Image.Image, grid_spacing: int = 50, line_color="gray"):
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

def image_generator(state: ComicGenerationState) -> dict:
    """
    Generates a placeholder image with a grid pattern for the current panel 
    using target dimensions from layout_planner.
    """
    panel_index = state['current_panel_index']
    panel_layout_details = state['panel_layout_details']
    
    # Find the layout detail for the current panel
    current_panel_layout = None
    for detail in panel_layout_details:
        if detail['panel_index'] == panel_index:
            current_panel_layout = detail
            break
    
    if not current_panel_layout:
        # This should not happen if layout_planner ran correctly
        print(f"Error: No layout details found for panel {panel_index}. Using default 512x512.")
        target_w, target_h = 512, 512
    else:
        target_w = current_panel_layout['target_generation_width']
        target_h = current_panel_layout['target_generation_height']

    print(f"---AGENT: Image Generator (Panel {panel_index + 1})---")
    print(f"   > Target generation dimensions for placeholder: {target_w}x{target_h}")

    # Ensure output directory exists
    output_dir = "output/panels"
    os.makedirs(output_dir, exist_ok=True)
    # Define the final output path for the panel image
    image_path = f"{output_dir}/panel_{panel_index + 1}.png"

    # --- Generate placeholder image with a grid ---
    print(f"   > Generating placeholder image with grid ({target_w}x{target_h})...")
    # Ensure dimensions are at least 1x1 for Image.new
    img_w = max(1, target_w)
    img_h = max(1, target_h)
    img = Image.new('RGB', (img_w, img_h), color='white') # White background
    img = draw_grid(img, grid_spacing=50, line_color=(200, 200, 200)) # Light gray grid
    # Optionally, draw a border to see exact image extents before sizing
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0), (img_w-1, img_h-1)], outline="black", width=1)
    img.save(image_path)
    # --- End placeholder generation ---

    # --- Image Generation API Placeholder (Commented out) ---
    # This is where you'd call a service like DALL-E 3, Imagen, or Stable Diffusion.
    # image_bytes = image_generation_api(prompt=state["panel_prompts"][-1])
    # with open(image_path, "wb") as f:
    #     f.write(image_bytes)
    # --- End Placeholder ---

    # Add the new image path to our list and increment the counter for the next loop
    paths = state.get("panel_image_paths") or []
    return {
        "panel_image_paths": paths + [image_path], 
        "current_panel_index": panel_index + 1
    }