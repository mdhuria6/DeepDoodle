from PIL import Image
from graph.state import ComicGenerationState
from utils.config import PAGES_DIR
from utils import layout

def page_composer(state: ComicGenerationState) -> dict:
    """Assembles generated panels into final pages using a specified layout."""
    print("---AGENT: Page Composer---")
    
    layout_style = state.get("layout_style") or "grid_2x2"
    panels_per_page = 4
    if layout_style == "feature_left": panels_per_page = 3
    # Add conditions for strip layouts if they can have variable panels
    if layout_style == "horizontal_strip" or layout_style == "vertical_strip":
        panels_per_page = state['panel_count']


    page_chunks = [state["panel_image_paths"][i:i + panels_per_page] for i in range(0, len(state["panel_image_paths"]), panels_per_page)]
    
    final_pages = []
    final_page_paths = []

    for i, page_chunk in enumerate(page_chunks):
        if layout_style == "feature_left" and len(page_chunk) < 3: continue
        if layout_style in ["grid_2x2", "mixed_2x2"] and len(page_chunk) < 4: continue

        if layout_style == "horizontal_strip": w, h = layout.get_horizontal_strip_dims(page_chunk)
        elif layout_style == "vertical_strip": w, h = layout.get_vertical_strip_dims(page_chunk)
        else: w, h = layout.get_grid_dims()

        page = Image.new('RGB', (w, h), color='white')

        # Add missing elif blocks for strip layouts
        if layout_style == "grid_2x2": page = layout.compose_grid_2x2(page, page_chunk)
        elif layout_style == "horizontal_strip": page = layout.compose_horizontal_strip(page, page_chunk)
        elif layout_style == "vertical_strip": page = layout.compose_vertical_strip(page, page_chunk)
        elif layout_style == "feature_left": page = layout.compose_feature_left(page, page_chunk)
        elif layout_style == "mixed_2x2": page = layout.compose_mixed_2x2(page, page_chunk)

        final_pages.append(page)
        page_path = f"{PAGES_DIR}/page_{i + 1}.png"
        page.save(page_path)
        final_page_paths.append(page_path)
        print(f"   > Saved composed page to: {page_path}")

    return {"final_page_images": final_pages, "final_page_paths": final_page_paths}
