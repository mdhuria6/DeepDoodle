import os
from dotenv import load_dotenv

load_dotenv()

from graph.workflow import create_workflow

def generate_workflow_diagram(app=None):
    """
    Generates a PNG image of the LangGraph workflow diagram.
    
    This script requires the 'pygraphviz' library to be installed.
    On macOS with Homebrew, you may need to install it like this:
    1. brew install graphviz
    2. LDFLAGS="-L/opt/homebrew/lib" CPPFLAGS="-I/opt/homebrew/include" pip install pygraphviz
    """
    print("Attempting to generate workflow diagram...")


    output_filename = "workflow_diagram.png"

    try:
        # Get the graph object from the compiled app
        graph = app.get_graph()

        # Generate the image data as bytes
        image_bytes = graph.draw_mermaid_png()

        # Save the bytes to a file
        with open(output_filename, "wb") as f:
            f.write(image_bytes)

        print(f"✅ Workflow diagram saved successfully as '{output_filename}' in your project root.")

    except Exception as e:
        print("\n" + "="*50)
        print("❌ ERROR: Could not generate the diagram.")
        print("This usually means the 'pygraphviz' library or the system-level 'graphviz' tool is not installed correctly.")
        print("\nPlease ensure you have installed Graphviz on your system.")
        print("For macOS with Homebrew, run: brew install graphviz")
        print("For Ubuntu/Debian, run: sudo apt-get install graphviz")
        print("\nThen, try reinstalling pygraphviz with the correct flags for your system.")
        print(f"   Detailed Error: {e}")
        print("="*50 + "\n")

if __name__ == "__main__":

    # Create an instance of the compiled workflow app
    app = create_workflow()
    generate_workflow_diagram(app)