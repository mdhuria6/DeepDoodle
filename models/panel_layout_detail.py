# filepath: models/panel_layout_detail.py
from typing import TypedDict

class PanelLayoutDetail(TypedDict):
    panel_index: int
    page_number: int
    page_layout_type: str  # e.g., "2x2_grid", "vertical_strip"
    ideal_width: int
    ideal_height: int
    target_generation_width: int  # Multiple of 64
    target_generation_height: int # Multiple of 64
    # Position on page (x, y) might also be useful later for page_composer
    ideal_x_offset: int
    ideal_y_offset: int
