import os
from PIL import Image
from typing import List, Dict, Tuple

from models.comic_generation_state import ComicGenerationState
from utils.config import RAW_PANELS_DIR, COMIC_PAGES_DIR, PANEL_OUTPUT_SIZE, PAGE_WIDTH, PAGE_HEIGHT, MARGIN

from utils.layout import crop_to_fit

def get_panel_dimensions(layout_style: str, num_panels_on_page: int, panel_index_on_page: int) -> tuple[int, int]:
    """
    Calculates the target width and height for a specific panel 
    based on the layout style and its index on the page.
    """
    if layout_style == "grid_2x2":
        # Assuming 4 panels for a 2x2 grid
        panel_w = (PAGE_WIDTH - 3 * MARGIN) / 2
        panel_h = (PAGE_HEIGHT - 3 * MARGIN) / 2
        return int(round(panel_w)), int(round(panel_h))
    
    elif layout_style == "horizontal_strip":
        # Horizontal strip always assumes 4 panels stacked vertically for its geometry.
        characteristic_num_panels = 4
        panel_w = PAGE_WIDTH - 2 * MARGIN
        panel_h = (PAGE_HEIGHT - (characteristic_num_panels + 1) * MARGIN) / characteristic_num_panels
        return int(round(panel_w)), int(round(panel_h))

    elif layout_style == "vertical_strip":
        # Vertical strip always assumes 3 panels arranged horizontally for its geometry.
        characteristic_num_panels = 3
        panel_w = (PAGE_WIDTH - (characteristic_num_panels + 1) * MARGIN) / characteristic_num_panels
        panel_h = PAGE_HEIGHT - 2 * MARGIN
        return int(round(panel_w)), int(round(panel_h))

    elif layout_style == "feature_left":
        # Panel 0 (Large feature panel on the left)
        if panel_index_on_page == 0:
            p1_w = int(round(PAGE_WIDTH * 0.6 - 1.5 * MARGIN))
            p1_h = PAGE_HEIGHT - 2 * MARGIN
            return p1_w, p1_h
        # Panels 1 & 2 (Right column)
        else:
            p1_w_calc = int(round(PAGE_WIDTH * 0.6 - 1.5 * MARGIN)) # Width of the left panel
            p_right_w = int(round(PAGE_WIDTH - p1_w_calc - 3 * MARGIN))
            p_right_h = int(round((PAGE_HEIGHT - 3 * MARGIN) / 2))
            return p_right_w, p_right_h
            
    elif layout_style == "mixed_2x2":
        panel_w = int(round((PAGE_WIDTH - 3 * MARGIN) / 2))
        available_h = PAGE_HEIGHT - 3 * MARGIN
        small_h = int(round(available_h / 3))
        large_h = available_h - small_h

        # Panel 0 (top-left, small_h), Panel 3 (bottom-right, small_h)
        if panel_index_on_page == 0 or panel_index_on_page == 3:
            return panel_w, small_h
        # Panel 1 (top-right, large_h), Panel 2 (bottom-left, large_h)
        else: # panel_index_on_page == 1 or panel_index_on_page == 2
            return panel_w, large_h
    else:
        print(f"Warning: Unknown layout style '{layout_style}' in panel_sizer_agent. Using default square panel.")
        # Fallback to a square panel, though this might not fit well
        default_size = int(round((PAGE_WIDTH - 3*MARGIN)/2)) # Arbitrary default
        return default_size, default_size


def panel_sizer(state: ComicGenerationState) -> dict: # Renamed from panel_sizer_agent
    print("---AGENT: Panel Sizer---")
    
    panel_image_paths = state.get("panel_image_paths", [])
    scenes = state.get("scenes", []) # Needed for captions later, pass through
    layout_style = state.get("layout_style", "grid_2x2") # Default if not provided

    if not panel_image_paths:
        print("Error: panel_image_paths not found in state for panel_sizer_agent.")
        return {"sized_panel_image_paths": [], "scenes": scenes, "layout_style": layout_style}

    output_dir_sized = "output/panels_sized"
    os.makedirs(output_dir_sized, exist_ok=True)
    
    sized_panel_image_paths = []
    
    # Determine panels per page based on layout style
    if layout_style == "grid_2x2":
        panels_per_page = 4
    elif layout_style == "horizontal_strip":
        panels_per_page = 4 # As per previous discussions
    elif layout_style == "vertical_strip":
        panels_per_page = 3 # As per previous discussions
    elif layout_style == "feature_left":
        panels_per_page = 3
    elif layout_style == "mixed_2x2":
        panels_per_page = 4
    else:
        print(f"Warning: Unknown layout_style '{layout_style}' for determining panels_per_page. Defaulting to 4.")
        panels_per_page = 4

    current_panel_idx = 0
    for i in range(0, len(panel_image_paths), panels_per_page):
        page_chunk_paths = panel_image_paths[i:i + panels_per_page]
        
        for panel_index_on_page, original_panel_path in enumerate(page_chunk_paths):
            try:
                target_w, target_h = get_panel_dimensions(layout_style, len(page_chunk_paths), panel_index_on_page)
                
                img = Image.open(original_panel_path)
                sized_img = crop_to_fit(img, target_w, target_h)
                
                base_name = os.path.basename(original_panel_path)
                name, ext = os.path.splitext(base_name)
                output_filename = f"{name}_sized{ext}"
                output_path_sized = os.path.join(output_dir_sized, output_filename)
                
                sized_img.save(output_path_sized)
                sized_panel_image_paths.append(output_path_sized)
                print(f"   > Sized panel {current_panel_idx + 1}: {original_panel_path} -> {output_path_sized} ({target_w}x{target_h})")
                
            except FileNotFoundError:
                print(f"Error: Original panel image not found at {original_panel_path}")
            except Exception as e:
                print(f"Error processing panel {original_panel_path} in panel_sizer_agent: {e}")
            current_panel_idx += 1
            
    return {
        "sized_panel_image_paths": sized_panel_image_paths,
        "scenes": scenes, # Pass through
        "layout_style": layout_style # Pass through
    }

