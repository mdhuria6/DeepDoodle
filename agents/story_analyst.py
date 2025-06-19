import logging
from typing import Dict, Any
from models.comic_generation_state import ComicGenerationState
from utils.huggingface_utils import get_hf_client
import json
import re

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def story_analyst(state: ComicGenerationState) -> Dict[str, Any]:
    """
    Analyzes the story and sets up initial style, mood, and character using HuggingFace LLM.
    Returns a dictionary with keys: character_descriptions, artistic_style, mood, layout_style.
    """
    logger.info("------ AGENT: Story Analyst --------")
    try:
        # Retrieve the story text from the state
        story_text = state.get('story_text', '')

        logger.info(f"Input Story Text: {story_text}")
        logger.info(f"Input Story Text Length: {len(story_text)}")

        ##############################################################################
        # Check if story_text is empty or None
        if not story_text:
            logger.warning("No story_text found in state or story_text is empty.")
            # Return fallback values if no story text is provided
            return {
                "character_descriptions": [{"name": "Main character", "description": "Main character from the story"}],
                "artistic_style": state.get('style_preset', 'Modern Comic Style'),
                "mood": state.get('genre_preset', 'Adventure'),
                "layout_style": state.get('layout_style', 'grid_2x2')
            }
        # Get style and mood presets from state if available
        artistic_style = state.get('style_preset', None)
        mood = state.get('genre_preset', None)
        logger.info(f"Using provided presets - Style: {artistic_style}, Mood: {mood}")

        ################################################################################
        # Build the prompt for the LLM to analyze the story
        analysis_prompt = f"""
        You are an expert in comic book adaptation and visual storytelling. Analyze the narrative provided below and extract the following information in a format suitable for a visual design pipeline:

        1. **Artistic Style**: Identify the most visually appropriate comic art style (e.g., Modern Anime, Classic Comic, Ghibli Animation, Noir, Cartoon, Realistic, etc.) that aligns with the story’s tone and themes.
        2. **Genre/Mood**: Determine the dominant genre or emotional tone of the story (e.g., Sci-Fi, Fantasy, Drama, Comedy, Horror, Adventure, Suspense, etc.).
        3. **Character Descriptions**: Extract all named characters (including pets and animals). For each, provide a detailed visual description sufficient for consistent illustration, including:
        - Name
        - Age (if available)
        - Gender (if available)
        - Physical appearance (hair, eyes, build, height, skin tone)
        - Clothing
        - Personality traits
        - Distinctive features or props

        If the character is an animal, include breed, color, and behavioral traits.

        **Output Format Requirements**:
        - Return the output strictly as a **valid JSON object**, with no additional text.
        - The JSON must contain the following keys:
        - `"artistic_style"`: A string indicating the recommended visual style.
        - `"mood"`: A string indicating the genre or emotional tone.
        - `"character_descriptions"`: A list of dictionaries, each containing:
            - `"name"`: The character’s name.
            - `"description"`: A detailed, visually focused character description.

        - Ensure **no trailing commas** in the JSON output.

        **Input Story**:
        {story_text}

        **Example Output**:
        {{
        "artistic_style": "Modern Anime",
        "mood": "Adventure",
        "character_descriptions": [
            {{
            "name": "Alex",
            "description": "12-year-old boy with messy brown hair, blue eyes, slim build, wears a blue hoodie and jeans, curious and energetic."
            }},
            {{
            "name": "Grandma Edna",
            "description": "Elderly woman with gray hair in a bun, glasses, floral apron over a dress, sharp eyes, warm but strict demeanor."
            }},
            {{
            "name": "Mittens",
            "description": "Small gray tabby cat with green eyes, mischievous and agile, always alert."
            }}
        ]
        }}

        Return **only** the JSON object shown above. No additional commentary or formatting.
        """
        logger.info("Submitting analysis prompt to the language model for story analysis...")
        
        ################################################################################
        analysis_prompt = analysis_prompt.strip()
        try:
            # Get the HuggingFace client
            hf_client = get_hf_client()
            # Prepare the conversation for the LLM
            messages = [
                {"role": "system", "content": "You are an expert in comic book adaptation and visual storytelling."},
                {"role": "user", "content": analysis_prompt}
            ]
            # Generate the LLM response
            llm_response = hf_client.generate_conversation(
                messages=messages,
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                max_tokens=800,
                temperature=0.3
            )

            logger.info("LLM response received successfully.")
            # Extract the content string from the ChatCompletionOutput object
            if hasattr(llm_response, "choices"):
                llm_content = llm_response.choices[0].message.content
            else:
                llm_content = llm_response  # fallback if already a string

            logger.debug(f"LLM Response: {llm_content[:300]}...")  # Log only the first 300 characters for brevity
            try:
                # Parse the LLM response as JSON
                analysis = json.loads(llm_content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decoding failed: {e}")
                analysis = {}
            # Handle LLM analysis response
            if isinstance(analysis, dict):
                final_style = analysis.get('artistic_style') or artistic_style or 'Modern Comic Style'
                final_mood = analysis.get('mood') or mood or 'Adventure'
                character_descriptions = analysis.get('character_descriptions', [])
            else:
                final_style = artistic_style or 'Modern Comic Style'
                final_mood = mood or 'Adventure'
                character_descriptions = []
            logger.info(f"LLM Analysis - Style: {final_style}, Mood: {final_mood}")
        except Exception as e:
            # Log any exception during LLM analysis
            logger.exception(f"Error in LLM story analysis: {e}")
            final_style = artistic_style or 'Modern Comic Style'
            final_mood = mood or 'Adventure'
            character_descriptions = []
        # If no character descriptions were found, use fallback extraction
        if not character_descriptions:
            character_descriptions = extract_fallback_character_descriptions(story_text)

        layout_style = state.get('layout_style', 'grid_2x2') # Default layout style if not provided

        logger.info(f"Character Defined: {character_descriptions}")
        logger.info(f"Style set to: {final_style}")
        logger.info(f"Mood set to: {final_mood}")
        logger.info(f"Layout style set to: {layout_style}")

        ################################################################################
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
        return {
            "character_descriptions": [{"name": "Main character", "description": "Main character from the story"}],
            "artistic_style": state.get('style_preset', 'Modern Comic Style'),
            "mood": state.get('genre_preset', 'Adventure'),
            "layout_style": state.get('layout_style', 'grid_2x2')
        }

########################################################################
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
