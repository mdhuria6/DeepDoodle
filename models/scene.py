from typing import TypedDict, List
from models.caption import Caption

class Scene(TypedDict):
    panelId: int  # Unique identifier for the panel
    panel_description: str
    captions: List[Caption]
    # Potentially other scene-specific details in the future
