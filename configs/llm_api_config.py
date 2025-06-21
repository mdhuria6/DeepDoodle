# configs/llm_api_config.py
# OPENAI_API_KEY is loaded and available from configs.base_config

# --- Image Generation Configuration ---
# Flag to enable/disable Bedrock image generation
USE_BEDROCK_IMAGE_GENERATION = False

# AWS Bedrock settings (only used if USE_BEDROCK_IMAGE_GENERATION is True)
BEDROCK_AWS_REGION = "us-east-1"
BEDROCK_IMAGE_MODEL_ID = "stability.stable-diffusion-xl-v1"
#BEDROCK_IMAGE_MODEL_ID = "amazon.titan-image-generator-v1"
# For Stable Diffusion via Bedrock, you might use: "stability.stable-diffusion-xl-v0"
# or "stability.stable-diffusion-xl-v1" (check exact model ID in Bedrock console)
