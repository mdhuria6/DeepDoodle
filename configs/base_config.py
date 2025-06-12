# configs/base_config.py
import os
from dotenv import load_dotenv

# Load variables from .env file for sensitive information like API keys
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env file. Please ensure it's set in your .env file.")

# PROJECT_ROOT is defined as the directory containing the 'configs' folder (i.e., the main project directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
