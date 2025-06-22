import logging
import json
from models.comic_generation_state import ComicGenerationState
from utils.response_util import sanitize_llm_response
from utils.llm_factory import get_model_client
from utils.load_prompts import load_prompt_template
from typing import List, Dict
import re

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_scene_prompt(
	story_text: str,
	panel_count: int,
	artistic_style: str,
	mood: str,
	character_descriptions: List[Dict[str, str]],
	prompt_file: str = "hybrid_scene_decomposer_prompt.txt"
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

	# Format the prompt
	# Load the analysis prompt from the specified file
	prompt_template = load_prompt_template(
		prompt_folder="prompts/scene_decomposer",
		prompt_file=prompt_file,
		input_variables=["story_text", "panel_count", "char_desc_str", "artistic_style", "mood"]
	)
	prompt = prompt_template.format(
		story_text=story_text,
		panel_count=panel_count,
		char_desc_str=char_desc_str,
		artistic_style=artistic_style,
		mood=mood
	)
	return prompt


def scene_decomposer(state: ComicGenerationState, prompt_file: str = "hybrid_scene_dec_prompt.txt") -> dict:
	"""Decomposes the story into visual scenes with dialogue and narration using an LLM, with retries. Raises on error."""
	logger.info("---AGENT: Scene Decomposer---")

	panel_count = state['panel_count']
	story_text = state['story_text']
	text_engine = state.get("text_engine", "openai_gpt4") # Get selected engine
	max_retries = 2

	# Get the appropriate LLM client from the factory
	llm = get_model_client("text", text_engine)

	character_descriptions = state.get('character_descriptions', [])
	artistic_style = state.get('artistic_style', '')
	mood = state.get('mood', '')
	prompt = build_scene_prompt(
		story_text=story_text,
		panel_count=panel_count,
		artistic_style=artistic_style,
		mood=mood,
		character_descriptions=character_descriptions,
		prompt_file=prompt_file
	)

	logger.info(f"   > Generated prompt for LLM: {prompt}")
	
	for attempt in range(max_retries):
		logger.info(f"   > Calling {text_engine} to decompose story... (Attempt {attempt + 1}/{max_retries})")
		try:
			response = llm.generate_text(prompt, max_tokens=8000)
			response = sanitize_llm_response(response)  # Clean up the response
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
