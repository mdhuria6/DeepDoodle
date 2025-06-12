from typing import TypedDict, List
from models.caption import Caption

class Scene(TypedDict):
    panel_description: str
    captions: List[Caption]
    # Potentially other scene-specific details in the future
