# utils/huggingface_utils.py
import os
import json
from typing import Dict, Any, Optional, List
from huggingface_hub import InferenceClient
from PIL import Image
import io
import logging
import re

# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceClient:
    """
    Unified client for Hugging Face Inference API operations.
    Provides methods for text generation and conversational (chat) completion.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the HuggingFaceClient with an API token.
        If no token is provided, attempts to read from the environment variable 'HUGGINGFACE_API_TOKEN'.
        Raises:
            ValueError: If no token is found.
        """
        self.token = token or os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.token:
            raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables")
        # Create the HuggingFace InferenceClient instance
        self.client = InferenceClient(token=self.token)
        logger.info("HuggingFace client initialized successfully")

    
    def generate_conversation(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Dict[str, Any]:
        """
        Generate a conversation response using the specified model.
        
        Args:
            model (str): The Hugging Face model ID to use.
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content'.
            max_new_tokens (int): Maximum number of tokens to generate.
            temperature (float): Sampling temperature.
            top_p (float): Nucleus sampling parameter.
        
        Returns:
            Dict[str, Any]: The response from the model.
        """
        logger.info(f"Generating conversation with model {model}")
        # Try with max_new_tokens, fallback to max_tokens if needed
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
        except Exception as e:
            logger.error(f"Error generating conversation: {e}")
            raise
        logger.info("Conversation generated successfully")
        return response
# Global HuggingFace client instance (singleton pattern)
_hf_client = None

def get_hf_client() -> HuggingFaceClient:
    """
    Get or create a global HuggingFace client instance.
    Returns:
        HuggingFaceClient: The singleton client instance.
    """
    global _hf_client
    if _hf_client is None:
        _hf_client = HuggingFaceClient()
    return _hf_client