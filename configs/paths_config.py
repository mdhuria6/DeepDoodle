# configs/paths_config.py
import os
from configs.base_config import PROJECT_ROOT

# Asset Paths
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
BUNDLED_FONT_PATH = os.path.join(FONTS_DIR, "ComicNeue", "ComicNeue-Regular.ttf")

# Output Directories
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
RAW_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels")
SIZED_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels_sized")
CAPTIONED_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels_with_captions")
COMIC_PAGES_DIR = os.path.join(OUTPUT_DIR, "pages")
