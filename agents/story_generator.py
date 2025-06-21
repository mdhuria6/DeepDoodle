import logging
from typing import Dict, Any
from models.comic_generation_state import ComicGenerationState
from utils.llm_factory import get_model_client
from configs import STORY_EXPANSION_WORD_LIMIT
from utils.load_prompts import load_prompt_template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def story_generator(state: ComicGenerationState) -> Dict[str, Any]:
    logger.info("------ AGENT: Story Generator --------")
    try:
        story_text = state.get('story_text', '')
        artistic_style = state.get('style_preset')
        mood = state.get('genre_preset')
        layout_style = state.get('layout_style')
        character_descriptions = state.get('character_description')
        text_engine = state.get('text_engine', 'mistral_mixtral_8x7b_instruct')
        llm = get_model_client("text", text_engine)
        logger.info(f"Received story text:\n{story_text}")
        logger.info(f"Mood: {mood}, Style: {artistic_style}")
        prompt_template = load_prompt_template(
            prompt_folder="prompts/story_generator",
            prompt_file="cot_structured_prompt.txt",
            input_variables=["story_text", "mood", "artistic_style", "word_limit"]
        )
        expansion_prompt = prompt_template.format(
            word_limit=STORY_EXPANSION_WORD_LIMIT,
            story_text=story_text,
            mood=mood,
            artistic_style=artistic_style
        )
        logger.info(f" Prompt is  : {expansion_prompt}")
        expanded_story = llm.generate_text(
            expansion_prompt, max_tokens=1000, temperature=0.8)
        logger.info(f"Expanded story generated successfully. {expanded_story}")
        story_text = expanded_story if isinstance(
            expanded_story, str) else str(expanded_story)
        return {
            "story_text": story_text,
            "character_description": character_descriptions,
            "artistic_style": artistic_style,
            "mood": mood,
            "layout_style": layout_style
        }
    except Exception as e:
        logger.error(f"Exception in story_generator: {e}")
        raise RuntimeError(f"story_generator failed: {e}")
