from typing import TypedDict, List, Optional, Dict
from PIL import Image
from models.scene import Scene
from models.panel_layout_detail import PanelLayoutDetail # Import from new file

class ComicGenerationState(TypedDict):
    """
    Represents the shared state of our comic generation graph.
    """
    # Inputs from UI - these keys must match the initial 'inputs' dictionary
    story_text: str
    text_engine: str
    image_engine: str
    prompt:str
    panel_count: int
    style_preset: Optional[str]
    genre_preset: Optional[str]
    layout_style: Optional[str] # This might be used to guide the layout_planner or be superseded by its logic

    # Derived state added by agents
    character_descriptions: List[Dict[str, str]]
    artistic_style: str # This key is created by the story_analyst
    mood: str           # This key is also created by the story_analyst
    scenes: List[Scene] # Updated to use the Scene TypedDict
    
    panel_layout_details: List[PanelLayoutDetail] # Added for planned layout information

    panel_prompts: List[str]
    panel_image_paths: List[str] # Paths to raw images from image_generator
    sized_panel_image_paths: List[str] # Paths to images after panel_sizer_agent
    panel_images_with_captions_paths: List[str] # Paths to images after caption_agent
    
    # Internal loop counter
    current_panel_index: int

    # Final outputs for UI
    final_page_images: List[Image.Image]
    final_page_paths: List[str]
