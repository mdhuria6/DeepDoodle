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
BUNDLED_FONT_PATH = os.path.join(FONTS_DIR, "ComicNeue", "ComicNeue-Regular.ttf")

# Output Directories
# All output is organized under a main 'output' directory within the project root.
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
RAW_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels") # For initial generated panels
SIZED_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels_sized") # For panels after sizing
CAPTIONED_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels_with_captions") # For panels with text
COMIC_PAGES_DIR = os.path.join(OUTPUT_DIR, "pages") # For final composed comic pages

# --- Directory Paths ---
OUTPUT_DIR = "output"
RAW_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels")
COMIC_PAGES_DIR = os.path.join(OUTPUT_DIR, "pages")
SIZED_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels_sized") # For panel_sizer output
CAPTIONS_DIR = os.path.join(OUTPUT_DIR, "panels_with_captions") # For captioner output

# --- Image Generation & Processing ---
PANEL_OUTPUT_SIZE = (512, 512) # Default size for raw panel images from generator
PAGE_WIDTH = 1024  # Width of the final comic page in pixels
PAGE_HEIGHT = 1024 # Height of the final comic page in pixels

# --- Story & Character Configuration ---
# Default character description to ensure consistency across generated content.
CHARACTER_DESCRIPTION = "Elara, a young female astronomer with dark hair in a ponytail, wearing a headset."

# --- Page Layout & Dimensions ---
PAGE_WIDTH = 540  # Standard page width in pixels
PAGE_HEIGHT = 860 # Standard page height in pixels
MARGIN = 5        # Margin around panels and page edges in pixels
PANEL_SIZE = (PAGE_WIDTH - 3 * MARGIN) // 2  # Default panel size for grid layout, calculated based on margins


# --- Text & Caption Styling ---
# Caption styling
CAPTION_BACKGROUND_COLOR = (255, 255, 255, 100)  # RGBA: White with some transparency
CAPTION_TEXT_COLOR = "black"
CAPTION_PADDING = 8                    # Pixels inside the caption box
CAPTION_MARGIN = 5                      # Pixels outside the caption box (spacing between captions)
MAX_CAPTION_HEIGHT_RATIO = 0.25         # Max height of the entire caption block relative to panel height
LINE_SPACING = 2                        # Pixels between lines of text within a single caption
CAPTION_CORNER_RADIUS = 10              # Pixels for rounded corners of dialogue bubbles
NARRATOR_BACKGROUND_COLOR = (220, 220, 220, 100) # RGBA: Light grey with some transparency
MAX_FONT_SIZE = 14 # Maximum font size for captions
DEFAULT_FONT_SIZE = 12 # Default font size if not otherwise determined
MIN_FONT_SIZE = 10 # Absolute minimum font size to attempt for captions

# SFX (Sound Effects) styling
SFX_TEXT_COLOR = "yellow"  # Example: SFX text color, changed to yellow for visibility
SFX_FONT_PATH = None # Example: Path to a dedicated SFX font, set to None if not used or use BUNDLED_FONT_PATH

# --- UI Configuration ---
# DEFAULT_LAYOUT_STYLE sets the default layout for the comic panels.
# SUPPORTED_LAYOUT_STYLES lists all the layout styles that can be used.
DEFAULT_LAYOUT_STYLE = "grid_2x2"
SUPPORTED_LAYOUT_STYLES = ["grid_2x2", "horizontal_strip", "vertical_strip", "feature_left", "mixed_2x2"]

# DEFAULT_STYLE_PRESET and SUPPORTED_STYLE_PRESETS define the default and available style presets for the comic.
DEFAULT_STYLE_PRESET = "default comic style"
SUPPORTED_STYLE_PRESETS = ["default comic style", "Modern Anime", "Vintage Comic", "Noir", "Pop Art", "Minimalist"]

# DEFAULT_GENRE_PRESET and SUPPORTED_GENRE_PRESETS define the default and available genre presets for the comic.
DEFAULT_GENRE_PRESET = "neutral"
SUPPORTED_GENRE_PRESETS = ["neutral", "Sci-Fi", "Fantasy", "Adventure", "Comedy", "Horror", "Drama", "Mystery"]
