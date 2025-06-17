from typing import TypedDict, List, Optional, Dict
from PIL import Image
from models.scene import Scene
from models.panel_layout_detail import PanelLayoutDetail

class ComicGenerationState(TypedDict):
    """
    Represents the shared state of our comic generation graph.
    """
    # Inputs from UI - these keys must match the initial 'inputs' dictionary
    story_text: str
    panel_count: int
    style_preset: Optional[str]
    genre_preset: Optional[str]
    layout_style: Optional[str]

    # Derived state added by agents
    character_description: str
    character_details: Dict[str, str]  # Added for individual character consistency
    artistic_style: str
    mood: str
    scenes: List[Scene]
    
    panel_layout_details: List[PanelLayoutDetail]

    panel_prompts: List[str]
    panel_image_paths: List[str]
    sized_panel_image_paths: List[str]
    panel_images_with_captions_paths: List[str]
    
    # Internal loop counter
    current_panel_index: int

    # Final outputs for UI
    final_page_images: List[Image.Image]
    final_page_paths: List[str]
