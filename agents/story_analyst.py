import requests
import json
import re
from typing import Dict, List
from models.comic_generation_state import ComicGenerationState
from configs import HUGGINGFACE_API_TOKEN

def call_mistral_api(prompt: str, max_tokens: int = 1000) -> str:
    """
    Calls the Mistral AI model via Hugging Face API to extract information from text.
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
            "temperature": 0.1,  # Lower temperature for more consistent character extraction
            "do_sample": True,
            "top_p": 0.8,
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

def extract_characters_with_mistral(story_text: str) -> Dict[str, str]:
    """
    Uses Mistral AI to extract EXTREMELY detailed character information with explicit gender
    and appearance details for absolute visual consistency across all panels.
    """
    print("   > Using Mistral AI to extract detailed character information with gender specifics...")
    
    character_extraction_prompt = f"""<s>[INST] You are a character design expert for comic books. Your task is to extract EXTREMELY DETAILED visual descriptions of ALL characters mentioned in this story. Focus on creating consistent character designs that will look the same in every comic panel.

For each character, provide:
1. **Name**: The character's name
2. **Gender**: EXPLICITLY state Male/Female/Other - this is CRITICAL
3. **Age**: Specific age or age range
4. **Physical Features**:
   - Hair: Exact color, length, style (e.g., "shoulder-length brown hair in a ponytail")
   - Eyes: Color and shape
   - Skin tone: Specific description
   - Height/Build: Tall, short, slim, etc.
   - Facial features: Any distinctive features
5. **Clothing**: EXACT outfit description that will remain consistent
   - Top: Color, style, details
   - Bottom: Color, style, details  
   - Shoes: Type and color
   - Accessories: Any jewelry, hats, bags, etc.
6. **Distinctive Features**: Anything that makes them unique

**CRITICAL REQUIREMENTS:**
- EXPLICITLY state gender (Male/Female/Other) for each character
- Be EXTREMELY specific about clothing colors and styles
- Describe hairstyles in detail (length, color, how it's worn)
- Include age-appropriate features
- Make descriptions detailed enough for an artist to draw the same character repeatedly
- If multiple characters exist, make them visually distinct
- Focus on visual elements that will be consistent across all panels
- Add "CONSISTENCY CRITICAL:" at the start of each description

**Example Format:**
{{
    "Riya": "CONSISTENCY CRITICAL: Riya is FEMALE, 7-year-old girl with shoulder-length curly black hair tied in two small pigtails with red ribbons. She has large brown eyes, light brown skin, and a cheerful round face. She wears a bright yellow t-shirt with a small flower pattern, blue denim overalls with silver buckles, white sneakers with pink laces, and carries a small green backpack. She is petite for her age with a energetic, curious expression.",
    "Aarav": "CONSISTENCY CRITICAL: Aarav is MALE, 8-year-old boy with short straight black hair neatly combed to the side. He has dark brown eyes, light brown skin, and a serious but kind face. He wears a light blue collared shirt with short sleeves, dark blue shorts that reach his knees, brown leather sandals, and a digital watch on his left wrist. He is slightly taller than average for his age with a thoughtful expression."
}}

**Story to analyze:**
{story_text}

Provide ONLY the JSON response with extremely detailed character descriptions, no additional text.[/INST]"""

    mistral_response = call_mistral_api(character_extraction_prompt, max_tokens=2500)
    
    if not mistral_response:
        print("   > Mistral AI failed, using fallback character extraction")
        return extract_characters_fallback(story_text)
    
    try:
        # Try to parse the JSON response
        json_start = mistral_response.find('{')
        json_end = mistral_response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = mistral_response[json_start:json_end]
            characters = json.loads(json_str)
            
            if isinstance(characters, dict) and characters:
                print(f"   > Successfully extracted {len(characters)} characters with detailed descriptions")
                
                # Validate and enhance character descriptions
                enhanced_characters = {}
                for name, desc in characters.items():
                    # Ensure gender is explicitly mentioned
                    if "MALE" not in desc.upper() and "FEMALE" not in desc.upper():
                        # Try to infer gender from pronouns
                        if "he " in desc.lower() or "his " in desc.lower() or "him " in desc.lower():
                            gender = "MALE"
                        elif "she " in desc.lower() or "her " in desc.lower():
                            gender = "FEMALE"
                        else:
                            gender = "UNSPECIFIED"
                        
                        # Add gender explicitly
                        if "CONSISTENCY CRITICAL:" in desc:
                            desc = desc.replace("CONSISTENCY CRITICAL:", f"CONSISTENCY CRITICAL: {name} is {gender},")
                        else:
                            desc = f"CONSISTENCY CRITICAL: {name} is {gender}, " + desc
                    
                    # Add panel consistency reminder
                    if "MUST APPEAR IDENTICAL IN ALL PANELS" not in desc.upper():
                        desc += " MUST APPEAR IDENTICAL IN ALL PANELS."
                    
                    enhanced_characters[name] = desc
                    print(f"     - {name}: {desc[:100]}...")
                
                return enhanced_characters
            else:
                print("   > Mistral returned empty or invalid character data")
                return extract_characters_fallback(story_text)
        else:
            print("   > Could not find valid JSON in Mistral response")
            return extract_characters_fallback(story_text)
            
    except json.JSONDecodeError as e:
        print(f"   > Error parsing Mistral JSON response: {e}")
        print(f"   > Raw response: {mistral_response[:200]}...")
        return extract_characters_fallback(story_text)

def extract_characters_fallback(story_text: str) -> Dict[str, str]:
    """
    Enhanced fallback method with more detailed character descriptions including explicit gender.
    """
    print("   > Using enhanced fallback character extraction method with gender specifics")
    characters = {}
    
    # Look for common names and create detailed descriptions
    common_names = ['Riya', 'Aarav', 'Maya', 'Arjun', 'Priya', 'Rohan', 'Ananya', 'Karan']
    story_lower = story_text.lower()
    
    found_names = []
    for name in common_names:
        if name.lower() in story_lower:
            found_names.append(name)
    
    # If no common names found, extract from dialogue patterns
    if not found_names:
        dialogue_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):\s*["\']'
        names = re.findall(dialogue_pattern, story_text)
        exclude_words = {'Scene', 'Narration', 'Narrator', 'Title', 'Panel'}
        found_names = [name for name in names if name not in exclude_words]
    
    # Create detailed character descriptions with explicit gender
    if len(found_names) >= 2:
        # Two main characters
        characters[found_names[0]] = f"CONSISTENCY CRITICAL: {found_names[0]} is FEMALE, 7-year-old girl with shoulder-length curly black hair in pigtails with colorful ribbons. She has bright brown eyes, warm brown skin, and wears a cheerful yellow t-shirt, blue denim overalls, and white sneakers. She carries a small colorful backpack and has an energetic, curious personality. MUST APPEAR IDENTICAL IN ALL PANELS."
        characters[found_names[1]] = f"CONSISTENCY CRITICAL: {found_names[1]} is MALE, 8-year-old boy with short neat black hair combed to the side. He has dark brown eyes, light brown skin, and wears a light blue collared shirt, dark blue shorts, and brown sandals. He wears a simple digital watch and has a thoughtful, kind expression. MUST APPEAR IDENTICAL IN ALL PANELS."
    elif len(found_names) == 1:
        # Single main character - try to infer gender from pronouns
        gender = "UNSPECIFIED"
        if "he " in story_lower or "his " in story_lower or "him " in story_lower:
            gender = "MALE"
        elif "she " in story_lower or "her " in story_lower:
            gender = "FEMALE"
        
        characters[found_names[0]] = f"CONSISTENCY CRITICAL: {found_names[0]} is {gender}, young child with distinctive features including neat dark hair, bright eyes, and colorful casual clothing that remains consistent throughout the story. They have an expressive face and energetic personality. MUST APPEAR IDENTICAL IN ALL PANELS."
    else:
        # Generic characters
        characters["MainCharacter"] = "CONSISTENCY CRITICAL: MainCharacter is UNSPECIFIED, young child with distinctive dark hair, bright eyes, and consistent casual clothing including a colorful shirt and comfortable pants. They maintain the same appearance throughout the entire story. MUST APPEAR IDENTICAL IN ALL PANELS."
    
    # Check for fairy or magical characters
    if "fairy" in story_lower or "magical being" in story_lower or "sprite" in story_lower:
        characters["The Fairy"] = "CONSISTENCY CRITICAL: The Fairy is FEMALE, a tiny magical being with delicate translucent wings that shimmer with rainbow colors. She has long flowing silver hair that sparkles, bright emerald green eyes, and luminescent pale skin. She wears a flowing dress made of flower petals in shades of pink and purple, and carries a golden wand with a star tip. She has a graceful, ethereal appearance and a kind expression. MUST APPEAR IDENTICAL IN ALL PANELS."
    
    return characters

def detect_mood_with_mistral(story_text: str, genre_preset: str) -> str:
    """
    Uses Mistral AI to detect the mood/genre of the story.
    """
    # If user already specified a mood, use it
    if genre_preset and genre_preset != "auto":
        print(f"   > Using user-specified mood: {genre_preset}")
        return genre_preset
    
    print("   > Using Mistral AI to detect story mood...")
    
    mood_detection_prompt = f"""<s>[INST] You are a story analysis expert. Analyze the following story and determine its primary mood/genre.

Choose ONE of the following moods that best fits the story:
- Fantasy (magical elements, wizards, fairies, enchanted worlds)
- Sci-Fi (space, technology, robots, future, aliens)
- Adventure (journeys, quests, exploration, exciting action)
- Comedy (funny, humorous, lighthearted, silly)
- Horror (scary, dark, monsters, fear, suspense)
- Mystery (puzzles, clues, detective work, secrets)
- Whimsical (playful, childlike, innocent, colorful)
- Drama (emotional, serious, realistic, character-driven)
- Romance (love, relationships, emotional connections)

Respond with ONLY the mood name, nothing else.

Story to analyze:
{story_text}[/INST]"""

    mistral_response = call_mistral_api(mood_detection_prompt, max_tokens=50)
    
    if mistral_response:
        # Clean up the response and check if it's a valid mood
        detected_mood = mistral_response.strip().title()
        valid_moods = ["Fantasy", "Sci-Fi", "Adventure", "Comedy", "Horror", "Mystery", "Whimsical", "Drama", "Romance"]
        
        if detected_mood in valid_moods:
            print(f"   > Mistral AI detected mood: {detected_mood}")
            return detected_mood
        else:
            print(f"   > Mistral returned invalid mood '{detected_mood}', using fallback")
    
    # Fallback mood detection
    return detect_mood_fallback(story_text)

def detect_mood_fallback(story_text: str) -> str:
    """
    Fallback method to detect mood when Mistral AI is not available.
    """
    print("   > Using fallback mood detection")
    story_lower = story_text.lower()
    
    # Keyword-based mood detection
    if any(word in story_lower for word in ['magic', 'fairy', 'wizard', 'enchant', 'spell', 'magical']):
        return "Fantasy"
    elif any(word in story_lower for word in ['space', 'robot', 'future', 'alien', 'technology', 'spaceship']):
        return "Sci-Fi"
    elif any(word in story_lower for word in ['funny', 'laugh', 'joke', 'silly', 'giggle', 'humor']):
        return "Comedy"
    elif any(word in story_lower for word in ['scary', 'ghost', 'monster', 'fear', 'dark', 'horror']):
        return "Horror"
    elif any(word in story_lower for word in ['mystery', 'clue', 'detective', 'solve', 'secret', 'investigate']):
        return "Mystery"
    elif any(word in story_lower for word in ['adventure', 'journey', 'explore', 'quest', 'travel', 'expedition']):
        return "Adventure"
    elif any(word in story_lower for word in ['garden', 'flower', 'butterfly', 'children', 'play', 'colorful']):
        return "Whimsical"
    else:
        return "Drama"

def validate_character_consistency(character_details: Dict[str, str]) -> Dict[str, str]:
    """
    Validates and enhances character descriptions to ensure absolute consistency across panels.
    """
    print("   > Validating character consistency for image generation...")
    
    validated_characters = {}
    
    for name, description in character_details.items():
        enhanced_desc = description
        
        # Ensure consistency markers are present
        if "CONSISTENCY CRITICAL" not in enhanced_desc:
            enhanced_desc = f"CONSISTENCY CRITICAL: {enhanced_desc}"
        
        # Ensure gender is explicitly mentioned
        if "MALE" not in enhanced_desc.upper() and "FEMALE" not in enhanced_desc.upper():
            # Try to infer gender from pronouns in the description
            if "he " in enhanced_desc.lower() or "his " in enhanced_desc.lower() or "him " in enhanced_desc.lower():
                gender = "MALE"
            elif "she " in enhanced_desc.lower() or "her " in enhanced_desc.lower():
                gender = "FEMALE"
            else:
                gender = "UNSPECIFIED"
            
            # Add gender explicitly
            if "CONSISTENCY CRITICAL:" in enhanced_desc:
                enhanced_desc = enhanced_desc.replace("CONSISTENCY CRITICAL:", f"CONSISTENCY CRITICAL: {name} is {gender},")
            else:
                enhanced_desc = f"CONSISTENCY CRITICAL: {name} is {gender}, " + enhanced_desc
        
        # Ensure panel consistency reminder
        if "MUST APPEAR IDENTICAL IN ALL PANELS" not in enhanced_desc.upper():
            enhanced_desc += " MUST APPEAR IDENTICAL IN ALL PANELS."
        
        # Add visual consistency emphasis
        if "SAME EXACT APPEARANCE" not in enhanced_desc.upper():
            enhanced_desc += " Character MUST maintain the SAME EXACT APPEARANCE in every panel (same clothes, hair, colors, etc)."
        
        validated_characters[name] = enhanced_desc
    
    return validated_characters

def story_analyst(state: ComicGenerationState) -> dict:
    """
    Analyzes the story using Mistral AI to extract detailed character information with
    explicit gender identification and strict visual consistency enforcement.
    """
    print("---AGENT: Story Analyst (Enhanced Character Consistency with Gender)---")

    story_text = state.get('story_text', '').strip()
    
    if not story_text:
        print("   > No story text provided. Using default placeholder.")
        story_text = "A simple story about adventure and discovery."
    
    print(f"   > Analyzing story for character consistency and gender: {story_text[:100]}...")
    
    # Extract characters with extreme detail for visual consistency
    character_details = extract_characters_with_mistral(story_text)
    
    # Validate and enhance character descriptions for absolute consistency
    character_details = validate_character_consistency(character_details)
    
    # Create a comprehensive character description for consistency
    character_descriptions = []
    for name, desc in character_details.items():
        character_descriptions.append(f"CRITICAL VISUAL CONSISTENCY: {name} MUST ALWAYS appear exactly as: {desc}")
        print(f"   > {name}: {desc[:150]}...")
    
    # Combine all character descriptions with emphasis on consistency
    full_character_description = " ".join(character_descriptions) if character_descriptions else "Main characters from the story"
    
    # Add global consistency reminder
    full_character_description = "ABSOLUTE VISUAL CONSISTENCY REQUIRED ACROSS ALL PANELS. " + full_character_description
    
    # Detect mood using Mistral AI
    genre_preset = state.get('genre_preset', 'auto')
    mood = detect_mood_with_mistral(story_text, genre_preset)
    
    # Pass through the style from input
    artistic_style = state.get('style_preset', 'Simple Line Art Comic')
    layout_style = state.get('layout_style', 'grid_2x2')

    print(f"   > Final mood: {mood}")
    print(f"   > Style set to: {artistic_style}")
    print(f"   > Layout style set to: {layout_style}")
    print(f"   > Total characters extracted: {len(character_details)}")
    print(f"   > CHARACTER CONSISTENCY EMPHASIS: All characters must maintain exact same appearance across ALL panels")
    print(f"   > GENDER IDENTIFICATION: All characters have explicit gender markers")

    # Return all the necessary keys for the downstream nodes
    return {
        "character_description": full_character_description,
        "character_details": character_details,  # Store individual character details with gender
        "artistic_style": artistic_style,
        "mood": mood,
        "layout_style": layout_style
    }
