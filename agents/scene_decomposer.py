import requests
import json
import re
from typing import List, Dict
from models.comic_generation_state import ComicGenerationState
from configs import HUGGINGFACE_API_TOKEN

def call_mistral_api(prompt: str, max_tokens: int = 2000) -> str:
    """
    Calls the Mistral AI model via Hugging Face API to decompose story into scenes.
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
            "temperature": 0.2,  # Lower temperature for consistent scene breakdown
            "do_sample": True,
            "top_p": 0.85,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        
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

def decompose_story_with_mistral(story_text: str, panel_count: int, character_details: Dict[str, str]) -> List[Dict]:
    """
    Uses Mistral AI to create HIGHLY DETAILED scenes with rich backgrounds, character actions, and story context.
    """
    print(f"   > Using Mistral AI to create DETAILED CINEMATIC SCENES into {panel_count} panels...")
    
    # Create detailed character context for consistency
    character_context = ""
    if character_details:
        character_context = "**CRITICAL CHARACTER CONSISTENCY REQUIREMENTS:**\n"
        character_context += "These characters MUST appear EXACTLY the same in every panel where they appear:\n\n"
        for name, desc in character_details.items():
            character_context += f"**{name}**: {desc}\n\n"
        character_context += "**NEVER change their clothing, hairstyle, age, or appearance. They must look identical in every panel.**\n\n"
    
    story_decomposition_prompt = f"""<s>[INST] You are a master comic book artist and cinematic storyteller. Your task is to break down the following story into exactly {panel_count} HIGHLY DETAILED, VISUALLY RICH comic book panels with STRICT CHARACTER CONSISTENCY.

{character_context}

**DETAILED SCENE CREATION REQUIREMENTS:**

1. **CHARACTER CONSISTENCY**: Use ONLY the characters described above. Never introduce new characters. Each character must appear EXACTLY as described in every panel.

2. **RICH VISUAL DESCRIPTIONS**: Each panel must include:
   - **Detailed Character Actions**: What each character is doing, their body language, facial expressions, gestures
   - **Cinematic Background**: Rich environmental details, lighting, atmosphere, objects, textures
   - **Story Context**: What's happening in the scene, the emotional tone, the narrative progression
   - **Visual Composition**: Camera angles, perspective, focal points, visual flow

3. **BACKGROUND DETAILS**: Each background must include:
   - **Setting Description**: Specific location details (indoor/outdoor, time of day, weather)
   - **Environmental Elements**: Trees, buildings, furniture, decorative items, natural features
   - **Lighting & Atmosphere**: Sunlight, shadows, mood lighting, color palette suggestions
   - **Props & Objects**: Relevant items that support the story and character actions

4. **CHARACTER ACTIONS**: For each character, describe:
   - **Body Position**: Standing, sitting, running, reaching, etc.
   - **Facial Expression**: Happy, surprised, worried, determined, etc.
   - **Hand Gestures**: Pointing, holding objects, waving, etc.
   - **Interaction**: How characters relate to each other and the environment

5. **STORY PROGRESSION**: Each panel should:
   - **Advance the Plot**: Move the story forward meaningfully
   - **Show Character Development**: Reveal character emotions and growth
   - **Create Visual Interest**: Varied compositions and dynamic scenes
   - **Maintain Narrative Flow**: Connect logically to previous and next panels

**CAPTION TYPES:**
- **"dialogue"**: Character speech (gets circular speech bubbles)
- **"narration"**: Story narration (gets rectangular boxes)  
- **"thought"**: Character thoughts (gets cloud-like bubbles)
- **"sfx"**: Sound effects (gets stylized text)

**FORMAT REQUIREMENTS:**
For each panel, provide this exact JSON structure with RICH DETAILS:

{{
  "panel": 1,
  "description": "HIGHLY DETAILED visual description: [Character Name] is [specific action/pose] with [facial expression] while [detailed body language]. The character is positioned [location in scene] and is [interacting with environment/objects]. [Additional character details and consistency reminders]",
  "background": "RICH ENVIRONMENTAL DESCRIPTION: The scene takes place in [specific location] during [time of day/weather]. The background features [detailed environmental elements like trees, buildings, furniture]. The lighting is [lighting description] creating [atmosphere/mood]. Additional details include [props, textures, colors, atmospheric elements]",
  "captions": [
    {{
      "type": "dialogue",
      "speaker": "Character Name (must match character list exactly)",
      "text": "What the character says out loud",
      "position": "top"
    }},
    {{
      "type": "narration", 
      "speaker": "Narrator",
      "text": "Rich story narration describing the scene's significance and emotional context",
      "position": "narrator_bottom"
    }}
  ]
}}

**CRITICAL RULES:**
- Use ONLY characters from the character list above
- Keep character appearances EXACTLY as described
- Create CINEMATIC, DETAILED scene descriptions
- Include rich background environments
- Show clear character actions and emotions
- Ensure story flows logically across all panels
- Make each panel visually interesting and story-relevant

**Story to decompose:**
{story_text}

Create exactly {panel_count} panels with RICH VISUAL DETAILS in JSON array format.[/INST]"""

    mistral_response = call_mistral_api(story_decomposition_prompt, max_tokens=5000)
    
    if not mistral_response:
        print("   > Mistral AI failed, using enhanced fallback scene decomposition")
        return decompose_story_fallback_enhanced(story_text, panel_count, character_details)
    
    try:
        # Try to parse the JSON response
        json_start = mistral_response.find('[')
        json_end = mistral_response.rfind(']') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = mistral_response[json_start:json_end]
            scenes = json.loads(json_str)
            
            if isinstance(scenes, list) and len(scenes) > 0:
                # Ensure we have exactly the requested number of panels
                if len(scenes) > panel_count:
                    scenes = scenes[:panel_count]
                elif len(scenes) < panel_count:
                    # Extend with additional panels if needed
                    scenes = extend_scenes_to_count_enhanced(scenes, panel_count, story_text, character_details)
                
                # Validate and enhance scene details
                enhanced_scenes = validate_and_enhance_scenes(scenes, character_details)
                
                print(f"   > Successfully created {len(enhanced_scenes)} DETAILED CINEMATIC scenes")
                for i, scene in enumerate(enhanced_scenes):
                    print(f"     Panel {i+1}: {scene.get('description', '')[:120]}...")
                    print(f"       Background: {scene.get('background', '')[:100]}...")
                    captions = scene.get('captions', [])
                    print(f"       Total captions: {len(captions)}")
                
                return enhanced_scenes
            else:
                print("   > Mistral returned empty or invalid scene data")
                return decompose_story_fallback_enhanced(story_text, panel_count, character_details)
        else:
            print("   > Could not find valid JSON in Mistral response")
            return decompose_story_fallback_enhanced(story_text, panel_count, character_details)
            
    except json.JSONDecodeError as e:
        print(f"   > Error parsing Mistral JSON response: {e}")
        return decompose_story_fallback_enhanced(story_text, panel_count, character_details)

def validate_and_enhance_scenes(scenes: List[Dict], character_details: Dict[str, str]) -> List[Dict]:
    """
    Validates and enhances scene descriptions with rich details and character consistency.
    """
    print("   > Validating and enhancing scene details...")
    
    valid_character_names = set(character_details.keys())
    
    for scene_idx, scene in enumerate(scenes):
        # Enhance character consistency in descriptions
        description = scene.get('description', '')
        if description and valid_character_names:
            char_names_in_desc = [name for name in valid_character_names if name.lower() in description.lower()]
            if char_names_in_desc:
                consistency_reminder = f" CRITICAL CONSISTENCY: {', '.join(char_names_in_desc)} must appear exactly as described in character details - identical clothing, hairstyle, age, and appearance."
                scene['description'] = description + consistency_reminder
        
        # Ensure rich background descriptions
        background = scene.get('background', '')
        if not background or len(background) < 100:
            scene['background'] = create_rich_background_description(scene_idx + 1, description)
        
        # Validate captions for character consistency
        captions = scene.get('captions', [])
        for caption in captions:
            speaker = caption.get('speaker', '')
            if speaker and speaker not in ['Narrator', 'SFX'] and speaker not in valid_character_names:
                print(f"     Warning: Panel {scene_idx + 1} has invalid character '{speaker}', replacing with valid character")
                if valid_character_names:
                    caption['speaker'] = list(valid_character_names)[0]
    
    return scenes

def create_rich_background_description(panel_num: int, character_description: str) -> str:
    """
    Creates rich, detailed background descriptions when Mistral doesn't provide enough detail.
    """
    # Extract context clues from character description
    if 'garden' in character_description.lower():
        return f"The scene unfolds in a lush, vibrant garden during golden hour. Sunlight filters through leafy tree branches, casting dappled shadows on the emerald grass. Colorful flower beds with roses, daisies, and tulips create a rainbow of colors. A wooden swing hangs from an old oak tree, gently swaying in the warm breeze. Butterflies dance among the blooms while birds chirp melodiously from hidden perches. The atmosphere is magical and peaceful, with soft, warm lighting that makes everything glow."
    
    elif 'fairy' in character_description.lower():
        return f"A mystical, enchanted setting where reality blends with magic. Sparkles of golden light dance in the air, creating an ethereal atmosphere. The background shimmers with soft, iridescent colors - purples, blues, and golds that seem to move and flow. Tiny points of light float like fireflies, and the air itself seems to glimmer with magical energy. The lighting is soft and dreamlike, with a gentle glow that makes everything appear otherworldly and beautiful."
    
    elif 'house' in character_description.lower() or 'home' in character_description.lower():
        return f"A cozy, welcoming home environment with warm, inviting details. Comfortable furniture with soft cushions and throws creates a lived-in feeling. Family photos and artwork decorate the walls, while plants add life to windowsills. Natural light streams through curtains, creating a warm, golden ambiance. The space feels safe and nurturing, with details like books on shelves, a tea cup on a side table, and the gentle tick of a wall clock adding to the homey atmosphere."
    
    else:
        return f"A beautifully detailed scene with rich environmental elements. The setting features carefully arranged objects and natural elements that support the story. Lighting creates depth and mood, with shadows and highlights that add visual interest. The atmosphere is carefully crafted to match the emotional tone of the scene, with colors and textures that enhance the narrative. Every element in the background serves to immerse the viewer in the story world."

def extend_scenes_to_count_enhanced(scenes: List[Dict], target_count: int, story_text: str, character_details: Dict[str, str]) -> List[Dict]:
    """
    Extends the scene list to match the target panel count with RICH DETAILED scenes.
    """
    while len(scenes) < target_count:
        panel_num = len(scenes) + 1
        
        # Use existing characters only
        main_character = list(character_details.keys())[0] if character_details else "MainCharacter"
        
        if panel_num == target_count:
            # Make the last panel a detailed conclusion
            additional_scene = {
                "panel": panel_num,
                "description": f"{main_character} stands in a triumphant pose with a bright, satisfied smile, arms raised in celebration or hands on hips in a confident stance. The character's eyes sparkle with joy and accomplishment, and their entire body language conveys the successful completion of their adventure. {main_character} must appear exactly as described in character details - same clothing, hairstyle, and appearance.",
                "background": "The concluding scene takes place in a beautiful, sunlit environment that represents the successful end of the journey. Golden sunlight bathes everything in a warm, celebratory glow. The background features elements that callback to the story's beginning, showing how things have changed and grown. Flowers bloom more vibrantly, colors are richer and more saturated, and there's a sense of completion and harmony in the composition. The lighting is optimistic and uplifting, with soft shadows that add depth without darkness.",
                "captions": [
                    {
                        "type": "narration",
                        "speaker": "Narrator", 
                        "text": "And so our adventure comes to a wonderful conclusion, with lessons learned and friendships strengthened.",
                        "position": "narrator_bottom"
                    }
                ]
            }
        else:
            # Create a detailed transitional panel
            additional_scene = {
                "panel": panel_num,
                "description": f"{main_character} is shown in a moment of discovery or realization, with wide, curious eyes and an expression of wonder. The character leans forward slightly, showing engagement with their surroundings, perhaps reaching out to touch something or pointing at an interesting detail. Their posture shows alertness and interest in the unfolding story. {main_character} must appear exactly as described in character details - same clothing, hairstyle, and appearance.",
                "background": "A transitional scene that bridges story elements, featuring a dynamic environment that suggests movement and progress. The setting includes interesting details that hint at what's to come - perhaps mysterious shadows, intriguing objects, or pathways that lead to new discoveries. The lighting creates a sense of anticipation, with areas of light and shadow that suggest both the known and unknown. The atmosphere builds tension and curiosity for what happens next.",
                "captions": [
                    {
                        "type": "narration",
                        "speaker": "Narrator",
                        "text": "The adventure continues to unfold, bringing new discoveries and exciting possibilities.",
                        "position": "narrator_bottom"
                    }
                ]
            }
        
        scenes.append(additional_scene)
    
    return scenes

def decompose_story_fallback_enhanced(story_text: str, panel_count: int, character_details: Dict[str, str]) -> List[Dict]:
    """
    Enhanced fallback method with RICH DETAILED scenes, character consistency and proper dialogue/narration.
    """
    print("   > Using enhanced fallback with RICH DETAILED scene decomposition")
    scenes = []
    
    # Split story into sentences for basic decomposition
    sentences = re.split(r'[.!?]+', story_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        sentences = ["A wonderful story unfolds with interesting characters and magical events."]
    
    # Get main character for consistency
    main_character = list(character_details.keys())[0] if character_details else "MainCharacter"
    
    # Distribute sentences across panels
    sentences_per_panel = max(1, len(sentences) // panel_count)
    
    # Rich background templates
    background_templates = [
        "A vibrant, sunlit garden scene with lush green grass, colorful flower beds blooming with roses and daisies, tall oak trees providing dappled shade, and butterflies dancing in the warm afternoon air. The lighting is golden and magical, creating a peaceful, enchanting atmosphere.",
        
        "An intimate, cozy indoor setting with warm wooden furniture, soft cushions, family photos on the walls, and gentle sunlight streaming through lace curtains. The atmosphere is nurturing and safe, with details like potted plants, books on shelves, and the soft glow of afternoon light.",
        
        "A mystical, magical environment where sparkles of light dance in the air and everything seems to shimmer with enchantment. The background features ethereal colors - soft purples, blues, and golds - with floating points of light and an otherworldly glow that makes the scene feel dreamlike and wonderful.",
        
        "A dynamic outdoor scene with interesting pathways, intriguing shadows, and elements that suggest adventure and discovery. The lighting creates depth and mystery, with areas of bright sunlight contrasting with cool shadows, building anticipation for what lies ahead."
    ]
    
    for i in range(panel_count):
        start_idx = i * sentences_per_panel
        end_idx = start_idx + sentences_per_panel
        
        if i == panel_count - 1:  # Last panel gets remaining sentences
            panel_sentences = sentences[start_idx:]
        else:
            panel_sentences = sentences[start_idx:end_idx]
        
        if panel_sentences:
            # Create rich character description
            action_words = ["exploring", "discovering", "reaching", "looking", "smiling", "wondering"]
            emotion_words = ["curious", "excited", "amazed", "joyful", "determined", "hopeful"]
            
            action = action_words[i % len(action_words)]
            emotion = emotion_words[i % len(emotion_words)]
            
            description = f"{main_character} is {action} with a {emotion} expression, showing clear engagement with the unfolding story. The character's body language conveys {emotion} through their posture and facial expression. {panel_sentences[0]} {main_character} must appear exactly as described in character details - same clothing, hairstyle, and appearance."
            narration = '. '.join(panel_sentences)
        else:
            description = f"{main_character} appears in a moment of story progression, with expressive body language that conveys the emotional tone of the scene. The character must appear exactly as described in character details - same clothing, hairstyle, and appearance."
            narration = "The story continues with interesting developments and character growth."
        
        # Select appropriate background
        background = background_templates[i % len(background_templates)]
        
        # Create mix of dialogue and narration
        captions = [
            {
                "type": "narration",
                "speaker": "Narrator",
                "text": narration,
                "position": "narrator_bottom"
            }
        ]
        
        # Add some dialogue for variety
        if i % 2 == 0 and main_character != "MainCharacter":
            dialogue_options = [
                "This is so exciting!",
                "What an amazing discovery!",
                "I can't believe this is happening!",
                "This is the best adventure ever!"
            ]
            captions.append({
                "type": "dialogue",
                "speaker": main_character,
                "text": dialogue_options[i % len(dialogue_options)],
                "position": "top"
            })
        
        scene = {
            "panel": i + 1,
            "description": description,
            "background": background,
            "captions": captions
        }
        
        scenes.append(scene)
    
    return scenes

def scene_decomposer(state: ComicGenerationState) -> dict:
    """
    Enhanced scene decomposer with RICH DETAILED SCENES, strict character consistency and proper dialogue/narration handling.
    """
    print("---AGENT: Scene Decomposer (RICH DETAILED SCENES + Character Consistency)---")
    
    story_text = state.get('story_text', '').strip()
    panel_count = state.get('panel_count', 4)
    character_details = state.get('character_details', {})
    
    if not story_text:
        print("   > No story text provided. Using default placeholder.")
        story_text = "A wonderful story about adventure and discovery unfolds with interesting characters in magical settings."
    
    print(f"   > Creating RICH DETAILED SCENES for {panel_count} panels with CHARACTER CONSISTENCY...")
    print(f"   > Story preview: {story_text[:150]}...")
    print(f"   > Characters to maintain consistency: {list(character_details.keys())}")
    
    try:
        # Use Mistral AI to decompose the story with rich details and character consistency
        scenes = decompose_story_with_mistral(story_text, panel_count, character_details)
        
        print(f"   > Successfully created {len(scenes)} RICH DETAILED scenes with character consistency")
        for i, scene in enumerate(scenes):
            print(f"     Panel {i+1}:")
            print(f"       Description: {scene.get('description', '')[:150]}...")
            print(f"       Background: {scene.get('background', '')[:150]}...")
            captions = scene.get('captions', [])
            print(f"       Total captions: {len(captions)}")
            for cap in captions:
                print(f"         {cap.get('type', 'unknown')}: {cap.get('text', '')[:60]}...")
    
    except Exception as e:
        print(f"   > Error in AI scene decomposition: {e}")
        print("   > Using enhanced fallback scene generation with rich details")
        
        # Fallback scenes with rich details and character consistency
        scenes = decompose_story_fallback_enhanced(story_text, panel_count, character_details)
    
    # Initialize the state for the panel generation loop
    return {
        "scenes": scenes,
        "current_panel_index": 0,
        "panel_prompts": [],
        "panel_images": [],
    }
