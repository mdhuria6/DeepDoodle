# configs/llm_api_config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Hugging Face Configuration
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# --- LLM Configuration ---
# Use Hugging Face models for text generation
USE_HUGGINGFACE_LLM = True
HUGGINGFACE_LLM_MODEL = "meta-llama/Llama-2-7b-chat-hf"  # Switched to Llama-2-7b-chat for better instruction following
# Alternative models you can try:
# "microsoft/DialoGPT-large"
# "microsoft/DialoGPT-medium" 
# "HuggingFaceH4/zephyr-7b-beta"

# --- Image Generation Configuration ---
# Use Hugging Face models for image generation  
USE_HUGGINGFACE_IMAGE_GENERATION = True
HUGGINGFACE_IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"  # SDXL for high quality
# Alternative image models:
# "runwayml/stable-diffusion-v1-5"
# "stabilityai/stable-diffusion-2-1"
# "prompthero/openjourney-v4"

# Disable other providers
USE_BEDROCK_IMAGE_GENERATION = False
USE_OPENAI = False

# Legacy AWS Bedrock settings (kept for backward compatibility)
BEDROCK_AWS_REGION = "us-east-1"
BEDROCK_IMAGE_MODEL_ID = "stability.stable-diffusion-xl-v1"
