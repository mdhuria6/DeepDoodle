import os # Added for makedirs
from PIL import Image
from graph.state import ComicGenerationState
from utils.config import COMIC_PAGES_DIR, PAGE_WIDTH, PAGE_HEIGHT # Import new page dimensions and use COMIC_PAGES_DIR
from utils import layout

def page_composer(state: ComicGenerationState) -> dict:
    """Assembles generated panels into final pages using a specified layout."""
    print("---AGENT: Page Composer---")

    # Ensure output directory for pages exists
    os.makedirs(COMIC_PAGES_DIR, exist_ok=True) # Use COMIC_PAGES_DIR
    
    layout_style = state.get("layout_style") or "grid_2x2"
    # Expects paths to images that are already sized and captioned
    image_paths_to_compose = state.get("panel_images_with_captions_paths", [])

    if not image_paths_to_compose:
        print("Error: No image paths found to compose. Check 'panel_images_with_captions_paths' in state.")
        return {"final_page_images": [], "final_page_paths": []}

    # Define panels per page based on layout style
    if layout_style == "feature_left":
        panels_per_page = 3
    elif layout_style == "vertical_strip":
        panels_per_page = 3 # As per new requirement
    elif layout_style == "horizontal_strip":
        panels_per_page = 4 # As per new requirement
    elif layout_style in ["grid_2x2", "mixed_2x2"]:
        panels_per_page = 4
    else: # Default or unknown layout
        panels_per_page = 4 
        print(f"Warning: Unknown layout_style '{layout_style}', defaulting to 4 panels per page.")

    # Ensure total panel count from state is used if it's a strip layout that should fill one page
    # This logic might need refinement if strips can span multiple pages with fixed panels_per_page
    # For now, assuming strip layouts try to fit all panels from state['panel_count'] onto one page,
    # but capped by the new fixed panels_per_page for horizontal/vertical.
    # If state['panel_count'] is less than panels_per_page, it will be handled by page_chunk logic.

    page_chunks = [image_paths_to_compose[i:i + panels_per_page] for i in range(0, len(image_paths_to_compose), panels_per_page)]
    
    final_pages = []
    final_page_paths = []

    for i, page_chunk in enumerate(page_chunks):
        # Validate if enough panels for the chosen layout on this page
        if layout_style == "feature_left" and len(page_chunk) < 3:
            print(f"Skipping page {i+1} for feature_left: needs 3 panels, got {len(page_chunk)}")
            continue
        if layout_style == "vertical_strip" and len(page_chunk) < 3:
            print(f"Skipping page {i+1} for vertical_strip: needs 3 panels, got {len(page_chunk)}")
            continue
        if layout_style == "horizontal_strip" and len(page_chunk) < 4:
            # Allow fewer if it's the last page and not enough panels left
            if i < len(page_chunks) -1 : # Not the last page
                 print(f"Skipping page {i+1} for horizontal_strip: needs 4 panels, got {len(page_chunk)}")
                 continue
            elif len(page_chunk) == 0: # Empty chunk
                continue

        if layout_style in ["grid_2x2", "mixed_2x2"] and len(page_chunk) < 4:
            # Allow fewer if it's the last page and not enough panels left
            if i < len(page_chunks) -1: # Not the last page
                print(f"Skipping page {i+1} for {layout_style}: needs 4 panels, got {len(page_chunk)}")
                continue
            elif len(page_chunk) == 0: # Empty chunk
                continue
        
        # Create a new page with fixed dimensions
        page = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), color='white')

        # Call the appropriate layout composition function
        if layout_style == "grid_2x2":
            page = layout.compose_grid_2x2(page, page_chunk)
        elif layout_style == "horizontal_strip":
            page = layout.compose_horizontal_strip(page, page_chunk)
        elif layout_style == "vertical_strip":
            page = layout.compose_vertical_strip(page, page_chunk)
        elif layout_style == "feature_left":
            page = layout.compose_feature_left(page, page_chunk)
        elif layout_style == "mixed_2x2":
            page = layout.compose_mixed_2x2(page, page_chunk)
        else:
            print(f"Warning: Layout style '{layout_style}' not implemented. Creating blank page.")
            # Fallback: paste panels if any, or leave page blank
            if page_chunk:
                 page = layout.compose_grid_2x2(page, page_chunk) # Default to grid if unknown

        final_pages.append(page)
        page_path = f"{COMIC_PAGES_DIR}/page_{i + 1}.png" # Use COMIC_PAGES_DIR
        page.save(page_path)
        final_page_paths.append(page_path)
        print(f"   > Saved composed page to: {page_path}")

    return {"final_page_images": final_pages, "final_page_paths": final_page_paths}
