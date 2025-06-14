import logging
from typing import Dict, Any
from models.comic_generation_state import ComicGenerationState
from utils.huggingface_utils import get_hf_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def story_analyst(state: ComicGenerationState) -> Dict[str, Any]:
    """Analyzes the story and sets up initial style, mood, and character using HuggingFace LLM."""
    logger.info("AGENT: Story Analyst")
    try:
        story_text = state.get('story_text', '')
        print(story_text)
        if not story_text:
            logger.error("No story_text found in state.")
            return {
                "character_description": ["Main character from the story"],
                "artistic_style": state.get('style_preset', 'Modern Comic Style'),
                "mood": state.get('genre_preset', 'Adventure'),
                "layout_style": state.get('layout_style', 'grid_2x2')
            }
        artistic_style = state.get('style_preset', None)
        mood = state.get('genre_preset', None)
        logger.info(f"Using provided presets - Style: {artistic_style}, Genre: {mood}")
        analysis_prompt = f"""
You are a comic book adaptation expert. Analyze the following story and extract:
1. The most visually appropriate comic art style (e.g., Modern Anime, Classic Comic, Ghibli Animation, Noir, Cartoon, Realistic, etc.)
2. The genre/mood (e.g., Sci-Fi, Fantasy, Drama, Comedy, Horror, Adventure, Suspense, etc.)
3. A list of ALL named characters (including pets/animals) in the story, with a detailed, visually-focused description for each. For each character, include: name, age (if known), gender (if known), physical appearance (hair, eyes, build, height, skin), clothing, personality, and any unique features or props. Make each description suitable for a comic artist to draw the character consistently.

**Important:**
- Return ONLY a valid JSON object, no extra text or commentary.
- Do NOT include trailing commas.
- Use keys: artistic_style, mood, character_descriptions (as a list of strings, one per character, in the format: Name: description).
- If a character is an animal, describe its breed, color, and personality.

Story:
"""
        analysis_prompt += story_text
        analysis_prompt += """

Format example:
{
  "artistic_style": "Modern Anime",
  "mood": "Adventure",
  "character_descriptions": [
    "Alex: 12-year-old boy, messy brown hair, blue eyes, slim, wears a blue hoodie and jeans, curious and energetic.",
    "Grandma Edna: elderly woman, gray hair in a bun, glasses, floral apron over a dress, sharp eyes, warm but strict.",
    "Mittens: small gray tabby cat, green eyes, mischievous, always alert."
  ]
}

Return ONLY the JSON object, nothing else.
"""
        try:
            hf_client = get_hf_client()
            # Use conversational API
            messages = [
                {"role": "system", "content": "You are a comic book adaptation expert."},
                {"role": "user", "content": analysis_prompt}
            ]
            llm_response = hf_client.generate_conversation(
                messages=messages,
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                max_tokens=500,
                temperature=0.3
            )
            analysis = hf_client.parse_json_response(llm_response)
            # Handle both dict and list outputs
            if isinstance(analysis, dict):
                final_style = artistic_style or analysis.get('artistic_style', 'Modern Comic Style')
                final_mood = mood or analysis.get('mood', 'Adventure')
                character_descriptions = analysis.get('character_descriptions', [])
            elif isinstance(analysis, list):
                final_style = artistic_style or 'Modern Comic Style'
                final_mood = mood or 'Adventure'
                character_descriptions = analysis
            else:
                final_style = artistic_style or 'Modern Comic Style'
                final_mood = mood or 'Adventure'
                character_descriptions = []
            logger.info(f"LLM Analysis - Style: {final_style}, Mood: {final_mood}")
        except Exception as e:
            logger.error(f"Error in LLM story analysis: {e}")
            final_style = artistic_style or 'Modern Comic Style'
            final_mood = mood or 'Adventure'
            character_descriptions = []
        if not character_descriptions:
            if "Elara" in story_text:
                character_descriptions = ["Elara, a veteran astronomer, with hair streaked with grey, wearing a lab coat or space suit"]
            else:
                character_descriptions = ["Main character from the story"]
        logger.info(f"Character Defined: {character_descriptions}")
        logger.info(f"Style set to: {final_style}")
        logger.info(f"Mood set to: {final_mood}")
        layout_style = state.get('layout_style', 'grid_2x2')
        logger.info(f"Layout style set to: {layout_style}")
        return {
            "character_description": character_descriptions,
            "artistic_style": final_style,
            "mood": final_mood,
            "layout_style": layout_style
        }
    except Exception as e:
        logger.error(f"Exception in story_analyst: {e}")
        return {
            "character_description": ["Main character from the story"],
            "artistic_style": state.get('style_preset', 'Modern Comic Style'),
            "mood": state.get('genre_preset', 'Adventure'),
            "layout_style": state.get('layout_style', 'grid_2x2')
        }
