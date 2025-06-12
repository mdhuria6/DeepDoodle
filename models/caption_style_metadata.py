from typing import TypedDict, Optional

# --- Configuration Model ---
class CaptionStyleMetadata(TypedDict):
    font_path: str
    max_font_size: int
    min_font_size: int
    default_font_size: int
    line_spacing: int
    caption_margin: int
    caption_padding: int
    max_caption_height_ratio: float
    caption_background_color: str
    narrator_background_color: str
    caption_text_color: str
    caption_corner_radius: int
    sfx_text_color: Optional[str]
    sfx_font_path: Optional[str]
    border_color: Optional[str]  # Added
    border_width: Optional[int]  # Added