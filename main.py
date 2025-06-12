import os
import shutil
from graph import create_workflow
from utils import OUTPUT_DIR


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
    print(f"Output directory '{OUTPUT_DIR}' has been set up and cleaned.")
    print("Starting comic generation workflow...")

    # --- Inputs are now passed as an argument ---
    # story = """ ... """
    
    # inputs = {
    #     "story_text": story,
    #     "panel_count": 8,
    #     "style_preset": "Modern Anime",
    #     "genre_preset": "Sci-Fi",
    #     "layout_style": "mixed_2x2", 
    # }

    # Create and run the workflow
    app = create_workflow()
    
    print("--- Starting Comic Generation ---")
    print(f"   Requesting {inputs.get('panel_count', 'N/A')} panels with '{inputs.get('layout_style', 'N/A')}' layout.")
    
    final_state = None
    for output in app.stream(inputs, {"recursion_limit": 20}):
        for key, value in output.items():
            print(f"Finished running node '{key}'.")
            if key == "__end__": # LangGraph typically uses "__end__" for the final state
                final_state = value
        print("\n=====================================\n")

    print("--- Comic Generation Complete ---")
    print(f"   -> Final comic pages saved in the '{OUTPUT_DIR}' directory.")
    return final_state # Return the final state which might contain output paths


if __name__ == "__main__":
    # Example of how to run it directly, you might want to adjust this for direct script execution
    example_story = """
    In the silent hum of the deep space observatory, veteran astronomer Elara felt a familiar loneliness. For years, her screens showed nothing but cosmic static. Tonight was different. A single, pure sine wave, glowing an emerald green, cut through the noise. It was a signal. Before she could process it, alarms blared. A nearby red giant, catalogued for centuries, had gone supernova, decades ahead of schedule. The energy readings were impossible. As the shockwave data streamed in, she saw it: the supernova's energy was being shaped, focused. The sine wave wasn't from the star; it was riding the wave, a message in a bottle on a stellar tsunami. It was an invitation. Years later, her hair now streaked with grey, Elara steps out onto a world bathed in the light of twin suns. The air is sweet, the ground soft. A bustling, elegant city rises in the distance, a testament to her arrival. She looks at a device in her hand, which displays that same, beautiful green sine wave. She wasn't the discoverer of a message; she was its recipient. And she was finally home.
    """
    default_inputs = {
        "story_text": example_story,
        "panel_count": 4, # Reduced for quicker testing
        "style_preset": "Vintage Comic",
        "genre_preset": "Adventure",
        "layout_style": "grid_2x2",
    }
    run_comic_generation_workflow(default_inputs)
