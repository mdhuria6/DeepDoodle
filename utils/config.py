import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env file")

# --- Configuration and Constants ---

# Define a consistent character for the story to help the Prompt Engineer
CHARACTER_DESCRIPTION = "Elara, a young female astronomer with dark hair in a ponytail, wearing a headset."

# Output directory for generated images and pages
OUTPUT_DIR = "output"
PANELS_DIR = os.path.join(OUTPUT_DIR, "panels")
PAGES_DIR = os.path.join(OUTPUT_DIR, "pages")

# Default panel size and margin for layouts
PANEL_SIZE = 512
MARGIN = 10
