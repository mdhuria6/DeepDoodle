import logging
import json
from typing import Dict, Any, List
from models.comic_generation_state import ComicGenerationState
from utils.llm_factory import get_model_client
import re

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- High-Quality Prompt Template ---
SCENE_DECOMPOSER_PROMPT = """
**Role:** You are a master storyteller and comic book scriptwriter. Your task is to adapt a prose story into a rich, visual comic script, inferring dialogue and actions where a character would naturally speak or react.

**Task:** Read the user-provided story and decompose it into exactly {panel_count} chronological scenes. Your primary goal is to create a compelling narrative flow, using a mix of visual descriptions, narration, and dialogue.

**Critical Rules:**
1.  **Generate Dialogue:** Do not just convert sentences into narration. If a character has a realization, expresses an emotion, or takes a significant action, **you should invent a short, impactful line of dialogue for them**. The goal is to show, not just tell. If the original text says "she was shocked," you could create dialogue like "What is that?!".
2.  **Strict JSON Output:** The output MUST be a single, valid JSON array of panel objects. Do not include any text, explanations, or markdown formatting like ```json before or after the JSON array.
3.  **Purely Visual Descriptions:** The `description` field is for the artist. It must only contain visual information (camera shots, character poses, environment, lighting). It must NOT contain dialogue, narration, or sound effects.
4.  **Schema Adherence:** All fields (`panel`, `description`, `captions`, `order`, `speaker`, `text`, `type`, `location`) are mandatory as per the schema. For dialogue, `location` must be one of `"left"`, `"right"`, `"center"`, or `"auto"`.

**JSON Schema:**
[
  {{
    "panel": <integer>,
    "description": "<Visuals only. e.g., 'Close-up on Elara's wide, shocked eyes, illuminated by the green glow of the monitor.'>",
    "captions": [
      {{
        "order": <integer>,
        "speaker": "<'Narrator' or a character's name>",
        "text": "<The narration or the dialogue text.>",
        "type": "<'narration' or 'dialogue'>",
        "location": "<'left', 'right', 'center', or 'auto' (only for 'dialogue')>"
      }}
    ]
  }}
]


**Example Transformation:**

**User Story Input:** "The knight was shocked to see a dragon in the cave. He thought it was magnificent."

**Your Excellent JSON Output:**
[
  {{
    "panel": 1,
    "description": "Medium shot from inside a dark cave. A knight in shining armor stands silhouetted against the bright entrance. His posture is tense and surprised. Deeper in the cave, a small green dragon sleeps on a pile of gold.",
    "captions": [
      {{
        "order": 1,
        "speaker": "Knight",
        "text": "By the ancient kings... a real dragon!",
        "type": "dialogue",
        "location": "center"
      }}
    ]
  }}
]

**IMPORTANT:** Your response must start with `[` and end with `]`. It must be a raw JSON string, with no other text or formatting.

User Story to Process:
"{story_text}"
"""

# def build_scene_prompt(
#     story_text: str,
#     panel_count: int,
#     artistic_style: str,
#     mood: str,
#     character_descriptions: List[Dict[str, str]]
# ) -> str:
#     """
#     Constructs the full prompt for panel generation using story and metadata.
#     """
#     # Convert character_descriptions (list of dicts) to a readable string for the LLM prompt
#     if isinstance(character_descriptions, list) and character_descriptions and isinstance(character_descriptions[0], dict):
#         char_desc_str = "\n".join(
#             f'- "{c["name"]}": "{c["description"]}"' for c in character_descriptions if c.get('name') and c.get('description')
#         )
#     else:
#         char_desc_str = str(character_descriptions)

# 	# Format the prompt
#     prompt = SCENE_DECOMPOSER_PROMPT.format(panel_count=panel_count, story_text=story_text)
    
#     return prompt


def scene_decomposer(state: ComicGenerationState) -> dict:
	"""Decomposes the story into visual scenes with dialogue and narration using an LLM, with retries. Raises on error."""
	logger.info("---AGENT: Scene Decomposer---")

	panel_count = state['panel_count']
	story_text = state['story_text']
	text_engine = state.get("text_engine", "openai_gpt4") # Get selected engine
	max_retries = 2

	# Get the appropriate LLM client from the factory
	llm = get_model_client("text", text_engine)

	prompt = SCENE_DECOMPOSER_PROMPT.format(panel_count=panel_count, story_text=story_text)

	for attempt in range(max_retries):
		logger.info(f"   > Calling {text_engine} to decompose story... (Attempt {attempt + 1}/{max_retries})")
		try:
			response = llm.generate_text(prompt, max_tokens=8000)
			logger.debug(f"   > Raw LLM response: {response}")
			if response.startswith("```"):
				response = re.sub(r"^```[a-zA-Z]*\n?", "", response)
				response = re.sub(r"\n?```$", "", response)
				response = response.strip()
			scenes = json.loads(response)
			if not isinstance(scenes, list):
				logger.warning(f"   > Validation Failed: LLM output is not a list.")
				continue
			if len(scenes) != panel_count:
				logger.warning(f"   > Validation Failed: Expected {panel_count} panels, got {len(scenes)}.")
				continue
			logger.info(f"   > Successfully decomposed and validated into {len(scenes)} scenes.")
			logger.debug(f"   > Scene: {scenes}")
			return {
				"scenes": scenes, 
				"current_panel_index": 0
			}
		except json.JSONDecodeError:
			logger.warning("   > Validation Failed: LLM response was not valid JSON. Retrying...")
			logger.info(f"   > LLM Response: {response}")
			continue
		except Exception as e:
			logger.error(f"   > An unexpected error occurred during LLM call: {e}")
			continue

	logger.error("   > All LLM attempts failed. Unable to generate scenes.")
	raise RuntimeError("Failed to generate valid scenes from the story after multiple attempts.")
