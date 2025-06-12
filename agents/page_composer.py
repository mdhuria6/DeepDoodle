from PIL import Image, ImageDraw
import os # Added missing import
from collections import defaultdict
from typing import List, Dict, Tuple

from configs import COMIC_PAGES_DIR, PAGE_WIDTH, PAGE_HEIGHT, MARGIN # Added MARGIN
from models.comic_generation_state import ComicGenerationState # PanelLayoutDetail will be imported from its own file
from models.panel_layout_detail import PanelLayoutDetail # Import from new file
from utils import layout_util # Changed from 'layout' to 'layout_util'

def page_composer(state: ComicGenerationState) -> dict:
    """Assembles sized and captioned panels into final pages based on pre-planned layouts."""
    print("---AGENT: Page Composer---")

    os.makedirs(COMIC_PAGES_DIR, exist_ok=True)
    
    # panel_images_with_captions_paths are the images ready to be placed
    panel_image_paths = state.get("panel_images_with_captions_paths", [])
    panel_layout_details = state.get("panel_layout_details", [])

    if not panel_image_paths:
        print("Error: No image paths found ('panel_images_with_captions_paths').")
        return {"final_page_images": [], "final_page_paths": []}
    
    if not panel_layout_details:
        print("Error: No panel layout details found.")
        return {"final_page_images": [], "final_page_paths": []}
    
    if len(panel_image_paths) != len(panel_layout_details):
        print("Error: Mismatch between number of panel images and layout details.")
        # Potentially return or handle error, e.g. try to compose with available info
        return {"final_page_images": [], "final_page_paths": []}

    # Group panel details and their corresponding image paths by page_number
    panels_by_page = defaultdict(list)
    for i, detail in enumerate(panel_layout_details):
        if i < len(panel_image_paths):
            panels_by_page[detail['page_number']].append(
                {'path': panel_image_paths[i], 'detail': detail}
            )
        else:
            print(f"Warning: More layout details than image paths. Detail for panel_index {detail['panel_index']} ignored.")

    final_pages_pil = [] # Store PIL Image objects
    final_page_paths = []

    for page_num in sorted(panels_by_page.keys()):
        page_panel_data = panels_by_page[page_num]
        
        if not page_panel_data:
            print(f"Warning: No panels found for page {page_num}. Skipping page.")
            continue

        # All panels on a page should have the same page_layout_type, determined by layout_planner
        # We can take it from the first panel on this page
        current_page_layout_type = page_panel_data[0]['detail']['page_layout_type']
        print(f"   > Composing Page {page_num} with layout: {current_page_layout_type}")

        page_image = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), color='white')

        # The core change: directly paste images using their pre-calculated ideal_x_offset and ideal_y_offset
        for panel_data in page_panel_data:
            panel_path = panel_data['path']
            detail = panel_data['detail']
            try:
                with Image.open(panel_path) as panel_img:
                    # panel_img should already be sized to ideal_width, ideal_height by panel_sizer
                    # We just need to paste it at the correct x, y offset
                    x_offset = detail['ideal_x_offset']
                    y_offset = detail['ideal_y_offset']
                    
                    # Sanity check image size against ideal dimensions (optional)
                    if panel_img.width != detail['ideal_width'] or panel_img.height != detail['ideal_height']:
                        print(f"Warning: Panel {detail['panel_index']} image size ({panel_img.width}x{panel_img.height}) "
                              f"does not match ideal size ({detail['ideal_width']}x{detail['ideal_height']}). Pasting as is.")
                        # Optionally, resize here again, but panel_sizer should have handled it.
                        # panel_img = panel_img.resize((detail['ideal_width'], detail['ideal_height']), Image.Resampling.LANCZOS)

                    page_image.paste(panel_img, (x_offset, y_offset))
            except FileNotFoundError:
                print(f"Error: Panel image not found at {panel_path} for page {page_num}.")
                # Create a black box as a placeholder for the missing panel
                error_panel_img = Image.new('RGB', (detail['ideal_width'], detail['ideal_height']), color='black')
                page_image.paste(error_panel_img, (detail['ideal_x_offset'], detail['ideal_y_offset']))
            except Exception as e:
                print(f"Error loading or pasting panel {panel_path}: {e}")
                error_panel_img = Image.new('RGB', (detail['ideal_width'], detail['ideal_height']), color='red') # Red box for other errors
                page_image.paste(error_panel_img, (detail['ideal_x_offset'], detail['ideal_y_offset']))

        final_pages_pil.append(page_image)
        page_output_path = os.path.join(COMIC_PAGES_DIR, f"page_{page_num}.png")
        page_image.save(page_output_path)
        final_page_paths.append(page_output_path)
        print(f"   > Saved composed page to: {page_output_path}")

    return {"final_page_images": final_pages_pil, "final_page_paths": final_page_paths}
