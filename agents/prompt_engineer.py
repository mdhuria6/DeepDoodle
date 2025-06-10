from graph.state import ComicGenerationState
from utils import CHARACTER_DESCRIPTION

def prompt_engineer(state: ComicGenerationState) -> dict:
    """
    Node 3: Crafts a detailed, consistent prompt for a single panel's image generation.
    """
    panel_index = state["current_panel_index"]
    print(f"---AGENT: Prompt Engineer (Panel {panel_index + 1})---")

    current_scene = state["scenes"][panel_index]
    style_suffix = f"in the style of {state['artistic_style']}"

    # The core of the consistency strategy
    full_prompt = (
        f"{CHARACTER_DESCRIPTION}, "
        f"{current_scene['description']}. "
        f"The overall mood is {state['mood']}. "
        f"{style_suffix}, high detail, cinematic lighting."
    )
    print(f"   > Generated Prompt: {full_prompt[:100]}...")

    # Add the new prompt to our list in the state
    return {"panel_prompts": state["panel_prompts"] + [full_prompt]}