# configs/base_config.py
import os
from dotenv import load_dotenv

# Load variables from .env file for sensitive information like API keys
load_dotenv()

# Hugging Face API Token (required for HF Pro)
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
if not HUGGINGFACE_API_TOKEN:
    raise ValueError("Missing HUGGINGFACE_API_TOKEN in .env file. Please ensure it's set in your .env file.")

# Optional: Keep OpenAI key for potential fallback (can be removed if not needed)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# PROJECT_ROOT is defined as the directory containing the 'configs' folder (i.e., the main project directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
