# utils/huggingface_utils.py
import os
import json
from typing import Dict, Any, Optional, List
from huggingface_hub import InferenceClient
from PIL import Image
import io
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HuggingFaceClient:
    """Unified client for Hugging Face Inference API operations."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the HF client with API token."""
        self.token = token or os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.token:
            raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables")
        
        self.client = InferenceClient(token=self.token)
        logger.info("HuggingFace client initialized successfully")
    
    def generate_text(
        self, 
        prompt: str, 
        model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Generate text using HuggingFace LLM.
        
        Args:
            prompt: Input text prompt
            model: HuggingFace model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            
        Returns:
            Generated text string
        """
        try:
            
            # For instruction-tuned models, format the prompt properly
            if "Instruct" in model or "chat" in model.lower():
                formatted_prompt = f"<s>[INST] {prompt} [/INST]"
            else:
                formatted_prompt = prompt
            
            response = self.client.text_generation(
                formatted_prompt,
                model=model,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                return_full_text=False
            )
            
            # Handle different response types
            if isinstance(response, str):
                return response.strip()
            elif hasattr(response, 'generated_text'):
                return response.generated_text.strip()
            else:
                return str(response).strip()
                
        except Exception as e:
            logger.error(f"Error in text generation: {e}")
            return f"Error generating text: {str(e)}"
    
    def parse_json_response(self, text: str) -> Any:
        """
        Parse JSON from LLM response, handling common formatting issues and extracting the first valid JSON array.
        
        Args:
            text: Raw text response that should contain JSON
            
        Returns:
            Parsed JSON (list or dict)
        """
        try:
            text = text.strip()
            # Remove markdown code blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            # Try to extract the first JSON array
            array_match = re.search(r'(\[.*?\])', text, re.DOTALL)
            if array_match:
                json_text = array_match.group(1)
                try:
                    return json.loads(json_text)
                except Exception:
                    pass  # Try next fallback
            # Fallback: extract all {...} objects and build a list
            obj_matches = re.findall(r'\{[^{}]*\}', text, re.DOTALL)
            if obj_matches:
                try:
                    return [json.loads(obj) for obj in obj_matches]
                except Exception:
                    pass
            # Fallback: try parsing the whole text
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw text: {text[:200]}...")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in JSON parsing: {e}")
            return []

# Global client instance
_hf_client = None

def get_hf_client() -> HuggingFaceClient:
    """Get or create global HuggingFace client instance."""
    global _hf_client
    if _hf_client is None:
        _hf_client = HuggingFaceClient()
    return _hf_client