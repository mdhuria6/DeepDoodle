
import os
import sys

# ✅ Ensure the project root is in sys.path for clean imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from graph.state import ComicGenerationState
from utils.config import CHARACTER_DESCRIPTION  # Adjusted to match your utils path

def prompt_engineer(state: ComicGenerationState) -> dict:
    """
    Node 3: Crafts a detailed, consistent prompt for a single panel's image generation.
    """
    panel_index = state["current_panel_index"]
    print(f"---AGENT: Prompt Engineer (Panel {panel_index + 1})---")

    current_scene = state["scenes"][panel_index]
    style_suffix = f"in the style of {state['artistic_style']}"

    print(current_scene)
    print(style_suffix)

    # Build the prompt
    full_prompt = (
        f"{state['character_description']}, "
        f"{current_scene['description']}. "
        f"The overall mood is {state['mood']}. "
        f"{style_suffix}, high detail, cinematic lighting."
    )
    print(f"   > Generated Prompt: {full_prompt}...")

    # Add the new prompt to the state
    return {
        "panel_prompts": state["panel_prompts"] + [full_prompt]
    }
