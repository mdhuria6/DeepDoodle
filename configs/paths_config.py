import os
from configs.base_config import PROJECT_ROOT

# Asset Paths
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# --- Font Paths ---
BUNDLED_FONT_PATH = os.path.join(FONTS_DIR, "ComicNeue", "ComicNeue-Regular.ttf")
HINDI_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansHindi.ttf")
TAMIL_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansTamil.ttf")
TELUGU_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansTelugu.ttf")

# Output Directories
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
RAW_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels")
SIZED_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels_sized")
CAPTIONED_PANELS_DIR = os.path.join(OUTPUT_DIR, "panels_with_captions")
COMIC_PAGES_DIR = os.path.join(OUTPUT_DIR, "pages")
