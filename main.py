import os
import shutil
import logging
from graph import create_workflow
from configs import OUTPUT_DIR, PROMPT
from configs import STORY_EXPANSION_WORD_THRESHOLD
import nltk 

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_comic_generation_workflow(inputs: dict):
    """
    Main function to set up the environment and run the comic generation workflow.
    Accepts an inputs dictionary for story, panel_count, style, genre, and layout.
    """
    # Clean up previous outputs
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    
    os.makedirs(OUTPUT_DIR)
    os.makedirs(os.path.join(OUTPUT_DIR, "panels"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "pages"), exist_ok=True)
    logger.info(f"Output directory '{OUTPUT_DIR}' has been set up and cleaned.")
    logger.info("Starting comic generation workflow.")
    story_text = inputs.get("story_text", "")
    word_count = len(story_text.strip().split())

    # Create and run the workflow
    if word_count < STORY_EXPANSION_WORD_THRESHOLD:
        entry = "story_generator"
    else:
        if PROMPT == "Simple":
            entry = "story_analyst"
        elif PROMPT == "Detailed":
            entry = "detailed_story_analyst"
        else:
            raise ValueError("Incorrect prompt. Expected 'Simple' or 'Detailed'.")
    app = create_workflow(entry)        
    logger.info("Starting Comic Generation")
    final_state = app.invoke(inputs, {"recursion_limit": 100})
    logger.info("Comic Generation Workflow Complete")
    return final_state

if __name__ == "__main__":

    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    example_story = """
    In the silent hum of the deep space observatory, veteran astronomer Elara felt a familiar loneliness. 
    For years, her screens showed nothing but cosmic static. 
    Tonight was different. A single, pure sine wave, glowing an emerald green, cut through the noise. 
    It was a signal. Before she could process it, alarms blared. 
    A nearby red giant, catalogued for centuries, had gone supernova, decades ahead of schedule. 
    The energy readings were impossible. As the shockwave data streamed in, she saw it: the supernova's energy was being shaped, focused. 
    The sine wave wasn't from the star; it was riding the wave, a message in a bottle on a stellar tsunami. 
    It was an invitation. Years later, her hair now streaked with grey, Elara steps out onto a world bathed in the light of twin suns. 
    The air is sweet, the ground soft. A bustling, elegant city rises in the distance, a testament to her arrival. 
    She looks at a device in her hand, which displays that same, beautiful green sine wave. 
    She wasn't the discoverer of a message; she was its recipient. 
    And she was finally home.
    """
    default_inputs = {
        "story_text": example_story,
        "panel_count": 8,
        "style_preset": "Simple Line Art Comic",
        "genre_preset": "Sci-Fi",
        "layout_style": "mixed_2x2",
        "text_engine": "mistral_mixtral_8x7b_instruct",
        "prompt": PROMPT
    }
    run_comic_generation_workflow(default_inputs)
