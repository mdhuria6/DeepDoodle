from typing import TypedDict, Literal, Optional

class Caption(TypedDict):
    text: str
    position: Literal["top", "bottom", "center", "narrator_top", "narrator_bottom"]
    speaker: Optional[str] # Character name, "Narrator", "SFX", or None
    type: Literal["dialogue", "sfx", "narrator", "caption"] # Specific types
