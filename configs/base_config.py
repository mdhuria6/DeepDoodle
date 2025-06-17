import os
from dotenv import load_dotenv

# Load variables from .env file for sensitive information like API keys
load_dotenv()

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
if not HUGGINGFACE_API_TOKEN:
    print("Warning: HUGGINGFACE_API_TOKEN not found in .env file. Some features may not work.")

# PROJECT_ROOT is defined as the directory containing the 'configs' folder (i.e., the main project directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))