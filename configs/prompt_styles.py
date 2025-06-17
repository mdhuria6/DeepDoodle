# configs/prompt_styles.py

# --- Style Configuration Dictionary ---
STYLE_CONFIGS = {
    "Simple Line Art Comic": {
        "style_keywords": "simple line art, clear bold outlines, 2D graphic illustration, flat colors, minimal shading, clean vector style, ",
        "lighting_keywords": "flat lighting",
        "additional_details": "easily understandable forms",
        "prompt_suffix": " Scene should be easily understandable."
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
    },
    "Watercolor Storybook": {
        "style_keywords": "watercolor illustration, soft brush strokes, pastel colors, gentle gradients, dreamy atmosphere, storybook style, ",
        "lighting_keywords": "diffused, natural lighting",
        "additional_details": "whimsical details"
    },
    "Pixel Art": {
        "style_keywords": "pixel art, 8-bit style, retro video game graphics, blocky shapes, limited color palette, ",
        "lighting_keywords": "simple, flat lighting",
        "additional_details": "nostalgic feel"
    },
    "Noir Graphic Novel": {
        "style_keywords": "noir comic style, high contrast, heavy shadows, moody atmosphere, dramatic lighting, black and white, ",
        "lighting_keywords": "harsh, directional lighting",
        "additional_details": "mysterious mood"
    },
    "Disney Animation": {
        "style_keywords": "Disney animation style, expressive faces, smooth lines, vibrant colors, whimsical backgrounds, classic cartoon look, ",
        "lighting_keywords": "bright, cheerful lighting",
        "additional_details": "family-friendly tone"
    },
    "European Bande Dessinée": {
        "style_keywords": "bande dessinée, European comic style, clear line, detailed backgrounds, vibrant flat colors, realistic proportions, ",
        "lighting_keywords": "natural, balanced lighting",
        "additional_details": "rich environments"
    },
    "Gritty Noir Comic Art": {
        "style_keywords": "gritty noir comic art, rough textures, distressed inking, stark black and white, urban decay, rain-soaked streets, cigarette smoke, trench coats, fedoras, vintage crime drama, ",
        "lighting_keywords": "harsh, moody, low-key lighting with deep shadows",
        "additional_details": "atmospheric cityscapes, morally ambiguous characters, sense of danger and suspense, film noir influences, dramatic compositions, rain reflections, neon glows",
        "prompt_suffix": " Scene should evoke a sense of tension and mystery, with a focus on urban grit and classic noir aesthetics."
    }
}

# --- Default values if a style is not found or a keyword is missing ---
DEFAULT_STYLE_KEYWORDS = "versatile comic art style, " # General default
DEFAULT_LIGHTING_KEYWORDS = "cinematic lighting"
DEFAULT_ADDITIONAL_DETAILS = "high detail"
DEFAULT_PROMPT_SUFFIX = ""
