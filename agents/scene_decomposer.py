import logging
from typing import Dict, Any, List
from models.comic_generation_state import ComicGenerationState
from utils.huggingface_utils import get_hf_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scene_decomposer(state: ComicGenerationState) -> Dict[str, Any]:
    """
    Decompose the story into exactly panel_count comic panels, each with a detailed description and (if possible) captions/dialogue.
    """
    story_text = state['story_text']
    panel_count = state['panel_count']
    artistic_style = state.get('artistic_style', 'comic book style')
    mood = state.get('mood', 'neutral')

    prompt = f"""
You are a professional comic book storyboard artist. Break the following story into exactly {panel_count} comic panels for AI image generation.

For each panel, provide:
- A mandatory, detailed, visual description (focus on characters, setting, and action; avoid abstract/emotional language)
- Captions and/or dialogue (as a list of objects with type, speaker, and text; include at least one per panel if possible)
- The panel number (as a field only, do NOT mention it in the description or captions)

**Important:**
- Do NOT include the panel number in the description or captions text. Only use the 'panel' field for numbering.
- You MUST return exactly {panel_count} panels. Do not return more or fewer. If the story is too long, summarize or combine events. If too short, split visually.
- Each object in the array MUST have these keys: panel (int), description (string, must be non-empty and detailed), captions (list of objects with type, speaker, text; at least one per panel if possible).
- Every panel MUST have a non-empty, detailed description. Do not leave any description blank or generic.
- Return ONLY a valid JSON array, no extra text or commentary.
- Do NOT include trailing commas.
- Use consistent character names and visual cues.

Story:
"""
    prompt += story_text
    prompt += f"""

Artistic Style: {artistic_style}
Overall Mood: {mood}

Format example:
[
  {{
    "panel": 1,
    "description": "A close-up of the main character, Alex, holding a glowing spellbook in a dusty library. Magical sparkles fill the air.",
    "captions": [
      {{"type": "caption", "speaker": "Narrator", "text": "Alex discovers an ancient spellbook."}},
      {{"type": "dialogue", "speaker": "Alex", "text": "What secrets do you hold?"}}
    ]
  }},
  ...
]

Return ONLY the JSON array, nothing else.
"""

    hf_client = get_hf_client()
    messages = [
        {"role": "system", "content": "You are a professional comic book storyboard artist."},
        {"role": "user", "content": prompt}
    ]
    llm_response = hf_client.generate_conversation(
        messages=messages,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=1800,
        temperature=0.7
    )
    logger.debug(f"LLM Response: {llm_response[:300]}...")
    scenes = hf_client.parse_json_response(llm_response)

    # Strict post-processing: ensure exactly panel_count, no empty descriptions, at least one caption/dialogue
    filtered_scenes = []
    for i in range(panel_count):
        if isinstance(scenes, list) and i < len(scenes):
            scene = scenes[i]
            desc = scene.get("description", "").strip()
            captions = scene.get("captions")
            if not desc:
                reprompt = f"Write a detailed, visual comic panel description for panel {i+1} of this story.\nStory: {story_text}"
                reprompt_msgs = [
                    {"role": "system", "content": "You are a professional comic book storyboard artist."},
                    {"role": "user", "content": reprompt}
                ]
                desc = hf_client.generate_conversation(
                    messages=reprompt_msgs,
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    max_tokens=120,
                    temperature=0.7
                ).strip()
            if not isinstance(captions, list) or len(captions) == 0:
                reprompt = f"Write a short comic panel caption or dialogue for panel {i+1} of this story.\nStory: {story_text}"
                reprompt_msgs = [
                    {"role": "system", "content": "You are a professional comic book storyboard artist."},
                    {"role": "user", "content": reprompt}
                ]
                cap_text = hf_client.generate_conversation(
                    messages=reprompt_msgs,
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    max_tokens=60,
                    temperature=0.7
                ).strip()
                captions = [{"type": "caption", "speaker": "Narrator", "text": cap_text}]
            filtered_scenes.append({
                "panel": i+1,
                "description": desc,
                "captions": captions
            })
        else:
            reprompt = f"Write a detailed, visual comic panel description for panel {i+1} of this story.\nStory: {story_text}"
            reprompt_msgs = [
                {"role": "system", "content": "You are a professional comic book storyboard artist."},
                {"role": "user", "content": reprompt}
            ]
            desc = hf_client.generate_conversation(
                messages=reprompt_msgs,
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                max_tokens=120,
                temperature=0.7
            ).strip()
            reprompt = f"Write a short comic panel caption or dialogue for panel {i+1} of this story.\nStory: {story_text}"
            reprompt_msgs = [
                {"role": "system", "content": "You are a professional comic book storyboard artist."},
                {"role": "user", "content": reprompt}
            ]
            cap_text = hf_client.generate_conversation(
                messages=reprompt_msgs,
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                max_tokens=60,
                temperature=0.7
            ).strip()
            filtered_scenes.append({
                "panel": i+1,
                "description": desc,
                "captions": [{"type": "caption", "speaker": "Narrator", "text": cap_text}]
            })
    logger.info(f"Final scene count: {len(filtered_scenes)}")
    logger.info(f"Scenes: {filtered_scenes}")
    logger.info("\nScene decomposition complete.\n")
    
    # Post-process to remove any panel numbers from description/captions
    import re
    for scene in filtered_scenes:
        # Remove 'Panel X:' or 'Panel X -' or similar from description
        scene['description'] = re.sub(r"^[Pp]anel\s*\d+[:\-\.]?\s*", "", scene['description']).strip()
        # Remove panel numbers from captions
        for cap in scene['captions']:
            if isinstance(cap.get('text'), str):
                cap['text'] = re.sub(r"^[Pp]anel\s*\d+[:\-\.]?\s*", "", cap['text']).strip()

    return {"scenes": filtered_scenes, "current_panel_index": state.get("current_panel_index", 0)}