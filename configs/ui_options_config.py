# configs/ui_options_config.py
from .prompt_styles import STYLE_CONFIGS # Relative import for sibling module

# --- UI Configuration ---
DEFAULT_LAYOUT_STYLE = "grid_2x2"
SUPPORTED_LAYOUT_STYLES = ["mixed_2x2", "grid_2x2", "horizontal_strip", "vertical_strip", "feature_left"]

# Style presets are derived from prompt_styles.py for consistency with UI and generation
SUPPORTED_STYLE_PRESETS = ["auto"] + list(STYLE_CONFIGS.keys())
DEFAULT_STYLE_PRESET = "auto" # Defaulting to "auto" as in streamlit_app.py

# Genre/Mood presets aligned with streamlit_app.py mood_options
SUPPORTED_GENRE_PRESETS = ["auto", "Sci-Fi", "Fantasy", "Horror", "Comedy", "Drama", "Mystery", "Adventure", "Whimsical", "Noir", "Cyberpunk", "Steampunk"]
DEFAULT_GENRE_PRESET = "auto" # Defaulting to "auto" as in streamlit_app.py
