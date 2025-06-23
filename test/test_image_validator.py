import sys
import os
import logging
from pprint import pprint

# Add project root to Python path to allow importing project modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.image_validator import get_validator_instance
from models.scene import Scene
from models.caption import Caption

# --- Configuration ---
# Configure logging to print to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# --- Sample Data ---
# This data simulates the state that would be passed to the agent in a real run.
# IMPORTANT: Make sure this image exists in your project directory.
SAMPLE_IMAGE_PATH = os.path.abspath("assets/test-panel.png") 

# A sample scene description from the scene_decomposer agent
sample_scene: Scene = {
    "panel": 1,
    "description": "Elara stands on soft ground, looking towards a distant, elegant city. Her expression is one of awe and peace.",
    "captions": [
      {
        "order": 1,
        "speaker": "Elara",
        "text": "It's beautiful... more than I ever imagined.",
        "type": "dialogue",
        "location": "right"
      }
    ]
  }

# Sample character descriptions from the story_analyst agent
sample_character_descriptions = [
    {
      "name": "Elara",
      "description": "Veteran astronomer with hair streaked with grey, suggesting middle to late age. She has a contemplative and determined personality, indicated by her years of solitary work. Elara's eyes reflect intelligence and curiosity, likely a deep color such as brown or hazel. Her build is average, and she stands at medium height. Her skin tone is not specified, but she likely wears practical clothing suitable for her profession."
    }
  ]

# Sample artistic style from the story_analyst agent
sample_artistic_style = "Gritty Noir Comic Art"

def run_validation_test():
    """
    Runs a standalone test of the ImageValidator with sample data.
    """
    logging.info("--- Starting Image Validator Test ---")

    # 1. Check if the sample image exists
    if not os.path.exists(SAMPLE_IMAGE_PATH):
        logging.error(f"Sample image not found at: {SAMPLE_IMAGE_PATH}")
        logging.error("Please create a sample image or update the path.")
        return

    logging.info(f"Using image: {SAMPLE_IMAGE_PATH}")

    # 2. Manually construct the validation 'task' dictionary
    # This logic is copied from the image_validator agent function for a direct test.
    
    # Extract character description based on speaker
    character_description_for_validation = ""
    all_caption_texts = []
    if sample_scene.get("captions"):
        for caption in sample_scene["captions"]:
            all_caption_texts.append(caption.get("text", ""))
            speaker = caption.get("speaker")
            if speaker and speaker != "Narrator" and not character_description_for_validation:
                for char in sample_character_descriptions:
                    if char.get("name") == speaker:
                        character_description_for_validation = char.get("description", "")
                        break

    # Use combined caption text for "action"
    action_from_captions = " ".join(all_caption_texts)

    # The final task object
    validation_task = {
        "image_path": SAMPLE_IMAGE_PATH,
        "caption_parts": {
            "scene": sample_scene.get("description"),
            "character": character_description_for_validation,
            "action": action_from_captions,
        },
        "style_prompt": sample_artistic_style,
        "weights": {"scene": 0.4, "character": 0.4, "action": 0.2, "style": 0.1},
        "thresholds": {"scene": 0.25, "character": 0.25, "action": 0.2}
    }

    logging.info("Constructed Validation Task:")
    pprint(validation_task)

    # 3. Run the validator
    try:
        logging.info("Initializing ImageValidator (this may take a moment)...")
        # Use the singleton getter to ensure the CLIP model is loaded only once
        validator = get_validator_instance() 
        
        logging.info("Running validation...")
        result = validator.run(validation_task)

        logging.info("--- Validation Complete ---")
        logging.info("Final Result:")
        pprint(result)

    except Exception as e:
        logging.error(f"An error occurred during the validation test: {e}", exc_info=True)

if __name__ == "__main__":
    run_validation_test()
