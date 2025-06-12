# configs/image_opts_config.py

# --- Image Generation & Processing ---
PANEL_OUTPUT_SIZE = (512, 512) # Default size for raw panel images from generator

# Page Dimensions
# The original utils/config.py had two definitions for PAGE_WIDTH and PAGE_HEIGHT.
# The latter definitions (540, 860) would take precedence in Python execution.
# PAGE_WIDTH_FINAL_COMIC = 1024  # As defined in utils/config.py line 33
# PAGE_HEIGHT_FINAL_COMIC = 1024 # As defined in utils/config.py line 34

PAGE_WIDTH = 540  # Standard page width in pixels (from utils/config.py line 41)
PAGE_HEIGHT = 860 # Standard page height in pixels (from utils/config.py line 42)
MARGIN = 5        # Margin around panels and page edges in pixels (from utils/config.py line 43)

# Default panel size for grid layout, calculated based on margins
# This calculation assumes a 2x2 grid on a page defined by PAGE_WIDTH and MARGIN.
PANEL_SIZE = (PAGE_WIDTH - 3 * MARGIN) // 2 # (from utils/config.py line 44)
