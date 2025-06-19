import logging
import json
from typing import Dict, Any, List
from models.comic_generation_state import ComicGenerationState
from utils.huggingface_utils import get_hf_client

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_scene_prompt(
    story_text: str,
    panel_count: int,
    artistic_style: str,
    mood: str,
    character_descriptions: List[Dict[str, str]]
) -> str:
    """
    Constructs the full prompt for panel generation using story and metadata.
    """
    # Convert character_descriptions (list of dicts) to a readable string for the LLM prompt
    if isinstance(character_descriptions, list) and character_descriptions and isinstance(character_descriptions[0], dict):
        char_desc_str = "\n".join(
            f'- "{c["name"]}": "{c["description"]}"' for c in character_descriptions if c.get('name') and c.get('description')
        )
    else:
        char_desc_str = str(character_descriptions)

    error_message = """
        ERROR:agents.scene_decomposer:Invalid JSON returned by the LLM.
        INFO:agents.scene_decomposer:Raw LLM output:
        [
        {
            "panel": 1,
            "description": "Rian, a man in his 20s-30s with short hair, wearing a suit jacket, sits at a desk in a home office. He confidently adjusts his tie and looks at a computer screen displaying the Zoom interface.",
            "captions": [
            { "type": "caption", "speaker": "Narrator", "text": "Rian prepared for his company's big virtual presentation." }
            ]
        },
        {
            "panel": 2,
        Uncaught app execution
        json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes
        ValueError: Could not parse JSON from model response.
    """
    return f"""
You are a professional comic book storyboard artist. Your task is to break down the following story into exactly {panel_count} comic panels, suitable for AI-assisted image generation.

**Important Instructions:**
- You MUST return exactly {panel_count} panel entries. Do NOT return fewer or more. If the story is too long, summarize or combine moments. If too short, expand visually or show different angles.
- If you reach the end of the story before {panel_count} panels, invent visually interesting filler panels or alternate angles to reach the required count.
- If you run out of content, repeat the last scene with a different visual perspective or focus on a character's reaction.
- Do NOT stop or truncate the output early. Always output all {panel_count} panels.

---

Character Descriptions:
{char_desc_str}

---

Instructions for Each Panel:
For each panel, provide:
- A mandatory, detailed visual description focusing on characters, environment, and specific actions. Avoid vague or emotional language. Be specific about positioning, expressions, clothing, props, and background elements.
- A list of captions and/or dialogue, where each item is an object containing:
  - "type": Either "caption" or "dialogue" (use "caption" for narration, sounds, or ambient descriptions)
  - "speaker": The character’s name, "Narrator", or sound source (e.g., "Alarm Clock", "Dog")
  - "text": The caption or dialogue content
- A "panel" field with the panel number (as an integer). This number must not appear in the description or captions.

---

Sound Effects:
Include ambient sound effects (e.g., alarms, barks, footsteps, doors creaking) where appropriate. Use caption entries for these, with the speaker being the source (e.g., "Alarm Clock" or "Dog"), and the text in onomatopoeia form (e.g., "BEEP BEEP!", "Woof!", "Creeeak...").

---

Output Constraints:
- Return exactly {panel_count} panel entries — no more, no fewer.
- Every panel must include:
  - A non-empty, highly detailed "description"
  - At least one "caption" or "dialogue" in the "captions" list (if possible)
- Output must be a valid JSON array, with no extra commentary or text.
- Text in Each Caption should be a valid JSON string, properly escaped.
- Each Panel Description must be a valid JSON string, properly escaped.
- All property names and string values must use double quotes (") as per JSON standard.
- Ensure visual and naming consistency throughout.
- No trailing commas allowed.

---

Input Story:
{story_text}

Artistic Style: {artistic_style}  
Overall Mood: {mood}

---

Output Format Example:
[
  {{
    "panel": 1,
    "description": "A close-up of Alex holding a glowing spellbook inside a dusty, candle-lit library. Magical runes shimmer in the air around him. Cobwebs cling to nearby shelves filled with ancient tomes.",
    "captions": [
      {{ "type": "caption", "speaker": "Narrator", "text": {{"Alex discovers an ancient spellbook."}} }},
      {{ "type": "dialogue", "speaker": "Alex", "text": {{"What secrets do you hold?"}} }},
      {{ "type": "caption", "speaker": "Clock", "text": {{"Tick-tock... Tick-tock..."}} }}
    ]
  }}
  // ... more panels ...
]

Return only the JSON array as shown above. Do not include any extra text, comments, or explanations. All property names and string values must use double quotes (") as per JSON standard. Output MUST include all {panel_count} panels, even if you need to invent filler or alternate perspectives.
Review the error message occured during last try carefully to ensure you meet the requirements and donot repeat the mistake again. {error_message}.
""".strip()

def scene_decomposer(state: ComicGenerationState) -> Dict[str, Any]:
    """
    Decomposes the input story into comic panels with visual descriptions and captions/dialogue.
    """
    logger.info("AGENT: Scene Decomposer started.")

    # Extract and validate required fields
    story_text = state.get('story_text')
    panel_count = state.get('panel_count', 4)
    artistic_style = state.get('artistic_style', 'comic book style')
    mood = state.get('mood', 'neutral')
    character_descriptions = state.get('character_descriptions', [])

    if not story_text:
        logger.error("Missing required key 'story_text' in state.")
        raise ValueError("Missing required key 'story_text' in state.")

    logger.info(f"Generating {panel_count} comic panels.")

    # Construct prompt
    prompt = build_scene_prompt(
        story_text=story_text,
        panel_count=panel_count,
        artistic_style=artistic_style,
        mood=mood,
        character_descriptions=character_descriptions
    )

    # Call LLM via HuggingFace client
    hf_client = get_hf_client()
    messages = [
        {"role": "system", "content": "You are a professional comic book storyboard artist."},
        {"role": "user", "content": prompt}
    ]

    try:
        llm_response = hf_client.generate_conversation(
            messages=messages,
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            max_tokens=2500,
        )
        logger.info("LLM response received. Parsing output...")
        # Extract the content string from the ChatCompletionOutput object
        if hasattr(llm_response, "choices"):
            llm_content = llm_response.choices[0].message.content
        else:
            llm_content = llm_response  # fallback if already a string

    except Exception as e:
        logger.exception("Failed during LLM conversation generation.")
        raise RuntimeError("LLM conversation failed.") from e

    # Parse JSON response
    try:
        if isinstance(llm_content, str):
            logger.info("Parsing LLM output as JSON, as the content is a string.")
            scenes = json.loads(llm_content)
        else:
            logger.info("Not parsing the llm outpu, as the content is already a dict.")
            scenes = llm_content
        if not isinstance(scenes, list):
            raise ValueError("Expected a JSON array from model.")
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON returned by the LLM.")
        logger.info(f"Raw LLM output:\n{llm_content}")
        raise ValueError("Could not parse JSON from model response.") from e

    # Sanitize and validate panel content
    panel_map = {
        int(scene["panel"]): scene
        for scene in scenes
        if isinstance(scene, dict) and "panel" in scene
    }

    logger.info(f"Panel map created with {len(panel_map)} entries.")
    final_scenes: List[Dict[str, Any]] = []

    for i in range(1, panel_count + 1):
        scene = panel_map.get(i, {})
        description = scene.get("description", "").strip()
        captions = scene.get("captions", [])

        if not description:
            description = f"A detailed visual scene for panel {i} could not be generated."

        if not isinstance(captions, list) or not captions:
            captions = [{"type": "caption", "speaker": "Narrator", "text": f"A visual scene is depicted in panel {i}."}]

        final_scenes.append({
            "panel": i,
            "description": description,
            "captions": captions
        })

    logger.info(f"{len(final_scenes)} panels processed successfully.")
    logger.info(f"Final scenes: {json.dumps(final_scenes, indent=2)}")

    return {
        "scenes": final_scenes,
        "current_panel_index": state.get("current_panel_index", 0)
    }
