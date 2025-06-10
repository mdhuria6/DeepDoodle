import os
import shutil
from graph import create_workflow
from utils import OUTPUT_DIR


def main():
    """
    Main function to set up the environment and run the comic generation workflow.
    """
    # Clean up previous outputs
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    
    os.makedirs(OUTPUT_DIR)
    os.makedirs(os.path.join(OUTPUT_DIR, "panels"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "pages"), exist_ok=True)
    print(f"Output directory '{OUTPUT_DIR}' has been set up and cleaned.")
    print("Starting comic generation workflow...")

    # --- DEFINE YOUR COMIC JOB HERE ---
    story = """
    In the silent hum of the deep space observatory, veteran astronomer Elara felt a familiar loneliness. For years, her screens showed nothing but cosmic static. Tonight was different. A single, pure sine wave, glowing an emerald green, cut through the noise. It was a signal. Before she could process it, alarms blared. A nearby red giant, catalogued for centuries, had gone supernova, decades ahead of schedule. The energy readings were impossible. As the shockwave data streamed in, she saw it: the supernova's energy was being shaped, focused. The sine wave wasn't from the star; it was riding the wave, a message in a bottle on a stellar tsunami. It was an invitation. Years later, her hair now streaked with grey, Elara steps out onto a world bathed in the light of twin suns. The air is sweet, the ground soft. A bustling, elegant city rises in the distance, a testament to her arrival. She looks at a device in her hand, which displays that same, beautiful green sine wave. She wasn't the discoverer of a message; she was its recipient. And she was finally home.
    """
    
    inputs = {
        "story_text": story,
        "panel_count": 8,
        "style_preset": "Modern Anime",
        "genre_preset": "Sci-Fi",
        "layout_style": "mixed_2x2", # CHOOSE: grid_2x2, horizontal_strip, vertical_strip, feature_left, mixed_2x2
    }

    # Create and run the workflow
    app = create_workflow()
    
    print("--- Starting Comic Generation ---")
    print(f"   Requesting {inputs['panel_count']} panels with '{inputs['layout_style']}' layout.")
    
    for output in app.stream(inputs, {"recursion_limit": 20}):
        for key, value in output.items():
            print(f"Finished running node '{key}'.")
        print("\n=====================================\n")

    print("--- Comic Generation Complete ---")
    print(f"   -> Final comic pages saved in the '{OUTPUT_DIR}' directory.")


if __name__ == "__main__":
    main()
