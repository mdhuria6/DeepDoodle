import os
from dotenv import load_dotenv

# --- Environment Variables ---
# Load variables from .env file for sensitive information like API keys
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env file. Please ensure it's set in your .env file.")

# --- Project Structure & Paths ---
# PROJECT_ROOT is defined as the directory containing the 'utils' folder (i.e., the main project directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Asset Paths
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
BUNDLED_FONT_PATH = os.path.join(FONTS_DIR, "Roboto", "Roboto-VariableFont_wdth,wght.ttf")

# Output Directories
# All output is organized under a main 'output' directory within the project root.
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
RAW_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels") # For initial generated panels
SIZED_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels_sized") # For panels after sizing
CAPTIONED_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels_with_captions") # For panels with text
COMIC_PAGES_DIR = os.path.join(OUTPUT_DIR, "pages") # For final composed comic pages

# --- Story & Character Configuration ---
# Default character description to ensure consistency across generated content.
CHARACTER_DESCRIPTION = "Elara, a young female astronomer with dark hair in a ponytail, wearing a headset."

# --- Page Layout & Dimensions ---
# Defines the final dimensions and margins for comic pages.
PAGE_WIDTH = 600  # pixels
PAGE_HEIGHT = 960 # pixels
MARGIN = 10       # pixels

PANEL_SIZE = 512 # Original default panel size, less directly used now as panel dimensions are
                   # calculated dynamically based on layout and page dimensions.
                   # Kept for reference or if specific fixed-size panel logic is reintroduced.

# --- Other Application Constants (Add as needed) ---
# Example: MAX_PANELS_PER_PAGE = 4
