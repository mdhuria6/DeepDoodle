# configs/prompt_styles.py

# --- Style Configuration Dictionary ---
STYLE_CONFIGS = {
    "Simple Line Art Comic": {
        "style_keywords": "simple line art, clear bold outlines, 2D graphic illustration, flat colors, minimal shading, clean vector style, ",
        "lighting_keywords": "flat lighting",
        "additional_details": "easily understandable forms",
        "prompt_suffix": " Scene should be easily understandable." # Specific suffix for this style
    },
    "Black and White Manga": {
        "style_keywords": "monochrome, black and white, manga style, screentones, dynamic lines, clear outlines, ",
        "lighting_keywords": "dramatic shadows",
        "additional_details": "expressive characters"
    },
    "Ghibli Animation": {
        "style_keywords": "Studio Ghibli style, hand-drawn animation aesthetic, painterly backgrounds, soft lighting, whimsical atmosphere, detailed natural environments, expressive characters, nostalgic feeling, beautiful scenery, anime film look, ",
        "lighting_keywords": "soft, natural lighting",
        "additional_details": "lush environments"
    },
    "Modern Anime": {
        "style_keywords": "modern anime style, vibrant colors, sharp digital lines, dynamic action poses, detailed character designs, cel shading, high contrast, cinematic angles, contemporary Japanese animation, ",
        "lighting_keywords": "dynamic, vibrant lighting",
        "additional_details": "crisp details"
    },
    "Classic Western Comic": {
        "style_keywords": "classic western comic book art, bold outlines, graphic illustration, dynamic paneling style, strong shadows, heroic poses, action-packed scenes, Ben Day dots, retro comic aesthetic, ",
        "lighting_keywords": "strong, contrasted lighting",
        "additional_details": "clear action"
    }
    # Add more styles here as needed
}

# --- Default values if a style is not found or a keyword is missing ---
DEFAULT_STYLE_KEYWORDS = "versatile comic art style, " # General default
DEFAULT_LIGHTING_KEYWORDS = "cinematic lighting"
DEFAULT_ADDITIONAL_DETAILS = "high detail"
DEFAULT_PROMPT_SUFFIX = ""
