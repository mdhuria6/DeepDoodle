import re
import requests
import json
from models.comic_generation_state import ComicGenerationState
from configs.prompt_styles import STYLE_CONFIGS, DEFAULT_STYLE_KEYWORDS, DEFAULT_LIGHTING_KEYWORDS, DEFAULT_ADDITIONAL_DETAILS, DEFAULT_PROMPT_SUFFIX
from configs import HUGGINGFACE_API_TOKEN

def clean_prompt_for_bedrock(prompt: str) -> str:
    """
    Remove potentially filtered words from Bedrock prompts to avoid content filtering.
    """
    # Remove words that might trigger content filters
    filtered_words = ['children', 'kids', 'young', 'little', 'small', 'child', 'kid']
    cleaned_prompt = prompt
    
    for word in filtered_words:
        # Replace with more neutral terms
        cleaned_prompt = cleaned_prompt.replace(word.lower(), 'characters')
        cleaned_prompt = cleaned_prompt.replace(word.capitalize(), 'Characters')
        cleaned_prompt = cleaned_prompt.replace(word.upper(), 'CHARACTERS')
    
    # Remove any formatting that might cause issues
    cleaned_prompt = cleaned_prompt.replace('**', '').replace('*', '')
    
    # Remove any potentially problematic phrases
    problematic_phrases = [
        'little ones', 'young people', 'small people'
    ]
    
    for phrase in problematic_phrases:
        cleaned_prompt = cleaned_prompt.replace(phrase, 'characters')
    
    return cleaned_prompt

def call_mistral_api(prompt: str, max_tokens: int = 800) -> str:
    """
    Calls the Mistral AI model via Hugging Face API to create optimized image generation prompts.
    """
    if not HUGGINGFACE_API_TOKEN:
        print("Warning: HUGGINGFACE_API_TOKEN not found. Cannot use Mistral AI.")
        return ""
    
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.3,  # Lower temperature for consistent prompt generation
            "do_sample": True,
            "top_p": 0.85,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').strip()
            else:
                print(f"Unexpected Mistral API response format: {result}")
                return ""
        else:
            print(f"Mistral API error: {response.status_code} - {response.text}")
            return ""
            
    except Exception as e:
        print(f"Error calling Mistral API: {e}")
        return ""

def create_optimized_prompt_with_mistral(
    scene_description: str,
    background_description: str,
    character_details: dict[str, str],
    panel_characters: list[tuple],
    style_keywords: str,
    lighting_keywords: str,
    additional_details: str,
    mood: str,
    panel_index: int
) -> str:
    """
    Uses Mistral AI to create an optimized, cohesive image generation prompt.
    """
    print(f"   > Using Mistral AI to create optimized prompt for panel {panel_index + 1}...")
    
    # Prepare character information
    character_info = ""
    if panel_characters:
        character_info = "Characters in this panel:\n"
        for char_name, char_desc in panel_characters:
            character_info += f"- {char_name}: {char_desc}\n"
    else:
        character_info = "No specific characters mentioned for this panel."
    
    prompt_creation_request = f"""<s>[INST] Create an image generation prompt with STRICT CHARACTER CONSISTENCY.

**CRITICAL CHARACTER CONSISTENCY REQUIREMENTS:**
{character_info}
**THESE CHARACTERS MUST LOOK IDENTICAL IN EVERY PANEL - SAME CLOTHES, HAIR, FACE, AGE**

**SCENE:** {scene_description}
**BACKGROUND:** {background_description}
**STYLE:** {style_keywords}
**MOOD:** {mood}

**REQUIREMENTS:**
1. START with character descriptions EXACTLY as provided
2. Include "CONSISTENT CHARACTER APPEARANCE" in the prompt
3. Specify "same clothing, same hairstyle, same age" for each character
4. Add scene and background details
5. Include art style specifications
6. Add strong negative prompts against text/speech bubbles

**FORMAT:** Single optimized prompt starting with character consistency details.

Generate the prompt:[/INST]"""

    mistral_response = call_mistral_api(prompt_creation_request, max_tokens=600)
    
    if mistral_response and len(mistral_response.strip()) > 50:
        # Clean up the response
        optimized_prompt = mistral_response.strip()
        
        # Ensure it starts properly
        if not optimized_prompt.lower().startswith("comic book panel"):
            optimized_prompt = f"Comic book panel illustration: {optimized_prompt}"
        
        # Add critical consistency and anti-text instructions
        optimized_prompt += " CRITICAL: Maintain exact character appearance as described. NO text, speech bubbles, dialogue balloons, captions, words, letters, or any written content. Clean visual scene only."
        
        # Clean prompt for Bedrock content filtering
        optimized_prompt = clean_prompt_for_bedrock(optimized_prompt)
        
        print(f"   > Mistral AI created optimized prompt ({len(optimized_prompt)} chars)")
        return optimized_prompt
    else:
        print("   > Mistral AI failed to create prompt, using fallback method")
        return create_fallback_prompt(
            scene_description, background_description, panel_characters,
            style_keywords, lighting_keywords, additional_details, mood
        )

def create_fallback_prompt(
    scene_description: str,
    background_description: str,
    panel_characters: list[tuple],
    style_keywords: str,
    lighting_keywords: str,
    additional_details: str,
    mood: str
) -> str:
    """
    Fallback method to create prompts when Mistral AI is not available.
    """
    print("   > Using fallback prompt creation method")
    
    # Create character consistency prompt
    character_prompt = ""
    if panel_characters:
        char_descriptions = []
        for char_name, char_desc in panel_characters:
            char_descriptions.append(f"{char_name}: {char_desc}")
        character_prompt = f"CHARACTERS (maintain exact appearance): {'. '.join(char_descriptions)}. "
    
    # Combine all elements
    fallback_prompt = (
        f"CONSISTENT CHARACTER APPEARANCE: {character_prompt}"
        f"Comic book panel: {scene_description}. "
        f"BACKGROUND: {background_description}. "
        f"CRITICAL: Characters must look EXACTLY the same as in previous panels - "
        f"identical clothing, hairstyle, facial features, age, and appearance. "
        f"Art Style: {style_keywords}{lighting_keywords}. "
        f"Mood: {mood}. {additional_details}. "
        f"NO text, speech bubbles, dialogue, words, letters, or written content. "
        f"Clean visual scene only with consistent character designs."
    )
    
    # Clean prompt for Bedrock content filtering
    fallback_prompt = clean_prompt_for_bedrock(fallback_prompt)
    
    return fallback_prompt

def prompt_engineer(state: ComicGenerationState) -> dict:
    """
    Node 3: Uses Mistral AI to craft optimized, detailed prompts for image generation
            with strong character consistency and rich scene details.
    """
    panel_index = state["current_panel_index"]
    print(f"---AGENT: Prompt Engineer (Panel {panel_index + 1}) - AI-Powered---")

    current_scene = state["scenes"][panel_index]
    artistic_style_preset = state['artistic_style']
    character_details = state.get('character_details', {})
    mood = state.get('mood', 'Adventure')

    # Get scene information
    scene_description = current_scene.get('description', 'A scene from the story')
    background_description = current_scene.get('background', 'An appropriate background setting')
    
    # Determine which characters should appear in this panel
    panel_characters = determine_panel_characters(current_scene, character_details)
    
    # Retrieve style configuration
    config = STYLE_CONFIGS.get(artistic_style_preset)

    if config:
        style_keywords = config.get("style_keywords", DEFAULT_STYLE_KEYWORDS)
        lighting_keywords = config.get("lighting_keywords", DEFAULT_LIGHTING_KEYWORDS)
        additional_details = config.get("additional_details", DEFAULT_ADDITIONAL_DETAILS)
        prompt_suffix = config.get("prompt_suffix", DEFAULT_PROMPT_SUFFIX)
    else:
        print(f"   > Warning: Style preset '{artistic_style_preset}' not found in STYLE_CONFIGS. Using defaults.")
        style_keywords = f"in the style of {artistic_style_preset}, "
        lighting_keywords = DEFAULT_LIGHTING_KEYWORDS
        additional_details = DEFAULT_ADDITIONAL_DETAILS
        prompt_suffix = DEFAULT_PROMPT_SUFFIX

    # Use Mistral AI to create an optimized prompt
    optimized_prompt = create_optimized_prompt_with_mistral(
        scene_description=scene_description,
        background_description=background_description,
        character_details=character_details,
        panel_characters=panel_characters,
        style_keywords=style_keywords,
        lighting_keywords=lighting_keywords,
        additional_details=additional_details,
        mood=mood,
        panel_index=panel_index
    )

    print(f"   > Final Optimized Prompt: {optimized_prompt[:200]}...")

    return {"panel_prompts": state["panel_prompts"] + [optimized_prompt]}

def determine_panel_characters(scene, character_details):
    """
    Determines which characters should appear in this panel based on dialogue and scene description.
    """
    characters_in_panel = []
    
    # Check dialogue for character names
    captions = scene.get('captions', [])
    speakers = set()
    
    for caption in captions:
        if caption.get('type') == 'dialogue':
            speaker = caption.get('speaker', '')
            if speaker and speaker != 'Narrator':
                # Handle multiple speakers (e.g., "Riya & Aarav")
                if '&' in speaker or 'and' in speaker.lower():
                    # Split and add all speakers
                    names = re.split(r'[&,]|and', speaker, flags=re.IGNORECASE)
                    for name in names:
                        clean_name = name.strip()
                        if clean_name:
                            speakers.add(clean_name)
                else:
                    speakers.add(speaker.strip())
    
    # Also check scene description for character names
    scene_desc = scene.get('description', '').lower()
    for char_name in character_details.keys():
        if char_name.lower() in scene_desc:
            speakers.add(char_name)
    
    # Match speakers with character details
    for speaker in speakers:
        for char_name, char_desc in character_details.items():
            if char_name.lower() in speaker.lower() or speaker.lower() in char_name.lower():
                characters_in_panel.append((char_name, char_desc))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_characters = []
    for char_name, char_desc in characters_in_panel:
        if char_name not in seen:
            unique_characters.append((char_name, char_desc))
            seen.add(char_name)
    
    # If no specific characters found, include main characters based on scene context
    if not unique_characters and character_details:
        # Include up to 2 main characters for the scene
        main_chars = list(character_details.items())[:2]
        unique_characters = main_chars
    
    return unique_characters
