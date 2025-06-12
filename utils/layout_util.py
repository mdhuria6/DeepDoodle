from PIL import Image, ImageOps
from configs import PAGE_WIDTH, PAGE_HEIGHT, MARGIN

# --- Helper Function for Aspect-Aware Cropping (used by panel_sizer_agent) ---
def crop_to_fit(image: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Scales and center-crops an image to fit target dimensions without distortion.
    This is also known as "Aspect Fill".
    """
    # Ensure target dimensions are integers
    target_width = int(round(target_width))
    target_height = int(round(target_height))
    if target_width <= 0 or target_height <= 0:
        # Fallback for invalid dimensions: return a small black square or raise error
        print(f"Warning: crop_to_fit called with invalid dimensions: w={target_width}, h={target_height}. Returning original image.")
        return image # Or raise ValueError("Target dimensions must be positive")
    return ImageOps.fit(image, (target_width, target_height), method=Image.Resampling.LANCZOS)

# --- Composition functions (expect pre-sized, pre-captioned panel images) ---
def compose_grid_2x2(page: Image.Image, page_chunk_paths: list[str]) -> Image.Image:
    # These dimensions are for placing the pre-sized panels
    panel_slot_w = (PAGE_WIDTH - 3 * MARGIN) / 2
    panel_slot_h = (PAGE_HEIGHT - 3 * MARGIN) / 2

    for j, panel_path in enumerate(page_chunk_paths):
        with Image.open(panel_path) as panel_img: # panel_img is already correctly sized and captioned
            row, col = j // 2, j % 2
            x = MARGIN + (col * (panel_slot_w + MARGIN))
            y = MARGIN + (row * (panel_slot_h + MARGIN))
            page.paste(panel_img, (int(round(x)), int(round(y))))
    return page

def compose_horizontal_strip(page: Image.Image, page_chunk_paths: list[str]) -> Image.Image:
    # 4 panels, stacked vertically. These dimensions are for placing.
    # The actual width of the panel image is already PAGE_WIDTH - 2 * MARGIN
    # The actual height of the panel image is already (PAGE_HEIGHT - (len(page_chunk_paths) + 1) * MARGIN) / len(page_chunk_paths)
    
    # We need the height of the slot for correct y_offset calculation
    num_panels_on_page = len(page_chunk_paths)
    panel_slot_h = (PAGE_HEIGHT - (num_panels_on_page + 1) * MARGIN) / num_panels_on_page

    for j, panel_path in enumerate(page_chunk_paths):
        with Image.open(panel_path) as panel_img: # panel_img is already correctly sized and captioned
            x_offset = MARGIN
            y_offset = MARGIN + (j * (panel_slot_h + MARGIN))
            page.paste(panel_img, (int(round(x_offset)), int(round(y_offset))))
    return page

def compose_vertical_strip(page: Image.Image, page_chunk_paths: list[str]) -> Image.Image:
    # 3 panels, arranged horizontally. These dimensions are for placing.
    # The actual height of the panel image is already PAGE_HEIGHT - 2 * MARGIN
    # The actual width of the panel image is already (PAGE_WIDTH - (len(page_chunk_paths) + 1) * MARGIN) / len(page_chunk_paths)

    # We need the width of the slot for correct x_offset calculation
    num_panels_on_page = len(page_chunk_paths)
    panel_slot_w = (PAGE_WIDTH - (num_panels_on_page + 1) * MARGIN) / num_panels_on_page

    for j, panel_path in enumerate(page_chunk_paths):
        with Image.open(panel_path) as panel_img: # panel_img is already correctly sized and captioned
            x_offset = MARGIN + (j * (panel_slot_w + MARGIN))
            y_offset = MARGIN
            page.paste(panel_img, (int(round(x_offset)), int(round(y_offset))))
    return page

def compose_feature_left(page: Image.Image, page_chunk_paths: list[str]) -> Image.Image:
    # Slot dimensions for placement calculations
    slot_p1_w = int(round(PAGE_WIDTH * 0.6 - 1.5 * MARGIN))
    # slot_p1_h = PAGE_HEIGHT - 2 * MARGIN # Height of image is already this
    
    slot_p_right_h = int(round((PAGE_HEIGHT - 3 * MARGIN) / 2))

    # Panel 1 (Large feature panel on the left)
    with Image.open(page_chunk_paths[0]) as p1_img: # Already sized and captioned
        page.paste(p1_img, (MARGIN, MARGIN))

    # Panel 2 (Top right)
    with Image.open(page_chunk_paths[1]) as p2_img: # Already sized and captioned
        page.paste(p2_img, (MARGIN + slot_p1_w + MARGIN, MARGIN))

    # Panel 3 (Bottom right)
    with Image.open(page_chunk_paths[2]) as p3_img: # Already sized and captioned
        page.paste(p3_img, (MARGIN + slot_p1_w + MARGIN, MARGIN + slot_p_right_h + MARGIN))
    return page

def compose_mixed_2x2(page: Image.Image, page_chunk_paths: list[str]) -> Image.Image:
    # Slot dimensions for placement calculations
    panel_slot_w = int(round((PAGE_WIDTH - 3 * MARGIN) / 2))
    available_h = PAGE_HEIGHT - 3 * MARGIN
    slot_small_h = int(round(available_h / 3))
    slot_large_h = available_h - slot_small_h # Define slot_large_h here

    if len(page_chunk_paths) != 4:
        print(f"Warning: compose_mixed_2x2 expects 4 panel paths, got {len(page_chunk_paths)}. Skipping page composition for this chunk.")
        return page

    with Image.open(page_chunk_paths[0]) as p1_img, \
         Image.open(page_chunk_paths[1]) as p2_img, \
         Image.open(page_chunk_paths[2]) as p3_img, \
         Image.open(page_chunk_paths[3]) as p4_img:
        
        # Panel 1 (top-left)
        page.paste(p1_img, (MARGIN, MARGIN)) # p1_img is already sized to panel_slot_w, slot_small_h
        
        # Panel 3 (bottom-left) - Assuming p3 is page_chunk_paths[2]
        page.paste(p3_img, (MARGIN, MARGIN + slot_small_h + MARGIN)) # p3_img is already sized to panel_slot_w, slot_large_h
        
        # Panel 2 (top-right) - Assuming p2 is page_chunk_paths[1]
        page.paste(p2_img, (MARGIN + panel_slot_w + MARGIN, MARGIN)) # p2_img is already sized to panel_slot_w, slot_large_h
        
        # Panel 4 (bottom-right) - Assuming p4 is page_chunk_paths[3]
        # Corrected y-coordinate to be below the large panel (p2_img)
        page.paste(p4_img, (MARGIN + panel_slot_w + MARGIN, MARGIN + slot_large_h + MARGIN)) # p4_img is already sized to panel_slot_w, slot_small_h
    return page
