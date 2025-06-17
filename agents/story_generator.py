import logging
from typing import Dict, Any
from models.comic_generation_state import ComicGenerationState
from utils.huggingface_utils import get_hf_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def story_generator(state: ComicGenerationState) -> Dict[str, Any]:
    """Generates or analyzes a story from a short user prompt, genre, and style."""
    logger.info("AGENT: Story Generator")
    try:
        story_text = state.get('story_text', '')
        artistic_style = state.get('style_preset')
        mood = state.get('genre_preset')
        layout_style = state.get('layout_style')
        character_descriptions = state.get('character_description')

        logger.info(f"Received story text:\n{story_text}")
        logger.info(f"Mood: {mood}, Style: {artistic_style}")
        logger.info("Story text is short, expanding into full story...")
        hf_client = get_hf_client()
        expansion_prompt = f"""
Expand the following idea into a short story of 300 words.
Incorporate the given genre and style into the story tone.

Story: {story_text}
Genre: {mood}
Style: {artistic_style}

Write the full story:
"""
        messages = [
                {"role": "system", "content": "You are a creative comic writer."},
                {"role": "user", "content": expansion_prompt}
            ]
        logger.info(f" Prompt is  : {expansion_prompt}")
        expanded_story = hf_client.generate_conversation(
        messages=messages,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=600,
        temperature=0.8
        )
        logger.info(f"Expanded story generated successfully. {expanded_story}")
        story_text = expanded_story
        return {
            "story_text": story_text,
            "character_description": character_descriptions,
            "artistic_style": artistic_style,
            "mood": mood,
            "layout_style": layout_style
        }

    except Exception as e:
        logger.error(f"Exception in story_generator: {e}")
        return {
            "story_text": story_text,
            "character_description": ["Main character from the story"],
            "artistic_style": artistic_style,
            "mood": mood,
            "layout_style": layout_style
        }
