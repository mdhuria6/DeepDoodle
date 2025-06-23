import os
import shutil
import logging
from graph import create_workflow
from generate_workflow_diagram import generate_workflow_diagram
from configs import OUTPUT_DIR
import nltk 

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_comic_generation_workflow(inputs: dict):
    """
    Main function to set up the environment and run the comic generation workflow.
    Accepts an inputs dictionary for story, panel_count, style, genre, and layout.
    Returns the final state and the compiled workflow app.
    """
    # Clean up previous outputs
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    
    os.makedirs(OUTPUT_DIR)
    os.makedirs(os.path.join(OUTPUT_DIR, "panels"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "pages"), exist_ok=True)
    logger.info(f"Output directory '{OUTPUT_DIR}' has been set up and cleaned.")
    logger.info("Starting comic generation workflow.")

    # Create the workflow. The entry point is now managed internally by the graph.
    app = create_workflow()        
    logger.info("Starting Comic Generation ...")
    final_state = app.invoke(inputs, {"recursion_limit": 100})
    logger.info("Comic Generation Workflow Complete")
    return final_state, app

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
        "panel_count": 4,
        "style_preset": "Simple Line Art Comic",
        "genre_preset": "Sci-Fi",
        "layout_style": "mixed_2x2",
        "text_engine": "mistral_mixtral_8x7b_instruct",
    }
    final_state, app = run_comic_generation_workflow(default_inputs)
    generate_workflow_diagram(app)