import os
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import create_workflow

def generate_workflow_diagram(app=None):
    """
    Generates a PNG image of the LangGraph workflow diagram.
    (pygraphviz dependency temporarily removed for deployment compatibility.)
    """
    print("Attempting to generate workflow diagram...")

    output_filename = "workflow_diagram.png"

    try:
        # Get the graph object from the compiled app
        graph = app.get_graph()

        # Instead of drawing, just print a placeholder message
        print("[INFO] Diagram generation is currently disabled (pygraphviz not installed).")
        # Optionally, you could export a DOT file or skip this step entirely
        # with open(output_filename, "w") as f:
        #     f.write("Diagram generation is disabled.")

    except Exception as e:
        print("\n" + "="*50)
        print("ERROR: Could not generate the diagram.")
        print("[INFO] Diagram generation is currently disabled (pygraphviz not installed).")
        print(f"Exception: {e}")
        print("="*50 + "\n")

if __name__ == "__main__":

    # Create an instance of the compiled workflow app
    app = create_workflow()
    generate_workflow_diagram(app)