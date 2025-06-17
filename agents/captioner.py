from PIL import Image, ImageDraw, ImageFont
import os
import requests
import json
from typing import List, Dict, Tuple, Optional
from io import BytesIO
import base64
import numpy as np

from models.caption import Caption
from models.caption_style_metadata import CaptionStyleMetadata

from utils import draw_caption_bubbles
 
from models.comic_generation_state import ComicGenerationState
from utils import caption_util 
from configs import (
    CAPTIONED_PANELS_DIR, SIZED_PANELS_DIR, BUNDLED_FONT_PATH,
    CAPTION_BACKGROUND_COLOR, CAPTION_TEXT_COLOR, CAPTION_PADDING,
    CAPTION_MARGIN, MAX_CAPTION_HEIGHT_RATIO, MAX_FONT_SIZE,
    DEFAULT_FONT_SIZE, MIN_FONT_SIZE,
    LINE_SPACING, NARRATOR_BACKGROUND_COLOR, CAPTION_CORNER_RADIUS,
    SFX_TEXT_COLOR, SFX_FONT_PATH, HUGGINGFACE_API_TOKEN
)

def call_blip2_image_captioning(image_path: str) -> str:
    """
    Uses Salesforce BLIP-2 FLAN-T5-XL model to analyze and describe what's actually in the image.
    This is more advanced than the basic BLIP model and provides better scene understanding.
    """
    if not HUGGINGFACE_API_TOKEN:
        print("Warning: HUGGINGFACE_API_TOKEN not found. Cannot use BLIP-2 image captioning.")
        return ""
    
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip2-flan-t5-xl"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    
    try:
        # Read and encode the image
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # BLIP-2 can take specific questions/prompts for better analysis
        payload = {
            "inputs": {
                "image": base64.b64encode(image_bytes).decode(),
                "text": "Describe this comic panel scene in detail, focusing on character positions and what they are doing."
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                caption = result[0].get('generated_text', '').strip()
                print(f"   > BLIP-2 Analysis: {caption}")
                return caption
            elif isinstance(result, dict):
                caption = result.get('generated_text', '').strip()
                print(f"   > BLIP-2 Analysis: {caption}")
                return caption
            else:
                print(f"Unexpected BLIP-2 API response format: {result}")
                return ""
        else:
            print(f"BLIP-2 API error: {response.status_code} - {response.text}")
            # Fallback to basic image analysis
            return call_blip_fallback(image_path)
            
    except Exception as e:
        print(f"Error calling BLIP-2 API: {e}")
        return call_blip_fallback(image_path)

def call_blip_fallback(image_path: str) -> str:
    """
    Fallback to basic BLIP model if BLIP-2 fails.
    """
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        response = requests.post(API_URL, headers=headers, data=image_bytes, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                caption = result[0].get('generated_text', '').strip()
                print(f"   > BLIP Fallback Analysis: {caption}")
                return caption
        
        print("Both BLIP-2 and BLIP fallback failed")
        return "A comic book panel scene with characters"
        
    except Exception as e:
        print(f"BLIP fallback also failed: {e}")
        return "A comic book panel scene with characters"

def call_mistral_for_dialogues_only(
    panel_description: str,
    character_details: Dict[str, str],
    panel_index: int
) -> List[Dict]:
    """
    Uses Mistral AI to generate ONLY CHARACTER DIALOGUES (no narration).
    Enhanced to work without image analysis dependency.
    """
    if not HUGGINGFACE_API_TOKEN:
        print("Warning: HUGGINGFACE_API_TOKEN not found. Cannot use Mistral AI.")
        return []
    
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    
    # Prepare character context
    character_context = ""
    if character_details:
        character_context = "Characters available for dialogue:\n"
        for name, desc in character_details.items():
            character_context += f"- {name}: {desc[:100]}...\n"
        character_context += "\n"
    
    dialogue_generation_prompt = f"""<s>[INST] You are a comic book dialogue writer. Create ONLY CHARACTER SPEECH - what characters SAY OUT LOUD.

**SCENE DESCRIPTION:** {panel_description}
**CHARACTERS:** {character_context}
**PANEL NUMBER:** {panel_index + 1}

**TASK: Generate EXACTLY 6 character dialogues ONLY - NO NARRATION**

**REQUIRED FORMAT:**
[
  {{
    "speaker": "Riya",
    "text": "Wow, this is amazing!",
    "emotion": "excited"
  }},
  {{
    "speaker": "Aarav", 
    "text": "I can't believe it!",
    "emotion": "surprised"
  }},
  {{
    "speaker": "The Fairy",
    "text": "Welcome to my garden!",
    "emotion": "friendly"
  }},
  {{
    "speaker": "Riya",
    "text": "It's so beautiful here!",
    "emotion": "amazed"
  }},
  {{
    "speaker": "Aarav",
    "text": "Can we explore more?",
    "emotion": "curious"
  }},
  {{
    "speaker": "The Fairy",
    "text": "Of course, follow me!",
    "emotion": "welcoming"
  }}
]

**STRICT RULES:**
- Generate EXACTLY 6 dialogues (no more, no less)
- Use ONLY characters from the character list above
- Keep each dialogue short (4-8 words maximum)
- Include appropriate emotions for each dialogue
- Make characters interact naturally with each other
- Create conversation flow that matches the scene
- NO narration, NO scene description, ONLY what characters SAY

**DIALOGUE EXAMPLES:**
- "Look at that!"
- "This is incredible!"
- "Come here quickly!"
- "What do you think?"
- "I'm so excited!"
- "Let's go together!"

Generate JSON array with EXACTLY 6 dialogues:[/INST]"""

    payload = {
        "inputs": dialogue_generation_prompt,
        "parameters": {
            "max_new_tokens": 800,
            "temperature": 0.7,  # Balanced creativity
            "do_sample": True,
            "top_p": 0.9,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                mistral_response = result[0].get('generated_text', '').strip()
                
                # Parse JSON response
                json_start = mistral_response.find('[')
                json_end = mistral_response.rfind(']') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = mistral_response[json_start:json_end]
                    dialogues = json.loads(json_str)
                    
                    if isinstance(dialogues, list):
                        # STRICTLY enforce exactly 6 dialogues
                        if len(dialogues) > 6:
                            dialogues = dialogues[:6]
                        elif len(dialogues) < 6:
                            # Pad with simple dialogues if needed
                            dialogues = pad_dialogues_to_six(dialogues, character_details)
                        
                        print(f"   > Mistral generated exactly {len(dialogues)} dialogues")
                        
                        # Validate dialogues
                        validated_dialogues = validate_dialogues(dialogues, character_details)
                        
                        # Log generated content for debugging
                        for i, dialogue in enumerate(validated_dialogues):
                            print(f"     {i+1}. {dialogue.get('speaker', 'Unknown')}: \"{dialogue.get('text', '')}\" ({dialogue.get('emotion', 'neutral')})")
                        
                        return validated_dialogues
                    else:
                        print("   > Mistral returned invalid dialogue format")
                        return generate_fallback_dialogues(character_details)
                else:
                    print("   > Could not parse Mistral response")
                    return generate_fallback_dialogues(character_details)
            else:
                print(f"Unexpected Mistral API response: {result}")
                return generate_fallback_dialogues(character_details)
        else:
            print(f"Mistral API error: {response.status_code} - {response.text}")
            return generate_fallback_dialogues(character_details)
            
    except json.JSONDecodeError as e:
        print(f"Error parsing Mistral JSON response: {e}")
        return generate_fallback_dialogues(character_details)
    except Exception as e:
        print(f"Error calling Mistral API for dialogues: {e}")
        return generate_fallback_dialogues(character_details)

def pad_dialogues_to_six(dialogues: List[Dict], character_details: Dict[str, str]) -> List[Dict]:
    """
    Pads dialogue list to exactly 6 dialogues if Mistral generates fewer.
    """
    if len(dialogues) >= 6:
        return dialogues[:6]
    
    character_names = list(character_details.keys()) if character_details else ["Character"]
    
    # Simple padding dialogues
    padding_dialogues = [
        {"speaker": character_names[0] if character_names else "Character", "text": "Amazing!", "emotion": "excited"},
        {"speaker": character_names[1] if len(character_names) > 1 else character_names[0], "text": "I agree!", "emotion": "happy"},
        {"speaker": character_names[0] if character_names else "Character", "text": "Let's go!", "emotion": "eager"},
        {"speaker": character_names[1] if len(character_names) > 1 else character_names[0], "text": "Yes!", "emotion": "enthusiastic"},
        {"speaker": character_names[0] if character_names else "Character", "text": "Wonderful!", "emotion": "joyful"},
        {"speaker": character_names[1] if len(character_names) > 1 else character_names[0], "text": "Perfect!", "emotion": "satisfied"}
    ]
    
    # Add padding dialogues until we have exactly 6
    while len(dialogues) < 6:
        padding_index = len(dialogues) - len(dialogues)
        if padding_index < len(padding_dialogues):
            dialogues.append(padding_dialogues[padding_index])
        else:
            break
    
    return dialogues[:6]

def validate_dialogues(dialogues: List[Dict], character_details: Dict[str, str]) -> List[Dict]:
    """
    Validates that dialogues use correct character names and are appropriate length.
    """
    validated_dialogues = []
    valid_character_names = set(character_details.keys()) if character_details else set()
    
    for dialogue in dialogues:
        speaker = dialogue.get('speaker', '')
        text = dialogue.get('text', '').strip()
        emotion = dialogue.get('emotion', 'neutral')
        
        if not text:
            continue
        
        # Validate speaker name
        if speaker not in valid_character_names:
            if valid_character_names:
                # Use first available character
                speaker = list(valid_character_names)[0]
            else:
                speaker = "Character"  # Fallback speaker
        
        # Ensure dialogue is appropriate length (3-10 words)
        word_count = len(text.split())
        if word_count > 10:
            # Truncate if too long
            words = text.split()[:8]
            text = ' '.join(words) + "..."
        elif word_count < 2:
            # Skip if too short
            continue
        
        validated_dialogue = {
            'speaker': speaker,
            'text': text,
            'emotion': emotion
        }
        
        validated_dialogues.append(validated_dialogue)
    
    return validated_dialogues

def generate_fallback_dialogues(character_details: Dict[str, str]) -> List[Dict]:
    """
    Generates exactly 6 fallback dialogues when Mistral AI fails.
    """
    print("   > Using fallback dialogue generation (6 dialogues)")
    
    character_names = list(character_details.keys()) if character_details else ["Character1", "Character2"]
    
    # Ensure we have at least 2 character names
    if len(character_names) == 1:
        character_names.append("Friend")
    elif len(character_names) == 0:
        character_names = ["Character1", "Character2"]
    
    # Generate exactly 6 fallback dialogues
    fallback_dialogues = [
        {
            "speaker": character_names[0],
            "text": "This is amazing!",
            "emotion": "excited"
        },
        {
            "speaker": character_names[1], 
            "text": "I can't believe it!",
            "emotion": "surprised"
        },
        {
            "speaker": character_names[0],
            "text": "Look at this!",
            "emotion": "amazed"
        },
        {
            "speaker": character_names[1],
            "text": "So incredible!",
            "emotion": "wonder"
        },
        {
            "speaker": character_names[0],
            "text": "Let's explore more!",
            "emotion": "eager"
        },
        {
            "speaker": character_names[1],
            "text": "Great idea!",
            "emotion": "enthusiastic"
        }
    ]
    
    return fallback_dialogues

def create_optimal_grid_positions(panel_width: int, panel_height: int, dialogue_count: int = 6) -> List[Tuple[int, int]]:
    """
    Creates optimal 2x3 grid positions for exactly 6 speech bubbles to prevent overlapping.
    """
    # Create 2 rows, 3 columns grid for 6 dialogues
    positions = []
    
    # Calculate grid spacing
    cols = 3
    rows = 2
    
    # Add margins to prevent bubbles from touching edges
    margin_x = panel_width // 8
    margin_y = panel_height // 8
    
    # Calculate available space
    available_width = panel_width - (2 * margin_x)
    available_height = panel_height - (2 * margin_y)
    
    # Calculate spacing between positions
    col_spacing = available_width // cols
    row_spacing = available_height // rows
    
    # Generate positions
    for row in range(rows):
        for col in range(cols):
            x = margin_x + (col * col_spacing) + (col_spacing // 2)
            y = margin_y + (row * row_spacing) + (row_spacing // 2)
            positions.append((x, y))
    
    print(f"   > Created optimal 2x3 grid: {positions}")
    return positions

def analyze_character_positions_from_scene(panel_description: str, panel_width: int, panel_height: int) -> Dict[str, Tuple[int, int]]:
    """
    Analyzes scene description to determine optimal character positions without image analysis.
    """
    # Create optimal grid positions for 6 dialogues
    grid_positions = create_optimal_grid_positions(panel_width, panel_height, 6)
    
    # Map positions to character slots
    character_positions = {}
    for i in range(6):
        character_positions[f"character_{i+1}"] = grid_positions[i]
    
    print(f"   > Image dimensions: {panel_width}x{panel_height}")
    print(f"   > Final character positions: {character_positions}")
    
    return character_positions

def draw_dialogue_bubble(
    draw: ImageDraw.Draw,
    text: str,
    position: Tuple[int, int],
    font: ImageFont.FreeTypeFont,
    emotion: str = "neutral"
) -> None:
    """
    Draws a speech bubble for character dialogue with emotion-based styling.
    """
    # Calculate text dimensions
    lines = text.split('\n')
    max_line_width = 0
    
    for line in lines:
        line_width = font.getlength(line)
        max_line_width = max(max_line_width, line_width)
    
    line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]
    total_height = len(lines) * line_height + (len(lines) - 1) * 4  # 4px line spacing
    
    # Calculate bubble dimensions with padding
    padding = 10  # Smaller padding for 6 bubbles
    bubble_width = max_line_width + 2 * padding
    bubble_height = total_height + 2 * padding
    
    # Position bubble (center it on the given position)
    x = position[0] - bubble_width // 2
    y = position[1] - bubble_height // 2
    
    # Ensure bubble stays within image bounds
    margin = 5
    x = max(margin, min(x, draw.im.size[0] - bubble_width - margin))
    y = max(margin, min(y, draw.im.size[1] - bubble_height - margin))
    
    # Choose bubble style based on emotion
    if emotion in ["excited", "happy", "joyful", "eager", "enthusiastic"]:
        bubble_color = (255, 255, 255, 240)  # Bright white
        border_color = "orange"
        border_width = 2
    elif emotion in ["surprised", "shocked", "amazed", "wonder"]:
        bubble_color = (255, 255, 255, 240)
        border_color = "red"
        border_width = 2
    elif emotion in ["worried", "sad", "concerned"]:
        bubble_color = (240, 240, 255, 240)  # Slightly blue tint
        border_color = "blue"
        border_width = 2
    elif emotion in ["friendly", "welcoming", "kind"]:
        bubble_color = (255, 255, 255, 240)
        border_color = "green"
        border_width = 2
    else:
        bubble_color = (255, 255, 255, 240)  # Default white
        border_color = "black"
        border_width = 2
    
    # Draw oval speech bubble
    draw.ellipse(
        (x, y, x + bubble_width, y + bubble_height),
        fill=bubble_color,
        outline=border_color,
        width=border_width
    )
    
    # Add speech bubble tail pointing down (smaller for 6 bubbles)
    tail_size = 8
    tail_x = position[0]
    tail_y = y + bubble_height
    
    # Only draw tail if there's space
    if tail_y < draw.im.size[1] - 15:
        draw.polygon([
            (tail_x - tail_size, tail_y),
            (tail_x + tail_size, tail_y),
            (tail_x, tail_y + tail_size)
        ], fill=bubble_color, outline=border_color)
    
    # Draw text
    text_x = x + padding
    text_y = y + padding
    
    current_y = text_y
    for line in lines:
        draw.text(
            (text_x, current_y),
            line,
            fill="black",
            font=font,
            anchor="lt"
        )
        current_y += line_height + 4

def create_dialogue_only_image(
    image_path: str,
    dialogues: List[Dict],
    character_positions: Dict[str, Tuple[int, int]],
    panel_width: int,
    panel_height: int,
    panel_idx_for_logging: int = -1
) -> Image.Image:
    """
    Creates an image with EXACTLY 6 character dialogues in optimal grid layout.
    """
    print(f"   > Creating enhanced dialogue layout for {len(dialogues)} dialogues")
    
    # Load image
    try:
        img = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        img = Image.new("RGBA", (panel_width, panel_height), "white")
        draw = ImageDraw.Draw(img)
        return img

    # Load font for dialogue (smaller for 6 bubbles)
    try:
        dialogue_font = ImageFont.truetype(BUNDLED_FONT_PATH, 12)  # Smaller font for 6 bubbles
    except IOError:
        dialogue_font = ImageFont.load_default()

    # Draw exactly 6 character dialogues
    for i, dialogue in enumerate(dialogues[:6]):  # Ensure exactly 6 dialogues
        speaker = dialogue.get('speaker', 'Unknown')
        text = dialogue.get('text', '')
        emotion = dialogue.get('emotion', 'neutral')
        
        if not text.strip():
            continue
        
        # Get position from optimal grid
        position_key = f"character_{i+1}"
        position = character_positions.get(position_key, (panel_width//2, panel_height//2))
        
        # Draw dialogue bubble
        draw_dialogue_bubble(
            draw=draw,
            text=text,
            position=position,
            font=dialogue_font,
            emotion=emotion
        )
        
        print(f"   > Drew dialogue {i+1} for {speaker}: \"{text}\" at {position}")

    return img

def captioner(state: ComicGenerationState) -> dict:
    """
    Mistral-Only Captioner: Generates exactly 6 character dialogues per panel using only Mistral AI.
    """
    print(f"---AGENT: Mistral-Only Captioner (6 Dialogues Per Panel)---")

    sized_panel_paths = state.get("sized_panel_image_paths", [])
    scenes_data = state.get("scenes", []) 
    character_details = state.get("character_details", {})
    layout_style = state.get("layout_style", "grid_2x2")

    if not sized_panel_paths:
        print("Error: No sized panel paths found in state for captioner.")
        return {"panel_images_with_captions_paths": [], "scenes": scenes_data, "layout_style": layout_style}

    os.makedirs(CAPTIONED_PANELS_DIR, exist_ok=True)
    
    panel_images_with_captions_paths = []

    for idx, sized_panel_path in enumerate(sized_panel_paths):
        if idx >= len(scenes_data):
            print(f"Skipping captioning for panel {idx+1} as no corresponding scene data found.")
            continue

        current_scene = scenes_data[idx]
        panel_description = current_scene.get('description', 'A scene from the story')
        
        try:
            with Image.open(sized_panel_path) as temp_img:
                panel_width, panel_height = temp_img.size
        except FileNotFoundError:
            print(f"Error: Sized panel image not found at {sized_panel_path}. Skipping for panel {idx+1}.")
            continue
        except Exception as e:
            print(f"Error opening sized panel image {sized_panel_path}: {e}. Skipping for panel {idx+1}.")
            continue

        print(f"   > Creating 6 DIALOGUES for panel {idx + 1}")
        
        # Step 1: Generate exactly 6 character dialogues using Mistral AI only
        print(f"   > Generating exactly 6 character dialogues with Mistral AI...")
        dialogues = call_mistral_for_dialogues_only(
            panel_description=panel_description,
            character_details=character_details,
            panel_index=idx
        )
        
        # Step 2: Create optimal character positions without image analysis
        character_positions = analyze_character_positions_from_scene(
            panel_description, panel_width, panel_height
        )
        
        # Step 3: Create image with exactly 6 dialogues in optimal grid
        captioned_image = create_dialogue_only_image(
            image_path=sized_panel_path,
            dialogues=dialogues,
            character_positions=character_positions,
            panel_width=panel_width,
            panel_height=panel_height,
            panel_idx_for_logging=idx
        )

        # Step 4: Save the captioned image
        base_name = os.path.basename(sized_panel_path)
        name, _ = os.path.splitext(base_name)
        output_filename = f"{name}_mistral_6dialogue.png"
        output_path_captioned = os.path.join(CAPTIONED_PANELS_DIR, output_filename)
        
        try:
            captioned_image.save(output_path_captioned, "PNG")
            panel_images_with_captions_paths.append(output_path_captioned)
            print(f"     > Saved Mistral-only 6-dialogue panel to: {output_path_captioned}")
        except Exception as e:
            print(f"Error saving Mistral-only dialogue image {output_path_captioned}: {e}")

    return {
        "panel_images_with_captions_paths": panel_images_with_captions_paths,
        "scenes": scenes_data,
        "layout_style": layout_style
    }
