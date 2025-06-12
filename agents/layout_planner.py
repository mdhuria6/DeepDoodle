# filepath: agents/layout_planner.py
import math
from typing import List, Dict, Tuple, Optional

from models.comic_generation_state import ComicGenerationState #type: ignore
from models.panel_layout_detail import PanelLayoutDetail #type: ignore
from configs import PAGE_WIDTH, PAGE_HEIGHT, MARGIN

GENERATION_DIM_MULTIPLE = 64

def round_to_multiple(number: float, multiple: int) -> int:
    """Rounds a number to the nearest multiple. Ensures result is at least the multiple if input is positive."""
    if number <= 0:
        return multiple 
    return max(multiple, multiple * round(number / multiple))

# --- Layout Configuration Helper Functions ---
def get_grid_2x2_config(page_w: int, page_h: int, margin: int) -> list[dict]:
    ideal_slot_w = int(round((page_w - 3 * margin) / 2))
    ideal_slot_h = int(round((page_h - 3 * margin) / 2))
    return [
        {"w": ideal_slot_w, "h": ideal_slot_h, "x": margin, "y": margin},
        {"w": ideal_slot_w, "h": ideal_slot_h, "x": margin + ideal_slot_w + margin, "y": margin},
        {"w": ideal_slot_w, "h": ideal_slot_h, "x": margin, "y": margin + ideal_slot_h + margin},
        {"w": ideal_slot_w, "h": ideal_slot_h, "x": margin + ideal_slot_w + margin, "y": margin + ideal_slot_h + margin}
    ]

def get_feature_left_config(page_w: int, page_h: int, margin: int) -> list[dict]:
    """
    Layout for 3 panels:
    - Two equal-width columns.
    - Left column: One full-height panel (P1).
    - Right column: Two panels, small (P2) on top of large (P3).
    """
    col_width = int(round((page_w - 3 * margin) / 2))

    # Left column panel (P1)
    p1_h = int(round(page_h - 2 * margin)) # Full height within page margins

    # Right column panels (P2, P3)
    right_col_allocatable_h = int(round(page_h - 2 * margin - margin)) # Total height for 2 panels + 1 internal margin
    p2_h_small = int(round(right_col_allocatable_h * 0.4)) # Small panel is 40% of allocatable height
    p3_h_large = right_col_allocatable_h - p2_h_small      # Large panel takes the rest

    return [
        # P1: Left, Full Height
        {"w": col_width, "h": p1_h, "x": margin, "y": margin},
        # P2: Right, Top, Small
        {"w": col_width, "h": p2_h_small, "x": margin + col_width + margin, "y": margin},
        # P3: Right, Bottom, Large
        {"w": col_width, "h": p3_h_large, "x": margin + col_width + margin, "y": margin + p2_h_small + margin}
    ]

def get_horizontal_strip_4_config(page_w: int, page_h: int, margin: int) -> list[dict]:
    """Layout for 4 panels stacked vertically."""
    panels_on_page = 4
    ideal_slot_w = int(round(page_w - 2 * margin))
    ideal_slot_h = int(round((page_h - (panels_on_page + 1) * margin) / panels_on_page))
    configs = []
    current_y = margin
    for _ in range(panels_on_page):
        configs.append({"w": ideal_slot_w, "h": ideal_slot_h, "x": margin, "y": current_y})
        current_y += ideal_slot_h + margin
    return configs

def get_vertical_strip_3_config(page_w: int, page_h: int, margin: int) -> list[dict]:
    """Layout for 3 panels arranged horizontally."""
    panels_on_page = 3
    ideal_slot_h = int(round(page_h - 2 * margin))
    ideal_slot_w = int(round((page_w - (panels_on_page + 1) * margin) / panels_on_page))
    configs = []
    current_x = margin
    for _ in range(panels_on_page):
        configs.append({"w": ideal_slot_w, "h": ideal_slot_h, "x": current_x, "y": margin})
        current_x += ideal_slot_w + margin
    return configs

def get_mixed_2x2_config(page_w: int, page_h: int, margin: int) -> list[dict]:
    """
    Layout for 4 panels in a "masonry-like" mixed 2x2 grid:
    - Two equal-width columns.
    - Col 1 (Left): Small panel (P1) on top of Large panel (P3).
    - Col 2 (Right): Large panel (P2) on top of Small panel (P4).
    P1 (top-left) and P4 (bottom-right) are small.
    P2 (top-right) and P3 (bottom-left) are large.
    """
    col_width = int(round((page_w - 3 * margin) / 2))
    
    # Height calculation for panels within a column
    # Total height available for two panels and one margin between them, within the page's top/bottom margins
    allocatable_h_for_two_panels = int(round(page_h - 2 * margin - margin)) 
    
    h_small = int(round(allocatable_h_for_two_panels * 0.4)) # Small panel is 40%
    h_large = allocatable_h_for_two_panels - h_small         # Large panel is 60%

    return [
        # P1: Top-left (Small)
        {"w": col_width, "h": h_small, "x": margin, "y": margin},
        # P2: Top-right (Large)
        {"w": col_width, "h": h_large, "x": margin + col_width + margin, "y": margin},
        # P3: Bottom-left (Large)
        {"w": col_width, "h": h_large, "x": margin, "y": margin + h_small + margin},
        # P4: Bottom-right (Small)
        {"w": col_width, "h": h_small, "x": margin + col_width + margin, "y": margin + h_large + margin}
    ]

def get_horizontal_strip_2_config(page_w: int, page_h: int, margin: int) -> list[dict]:
    panels_on_page = 2
    ideal_slot_w = int(round(page_w - 2 * margin))
    ideal_slot_h = int(round((page_h - (panels_on_page + 1) * margin) / panels_on_page))
    return [
        {"w": ideal_slot_w, "h": ideal_slot_h, "x": margin, "y": margin},
        {"w": ideal_slot_w, "h": ideal_slot_h, "x": margin, "y": margin + ideal_slot_h + margin}
    ]

def get_vertical_strip_2_config(page_w: int, page_h: int, margin: int) -> list[dict]:
    panels_on_page = 2
    ideal_slot_h = int(round(page_h - 2 * margin))
    ideal_slot_w = int(round((page_w - (panels_on_page + 1) * margin) / panels_on_page))
    return [
        {"w": ideal_slot_w, "h": ideal_slot_h, "x": margin, "y": margin},
        {"w": ideal_slot_w, "h": ideal_slot_h, "x": margin + ideal_slot_w + margin, "y": margin}
    ]

def get_single_panel_config(page_w: int, page_h: int, margin: int) -> list[dict]:
    ideal_slot_w = int(round(page_w - 2 * margin))
    ideal_slot_h = int(round(page_h - 2 * margin) / 3)
    return [{"w": ideal_slot_w, "h": ideal_slot_h, "x": margin, "y": margin}]

# --- Layout Definitions ---
# Maps layout type string to its properties: number of panels and config generation function.
layout_definitions = {
    # UI Facing Layouts - keys should match what Streamlit sends
    "grid_2x2": {"panels": 4, "config_func": get_grid_2x2_config},         # UI: "2x2 Grid"
    "horizontal_strip": {"panels": 4, "config_func": get_horizontal_strip_4_config}, # UI: "Horizontal Strip"
    "vertical_strip": {"panels": 3, "config_func": get_vertical_strip_3_config},   # UI: "Vertical Strip"
    "feature_left": {"panels": 3, "config_func": get_feature_left_config},       # UI: "Featured Panel"
    "mixed_2x2": {"panels": 4, "config_func": get_mixed_2x2_config},          # UI: "Mixed Grid"

    # Dynamic Fallback / Additional Layouts (can also be selected if UI sends these exact keys)
    "horizontal_strip_2": {"panels": 2, "config_func": get_horizontal_strip_2_config},
    "vertical_strip_2": {"panels": 2, "config_func": get_vertical_strip_2_config},
    "single_panel": {"panels": 1, "config_func": get_single_panel_config},
}

def layout_planner(state: ComicGenerationState) -> ComicGenerationState:
    """
    Determines page layouts and calculates ideal and target generation dimensions for each panel.
    Prioritizes UI-selected layout style, falling back to dynamic logic for partial/last pages
    or if no preference is set.
    """
    print("---AGENT: Layout Planner---")
    panel_count = state['panel_count']
    preferred_layout_style = state.get('layout_style') # From UI, e.g., "grid_2x2"

    panel_layout_details: list[PanelLayoutDetail] = []
    current_panel_global_idx = 0
    page_number = 1

    while current_panel_global_idx < panel_count:
        panels_remaining_total = panel_count - current_panel_global_idx
        page_layout_type = ""
        # How many panels the chosen layout type is designed for
        panels_layout_can_take = 0 
        panel_configs_for_page: list[dict] = []
        
        use_preferred_layout_this_page = False

        # Try to use preferred layout if set and applicable
        if preferred_layout_style and preferred_layout_style in layout_definitions:
            layout_info = layout_definitions[preferred_layout_style]
            num_panels_for_preferred = layout_info["panels"]
            if panels_remaining_total >= num_panels_for_preferred:
                page_layout_type = preferred_layout_style
                panels_layout_can_take = num_panels_for_preferred
                panel_configs_for_page = layout_info["config_func"](PAGE_WIDTH, PAGE_HEIGHT, MARGIN)
                use_preferred_layout_this_page = True
                print(f"   > Page {page_number}: Using UI preferred layout '{page_layout_type}' (for {panels_layout_can_take} panels).")

        # If preferred layout not used (not set, unknown, or not enough panels for it)
        if not use_preferred_layout_this_page:
            print(f"   > Page {page_number}: UI preference not used or not applicable. Dynamically choosing layout for up to {panels_remaining_total} panel(s).")
            
            # Dynamic layout choice for the current page based on panels_remaining_total
            chosen_dynamically = False
            if panels_remaining_total >= 4 and "grid_2x2" in layout_definitions:
                page_layout_type = "grid_2x2"
                chosen_dynamically = True
            elif panels_remaining_total == 3 and "feature_left" in layout_definitions:
                page_layout_type = "feature_left"
                chosen_dynamically = True
            elif panels_remaining_total == 2 and "horizontal_strip_2" in layout_definitions: # Defaulting to horizontal for 2
                page_layout_type = "horizontal_strip_2"
                chosen_dynamically = True
            elif panels_remaining_total >= 1 and "single_panel" in layout_definitions: # Handles 1 panel
                page_layout_type = "single_panel"
                chosen_dynamically = True
            
            if chosen_dynamically:
                layout_info = layout_definitions[page_layout_type]
                panels_layout_can_take = layout_info["panels"]
                panel_configs_for_page = layout_info["config_func"](PAGE_WIDTH, PAGE_HEIGHT, MARGIN)
                print(f"   > Page {page_number}: Dynamically selected '{page_layout_type}' (for {panels_layout_can_take} panels).")
            else: # Should only happen if panels_remaining_total is 0 or layout_definitions is incomplete
                if panels_remaining_total == 0: # All panels processed
                    break 
                print(f"Warning: Could not determine dynamic layout for {panels_remaining_total} panels. Breaking.")
                break
        
        # Determine how many panels will actually be processed and placed on this page
        num_panels_to_process_on_page = min(panels_layout_can_take, panels_remaining_total)
        
        if num_panels_to_process_on_page == 0 and panels_remaining_total > 0:
             # This might happen if a layout was selected (e.g. preferred) but panels_layout_can_take was 0 (error in defs)
             # Or if dynamic selection failed to set panels_layout_can_take > 0.
             # Fallback to a single panel to ensure progress if possible.
             print(f"Error: Layout selected but num_panels_to_process_on_page is 0 with {panels_remaining_total} panels remaining. Defaulting to single panel for one panel.")
             page_layout_type = "single_panel"
             if "single_panel" in layout_definitions:
                 layout_info = layout_definitions[page_layout_type]
                 panels_layout_can_take = layout_info["panels"] # Should be 1
                 panel_configs_for_page = layout_info["config_func"](PAGE_WIDTH, PAGE_HEIGHT, MARGIN)
                 num_panels_to_process_on_page = min(panels_layout_can_take, panels_remaining_total) # Recalculate
             else: # Critical error if single_panel is not defined
                 print("CRITICAL: single_panel layout not defined. Cannot proceed.")
                 break


        if num_panels_to_process_on_page > 0:
            print(f"   > Page {page_number}: Finalizing layout '{page_layout_type}', will place {num_panels_to_process_on_page} panel(s) on this page.")
        else:
            if panels_remaining_total > 0: 
                 print(f"Warning: No panels assigned to page {page_number} despite {panels_remaining_total} panels remaining. Breaking.")
            break # Break if no panels can be processed (e.g. all done, or error)

        for i in range(num_panels_to_process_on_page):
            # This check should be redundant due to panels_remaining_total and num_panels_to_process_on_page logic
            if current_panel_global_idx >= panel_count: 
                break 

            config = panel_configs_for_page[i] # panel_configs_for_page should have enough items
            ideal_w = config["w"]
            ideal_h = config["h"]
            
            # Ensure ideal dimensions are positive before rounding for generation
            if ideal_w <= 0: ideal_w = GENERATION_DIM_MULTIPLE # Fallback
            if ideal_h <= 0: ideal_h = GENERATION_DIM_MULTIPLE # Fallback

            detail = PanelLayoutDetail(
                panel_index=current_panel_global_idx,
                page_number=page_number,
                page_layout_type=page_layout_type, # Store the actual layout used for this panel's page
                ideal_width=ideal_w,
                ideal_height=ideal_h,
                target_generation_width=round_to_multiple(ideal_w, GENERATION_DIM_MULTIPLE),
                target_generation_height=round_to_multiple(ideal_h, GENERATION_DIM_MULTIPLE),
                ideal_x_offset=config["x"],
                ideal_y_offset=config["y"]
            )
            panel_layout_details.append(detail)
            current_panel_global_idx += 1
        
        if num_panels_to_process_on_page > 0:
            page_number += 1
        # If num_panels_to_process_on_page was 0, loop should have broken or will break due to current_panel_global_idx not changing

    state['panel_layout_details'] = panel_layout_details
    if panel_layout_details:
        final_page_num = panel_layout_details[-1]['page_number'] if panel_layout_details else 0
        print(f"   > Planned layouts for {len(panel_layout_details)} panels across {final_page_num} pages.")
    else:
        print("   > No panels to plan layouts for.")
    return state

