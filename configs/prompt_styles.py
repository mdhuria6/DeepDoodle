# configs/prompt_styles.py

# --- Style Configuration Dictionary ---
STYLE_CONFIGS = {
    "Simple Line Art Comic": {
        "style_keywords": "colorful comic book art, simple line art, clear bold outlines, 2D graphic illustration, bright vibrant colors, minimal shading, clean vector style, ",
        "lighting_keywords": "bright, cheerful lighting",
        "additional_details": "high quality colorful illustration, easily understandable forms, clean visual composition",
        "prompt_suffix": " Full color artwork, no black and white, no text elements."
    },
    "Black and White Manga": {
        "style_keywords": "colorful manga style, dynamic lines, clear outlines, vibrant colors, ",
        "lighting_keywords": "dramatic colorful lighting",
        "additional_details": "expressive characters, clean visual storytelling, full color",
        "prompt_suffix": " Full color manga style, vibrant colors, no text elements."
    },
    "Ghibli Animation": {
        "style_keywords": "Studio Ghibli style, hand-drawn animation aesthetic, painterly backgrounds, soft lighting, whimsical atmosphere, detailed natural environments, expressive characters, nostalgic feeling, beautiful scenery, anime film look, vibrant colors, ",
        "lighting_keywords": "soft, natural, colorful lighting",
        "additional_details": "lush colorful environments, clean visual composition",
        "prompt_suffix": " Full color Ghibli style, vibrant colors, no text elements."
    },
    "Modern Anime": {
        "style_keywords": "modern anime style, vibrant colors, sharp digital lines, dynamic action poses, detailed character designs, cel shading, high contrast, cinematic angles, contemporary Japanese animation, ",
        "lighting_keywords": "dynamic, vibrant, colorful lighting",
        "additional_details": "crisp details, clean visual storytelling, full color",
        "prompt_suffix": " Full color anime style, vibrant colors, no text elements."
    },
    "Classic Western Comic": {
        "style_keywords": "classic western comic book art, bold outlines, graphic illustration, vibrant colors, dynamic poses, action-packed scenes, retro comic aesthetic, colorful comic style, ",
        "lighting_keywords": "strong, vibrant, colorful lighting",
        "additional_details": "clear action, clean visual composition, full color illustration",
        "prompt_suffix": " Full color comic book style, vibrant colors, no text elements."
    }
}

# --- Default values if a style is not found or a keyword is missing ---
DEFAULT_STYLE_KEYWORDS = "colorful comic art style, vibrant colors, "
DEFAULT_LIGHTING_KEYWORDS = "bright, colorful lighting"
DEFAULT_ADDITIONAL_DETAILS = "high quality colorful illustration, clean visual composition"
DEFAULT_PROMPT_SUFFIX = " Full color artwork, vibrant colors, no text elements."
