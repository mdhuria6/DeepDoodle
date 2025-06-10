from typing import TypedDict, List, Optional
from PIL import Image

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
    artistic_style: str # This key is created by the story_analyst
    mood: str           # This key is also created by the story_analyst
    scenes: List[dict]
    panel_prompts: List[str]
    panel_image_paths: List[str]
    
    # Internal loop counter
    current_panel_index: int

    # Final outputs for UI
    final_page_images: List[Image.Image]
    final_page_paths: List[str]