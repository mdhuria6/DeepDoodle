from models.comic_generation_state import ComicGenerationState # Updated import
from configs.prompt_styles import STYLE_CONFIGS, DEFAULT_STYLE_KEYWORDS, DEFAULT_LIGHTING_KEYWORDS, DEFAULT_ADDITIONAL_DETAILS, DEFAULT_PROMPT_SUFFIX
import re

def prompt_engineer(state: ComicGenerationState) -> dict:
    """
    Node 3: Crafts a detailed, consistent prompt for a single panel's image generation
            using a dictionary-based style configuration.
    """
    panel_index = state.get("current_panel_index", 0)
    scenes = state.get("scenes", [])

    if not isinstance(scenes, list) or not scenes:
        print("[ERROR] No valid scenes found in state. Returning empty prompt list.")
        return {"panel_prompts": state.get("panel_prompts", [])}
    if panel_index >= len(scenes):
        print(f"[ERROR] Panel index {panel_index} out of range for scenes list.")
        return {"panel_prompts": state.get("panel_prompts", [])}
    try:
        current_scene = scenes[panel_index]
        print(f"   > Current Scene: {current_scene}")
        artistic_style_preset = state.get('artistic_style', 'Default Comic Style')
        config = STYLE_CONFIGS.get(artistic_style_preset)
        if config:
            style_keywords = config.get("style_keywords", DEFAULT_STYLE_KEYWORDS)
            lighting_keywords = config.get("lighting_keywords", DEFAULT_LIGHTING_KEYWORDS)
            additional_details = config.get("additional_details", DEFAULT_ADDITIONAL_DETAILS)
            prompt_suffix = config.get("prompt_suffix", DEFAULT_PROMPT_SUFFIX)
        else:
            print(f"   > Warning: Style preset '{artistic_style_preset}' not found in STYLE_CONFIGS. Using defaults and preset name.")
            style_keywords = f"in the style of {artistic_style_preset}, "
            lighting_keywords = DEFAULT_LIGHTING_KEYWORDS
            additional_details = DEFAULT_ADDITIONAL_DETAILS
            prompt_suffix = DEFAULT_PROMPT_SUFFIX
        # Join character descriptions into a single string
        character_desc = ", ".join(state.get('character_description', ['A character']))
        scene_desc = current_scene.get('description', '').strip()
        if not scene_desc or len(scene_desc) < 10:
            scene_desc = "A visually interesting comic panel scene."

        panel_prompts = state.get("panel_prompts", [])
        captions = current_scene.get('captions', [])
        if captions and isinstance(captions, list):
            for caption in captions:
                text = caption.get('text', '').strip()
                # Try to extract character dialogue: e.g., Grandma: "..."
                match = re.match(r'([A-Za-z0-9 _-]+):\s*"(.*)"', text)
                if match:
                    speaker = match.group(1).strip()
                    dialogue = match.group(2).strip()
                    prompt = (
                        f"Comic panel featuring: {character_desc}. "
                        f"Speaker: {speaker}. "
                        f"Dialogue: \"{dialogue}\". "
                        f"Scene: {scene_desc}. "
                        f"Art Style: {style_keywords}{lighting_keywords}, {additional_details}. "
                        f"Mood: {state.get('mood', 'neutral')}. "
                        f"{prompt_suffix}"
                    )
                    panel_prompts.append(prompt)
                else:
                    # Use the provided speaker or default to Narrator
                    speaker = caption.get('speaker', 'Narrator')
                    prompt = (
                        f"Comic panel featuring: {character_desc}. "
                        f"Speaker: {speaker}. "
                        f"Narration: \"{text}\". "
                        f"Scene: {scene_desc}. "
                        f"Art Style: {style_keywords}{lighting_keywords}, {additional_details}. "
                        f"Mood: {state.get('mood', 'neutral')}. "
                        f"{prompt_suffix}"
                    )
                    panel_prompts.append(prompt)
        else:
            # No captions, just a narrator prompt
            full_prompt = (
                f"Comic panel featuring: {character_desc}. "
                f"Speaker: Narrator. "
                f"Narration: \"{scene_desc}\". "
                f"Art Style: {style_keywords}{lighting_keywords}, {additional_details}. "
                f"Mood: {state.get('mood', 'neutral')}. "
                f"{prompt_suffix}"
            )
            panel_prompts.append(full_prompt)
        print(f"   > Generated Prompts: {panel_prompts}...")
        return {"panel_prompts": panel_prompts}
    except Exception as e:
        print(f"[ERROR] Exception in prompt_engineer: {e}")
        return {"panel_prompts": state.get("panel_prompts", [])}