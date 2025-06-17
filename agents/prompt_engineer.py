from models.comic_generation_state import ComicGenerationState  # Updated import
from configs.prompt_styles import (
    STYLE_CONFIGS,
    DEFAULT_STYLE_KEYWORDS,
    DEFAULT_LIGHTING_KEYWORDS,
    DEFAULT_ADDITIONAL_DETAILS,
    DEFAULT_PROMPT_SUFFIX,
)
import re
import logging

# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prompt_engineer(state: ComicGenerationState) -> dict:
    """
    Crafts a detailed, consistent prompt for a single panel's image generation
    using a dictionary-based style configuration.

    Args:
        state (ComicGenerationState): The current state of the comic generation process.

    Returns:
        dict: A dictionary containing the generated panel prompts.
    """
    panel_index = state.get("current_panel_index", 0)
    scenes = state.get("scenes", [])

    logger.info(f"---AGENT: Prompt Engineer (Panel {panel_index + 1})---")

    # Validate scenes list
    if not isinstance(scenes, list) or not scenes:
        logger.error("No valid scenes found in state. Returning empty prompt list.")
        return {"panel_prompts": state.get("panel_prompts", [])}

    if panel_index >= len(scenes):
        logger.error(f"Panel index {panel_index} out of range for scenes list.")
        return {"panel_prompts": state.get("panel_prompts", [])}

    try:
        current_scene = scenes[panel_index]
        logger.info(f"Current Scene: {current_scene}")

        # Retrieve artistic style configuration
        artistic_style_preset = state.get('artistic_style', 'Default Comic Style')
        config = STYLE_CONFIGS.get(artistic_style_preset)
        if config:
            style_keywords = config.get("style_keywords", DEFAULT_STYLE_KEYWORDS)
            lighting_keywords = config.get("lighting_keywords", DEFAULT_LIGHTING_KEYWORDS)
            additional_details = config.get("additional_details", DEFAULT_ADDITIONAL_DETAILS)
            prompt_suffix = config.get("prompt_suffix", DEFAULT_PROMPT_SUFFIX)
            logger.info(f"Using style preset: {artistic_style_preset}")
        else:
            logger.warning(
                f"Style preset '{artistic_style_preset}' not found in STYLE_CONFIGS. Using defaults and preset name."
            )
            style_keywords = [f"in the style of {artistic_style_preset}"]
            lighting_keywords = DEFAULT_LIGHTING_KEYWORDS
            additional_details = DEFAULT_ADDITIONAL_DETAILS
            prompt_suffix = DEFAULT_PROMPT_SUFFIX

        # Fix: Join style keywords, lighting keywords, or additional details if they are lists of single characters
        def join_if_char_list(val):
            if isinstance(val, list) and all(isinstance(x, str) and len(x) == 1 for x in val):
                return ''.join(val).replace('  ', ' ').strip()
            return val

        style_keywords = join_if_char_list(style_keywords)
        lighting_keywords = join_if_char_list(lighting_keywords)
        additional_details = join_if_char_list(additional_details)

        # If style_keywords is a string, wrap in list for join below
        if isinstance(style_keywords, str):
            style_keywords = [style_keywords]
        if isinstance(lighting_keywords, str):
            lighting_keywords = lighting_keywords
        if isinstance(additional_details, str):
            additional_details = additional_details

        # Get all character descriptions from state
        character_descriptions = state.get('character_descriptions', [])
        # Extract character names present in this panel (from captions and description)
        present_names = set()
        captions = current_scene.get('captions', [])
        for caption in captions:
            speaker = caption.get('speaker')
            if speaker and speaker.lower() != "narrator":
                present_names.add(speaker)
        # Optionally, try to extract names from the description (simple heuristic)
        desc_text = current_scene.get('description', '')
        for char in character_descriptions:
            name = char.get('name')
            if name and name in desc_text:
                present_names.add(name)
        # If no names found, fallback to all main characters
        if not present_names and character_descriptions:
            present_names = {char.get('name') for char in character_descriptions if char.get('name')}
        # Build a string of character names (not full descriptions) for those present
        if character_descriptions and present_names:
            character_names_str = ", ".join(
                c['name'] for c in character_descriptions if c.get('name') in present_names
            )
            # Optionally, add a comment with full descriptions for context (not in prompt)
            character_desc_comment = " | ".join(
                f"{c['name']}: {c['description']}" for c in character_descriptions if c.get('name') in present_names
            )
        else:
            character_names_str = "A character"
            character_desc_comment = ""

        # Get scene description, fallback if too short or missing
        scene_desc = current_scene.get('description', '').strip()
        if not scene_desc or len(scene_desc) < 5:
            scene_desc = "A visually interesting comic panel scene."

        panel_prompts = state.get("panel_prompts", [])
        captions = current_scene.get('captions', [])

        logger.info(f"Scene description: {scene_desc}")
        logger.info(f"Character names present: {present_names}")
        logger.info(f"Character descriptions: {character_desc_comment}")
        logger.info(f"Panel prompts before processing: {panel_prompts}")

        # Process captions if available
        # Prepare character descriptions string for prompt context
        if character_desc_comment:
            character_context = f"Characters: {character_desc_comment}. "
        else:
            character_context = ""

        if captions and isinstance(captions, list):
            for caption in captions:
                text = caption.get('text', '').strip()
                speaker = caption.get('speaker', 'Narrator')
                if text:
                    prompt = (
                        f"Comic panel featuring: {character_names_str}. "
                        f"{character_context}"
                        f"Speaker: {speaker}. "
                        f"Dialogue: \"{text}\". "
                        f"Scene: {scene_desc}. "
                        f"Art Style: {', '.join(style_keywords)}, {lighting_keywords}, {additional_details}. "
                        f"Mood: {state.get('mood', 'neutral')}. "
                        f"{prompt_suffix}"
                    )
                    logger.info(f"Generated prompt: {prompt}")
                    panel_prompts.append(prompt)
        else:
            # No captions, just a narrator prompt
            full_prompt = (
                f"Comic panel featuring: {character_names_str}. "
                f"{character_context}"
                f"Speaker: Narrator. "
                f"Narration: \"{scene_desc}\". "
                f"Art Style: {', '.join(style_keywords)}, {lighting_keywords}, {additional_details}. "
                f"Mood: {state.get('mood', 'neutral')}. "
                f"{prompt_suffix}"
            )
            logger.info(f"Generated default narrator prompt: {full_prompt}")
            panel_prompts.append(full_prompt)

        return {"panel_prompts": panel_prompts}

    except Exception as e:
        logger.error(f"Exception in prompt_engineer: {e}", exc_info=True)
        return {"panel_prompts": state.get("panel_prompts", [])}