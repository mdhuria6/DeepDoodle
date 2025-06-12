from models.comic_generation_state import ComicGenerationState # Updated import
from configs.prompt_styles import STYLE_CONFIGS, DEFAULT_STYLE_KEYWORDS, DEFAULT_LIGHTING_KEYWORDS, DEFAULT_ADDITIONAL_DETAILS, DEFAULT_PROMPT_SUFFIX

def prompt_engineer(state: ComicGenerationState) -> dict:
    """
    Node 3: Crafts a detailed, consistent prompt for a single panel's image generation
            using a dictionary-based style configuration.
    """
    panel_index = state["current_panel_index"]
    print(f"---AGENT: Prompt Engineer (Panel {panel_index + 1})---")

    current_scene = state["scenes"][panel_index]
    artistic_style_preset = state['artistic_style']

    # Retrieve style configuration from the dictionary
    config = STYLE_CONFIGS.get(artistic_style_preset)

    if config:
        style_keywords = config.get("style_keywords", DEFAULT_STYLE_KEYWORDS)
        lighting_keywords = config.get("lighting_keywords", DEFAULT_LIGHTING_KEYWORDS)
        additional_details = config.get("additional_details", DEFAULT_ADDITIONAL_DETAILS)
        prompt_suffix = config.get("prompt_suffix", DEFAULT_PROMPT_SUFFIX)
    else:
        # Fallback for any style_preset not explicitly defined in STYLE_CONFIGS
        print(f"   > Warning: Style preset \'{artistic_style_preset}\' not found in STYLE_CONFIGS. Using defaults and preset name.")
        style_keywords = f"in the style of {artistic_style_preset}, "
        lighting_keywords = DEFAULT_LIGHTING_KEYWORDS
        additional_details = DEFAULT_ADDITIONAL_DETAILS
        prompt_suffix = DEFAULT_PROMPT_SUFFIX

    full_prompt = (
        f"{state['character_description']}, "
        f"{current_scene['description']}. "
        f"Art Style: {style_keywords}{lighting_keywords}, {additional_details}. "
        f"The overall mood is {state['mood']}."
        f"{prompt_suffix}" # Append suffix, which might be empty
    )

    print(f"   > Generated Prompt: {full_prompt[:250]}...") # Increased print length

    # Add the new prompt to our list in the state
    return {"panel_prompts": state["panel_prompts"] + [full_prompt]}