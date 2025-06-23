import logging
from typing import Dict, Any
from models.comic_generation_state import ComicGenerationState
from utils.response_util import sanitize_llm_response
from utils.llm_factory import get_model_client
from utils.load_prompts import load_prompt_template
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def story_analyst(state: ComicGenerationState, prompt_file: str = "hybrid_prompt.txt") -> Dict[str, Any]:
    """
    Analyzes the story and sets up initial style, mood, and character using LLM (via factory).
    Returns a dictionary with keys: character_descriptions, artistic_style, mood, layout_style.
    Raises RuntimeError on unrecoverable error.
    """
    logger.info("------ AGENT: Story Analyst --------")
    try:
        # Retrieve the story text from the state
        story_text = state.get('story_text', '')

        logger.info(f"Input Story Text: {story_text}")
        logger.info(f"Word Count of Story: {len(story_text.strip().split())}")

        # Check if story_text is empty or None
        if not story_text:
            logger.warning("No story_text found in state or story_text is empty.")
            raise RuntimeError("No story_text provided to story_analyst.")
        # Get style and mood presets from state if available
        artistic_style = state.get('style_preset', None)
        mood = state.get('genre_preset', None)
        logger.info(f"Using provided presets - Style: {artistic_style}, Mood: {mood}")

        # Load the analysis prompt from the specified file
        prompt_template = load_prompt_template(
            prompt_folder="prompts/story_analyst",
            prompt_file=prompt_file,
            input_variables=["story_text"]
        )
        analysis_prompt = prompt_template.format(story_text=story_text)
        logger.info(f"Analysis Prompt: {analysis_prompt}")
        analysis_prompt = analysis_prompt.strip()
        # Use the factory to get the LLM client (text)
        text_engine = state.get("text_engine", "mistral_mixtral_8x7b_instruct")
        llm = get_model_client("text", text_engine)
        logger.info("Submitting analysis prompt to the language model for story analysis...")
        # Use the LLM's generate_text method
        llm_response = llm.generate_text(analysis_prompt, max_tokens=1000, temperature=0.3)

        logger.info("LLM response received successfully.")
        llm_content = llm_response if isinstance(llm_response, str) else str(llm_response)
        logger.debug(f"LLM Response: {llm_content[:300]}...")
        try:
            # Parse the LLM response as JSON
            llm_content = sanitize_llm_response(llm_content)
            analysis = json.loads(llm_content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding failed: {e}")
            logger.info(f"LLM Response Content: {llm_content}")
            raise RuntimeError("LLM response was not valid JSON.")
        # Handle LLM analysis response
        if isinstance(analysis, dict):
            final_style = analysis.get('artistic_style') or artistic_style or 'Modern Comic Style'
            final_mood = analysis.get('mood') or mood or 'Adventure'
            character_descriptions = analysis.get('character_descriptions', [])
        else:
            raise RuntimeError("LLM analysis did not return a dict.")
        # If no character descriptions were found, use fallback extraction
        if not character_descriptions:
            character_descriptions = extract_fallback_character_descriptions(story_text)

        layout_style = state.get('layout_style', 'grid_2x2')  # Default layout style if not provided.
        layout_style = state.get('layout_style', 'grid_2x2')  # Default layout style if not provided.

        logger.info(f"Character Defined: {character_descriptions}")
        logger.info(f"Style set to: {final_style}")
        logger.info(f"Mood set to: {final_mood}")
        logger.info(f"Layout style set to: {layout_style}")

        # Return the final analysis result
        return {
            "character_descriptions": character_descriptions,
            "artistic_style": final_style,
            "mood": final_mood,
            "layout_style": layout_style
        }
    except Exception as e:
        # Log any exception in the main function and return fallback values
        logger.exception("Exception in story_analyst:")
        raise RuntimeError(f"story_analyst failed: {e}")

# Heuristic fallback for character extraction
def extract_fallback_character_descriptions(story_text):
    """
    Heuristically extracts possible character names from the story text if the LLM fails to provide character descriptions.
    Args:
        story_text (str): The story text from which to extract character names.
    Returns:
        list: A list of dictionaries, each containing 'name' and 'description' keys for each detected character.
    """
    # List of common capitalized words to ignore as character names
    common_words = {
        "The", "Once", "When", "He", "She", "It", "They", "His", "Her", "A", "An", "In", "On", "At",
        "And", "But", "Or", "If", "As", "By", "For", "With", "Of", "To", "From"
    }
    # Find all capitalized words not at the start of a sentence
    candidates = re.findall(r'(?<![.!?]\s)(?<!^)(\b[A-Z][a-z]+\b)', story_text)
    # Filter out common words
    character_names = [name for name in candidates if name not in common_words]
    if character_names:
        # Remove duplicates while preserving order
        seen = set()
        unique_names = []
        for name in character_names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)
        # Return a unique description for each character
        return [
            {
                "name": name,
                "description": f"{name} is a key character in the story. Their appearance and personality are important to the plot."
            }
            for name in unique_names
        ]
    else:
        # Fallback if no character names are found
        return [{"name": "Main character", "description": "Main character from the story"}]
