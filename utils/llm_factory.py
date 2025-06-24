import os
from langchain_openai import ChatOpenAI
from huggingface_hub import InferenceClient
import boto3
import json
import base64
import io
from PIL import Image
import random

class ModelWrapper:
    def __init__(self, engine, engine_type, model_name=None, is_image_model=False):
        self.engine = engine
        self.engine_type = engine_type
        self.model_name = model_name
        self.is_image_model = is_image_model

    def generate_text(self, prompt, **kwargs):
        if self.is_image_model:
            raise ValueError("This is an image model. Use generate_image().")
        if self.engine_type == "openai" or self.engine_type == "gemini":
            response = self.engine.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        elif self.engine_type == "huggingface":
            model = self.model_name or kwargs.get("model", "mistralai/Mixtral-8x7B-Instruct-v0.1")
            max_tokens = kwargs.get("max_tokens", 10000)
            temperature = kwargs.get("temperature", 0.4)
            top_p = kwargs.get("top_p", 0.9)
            return self.engine.text_generation(
                prompt,
                model=model,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                return_full_text=False
            )
        else:
            raise ValueError(f"Unknown LLM engine type: {self.engine_type}")

    def generate_image(self, prompt, **kwargs):
        if not self.is_image_model:
            raise ValueError("This is a text model. Use generate_text().")
        
        if self.engine_type == "huggingface":
            model = self.model_name or kwargs.get("model", "stabilityai/stable-diffusion-2-1")
            # Accepts prompt, model, and other kwargs for image generation
            return self.engine.text_to_image(
                prompt,
                model=model,
                **kwargs
            )
        elif self.engine_type == "bedrock":
            bedrock_client = self.engine
            target_w = kwargs.get("width", 1024)
            target_h = kwargs.get("height", 1024)
            negative_prompt = kwargs.get("negative_prompt", "")

            # Only supporting Stability models for now
            if "stability.stable-diffusion" in self.model_name:
                request_body = {
                    "cfg_scale": 8, "steps": 40, "seed": random.randint(0, 1000000),
                    "text_prompts": [
                        {"text": prompt, "weight": 1.0},
                        {"text": negative_prompt, "weight": -1.0}
                    ],
                    "height": target_h, "width": target_w,
                }
            else:
                raise ValueError(f"Unsupported Bedrock model ID for factory: {self.model_name}")

            body = json.dumps(request_body)
            response = bedrock_client.invoke_model(
                body=body, modelId=self.model_name, accept='application/json', contentType='application/json'
            )
            response_body = json.loads(response.get('body').read())

            base64_image_data = response_body.get('artifacts')[0].get('base64')
            
            if not base64_image_data:
                raise ValueError("No image data found in Bedrock response.")

            image_bytes = base64.b64decode(base64_image_data)
            return Image.open(io.BytesIO(image_bytes))
        else:
            raise ValueError(f"Image generation not supported for engine type: {self.engine_type}")


def get_model_client(request_type: str = "text", engine_name: str = "mistral_mixtral_8x7b_instruct"):
    """
    Factory function to get an instance of a model client (text or image) based on the request type and engine name.
    request_type: 'text' or 'image'
    engine_name: e.g. 'openai_gpt4', 'mistral_mixtral', 'hf_diffusion', 'bedrock_stability.stable-diffusion-xl-v1'
    """
    print(f"---Model Factory: Creating {request_type} client for {engine_name}---")

    if request_type == "text":
        if engine_name == "mistral_mixtral_8x7b_instruct":
            hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
            if not hf_token:
                raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set.")
            model_name = "mistralai/Mixtral-8x7B-Instruct-v0.1"
            client = InferenceClient(token=hf_token)
            return ModelWrapper(client, "huggingface", model_name=model_name, is_image_model=False)
        elif engine_name == "openai_gpt4o":
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY environment variable not set.")
            client = ChatOpenAI(model="gpt-4o", temperature=0.4)
            return ModelWrapper(client, "openai", model_name="gpt-4o", is_image_model=False)
        elif engine_name == "gemini_1.5_flash":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
            except ImportError:
                raise ImportError("langchain-google-genai is required for Gemini Flash support. Please install it via 'pip install langchain-google-genai'.")
            google_api_key = os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set.")
            # Gemini Flash model name is 'gemini-1.5-flash-latest' (as per Google API)
            client = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=google_api_key, temperature=0.4)
            return ModelWrapper(client, "gemini", model_name="gemini-1.5-flash-latest", is_image_model=False)
        else:
            print(f"Warning: Unknown text engine '{engine_name}'. Defaulting to mistral_mixtral")
            hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
            if not hf_token:
                raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set.")
            model_name = "mistralai/Mixtral-8x7B-Instruct-v0.1"
            client = InferenceClient(token=hf_token)
            return ModelWrapper(client, "huggingface", model_name=model_name, is_image_model=False)

    elif request_type == "image":
        if engine_name.startswith("bedrock_"):
            model_id = engine_name.replace("bedrock_", "")
            aws_region = os.getenv("BEDROCK_AWS_REGION", "us-east-1")
            try:
                bedrock_client = boto3.client(service_name='bedrock-runtime', region_name=aws_region)
                return ModelWrapper(bedrock_client, "bedrock", model_name=model_id, is_image_model=True)
            except Exception as e:
                raise ValueError(f"Failed to create Bedrock client: {e}")
        else:
            # Default: Hugging Face diffusion model
            hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
            if not hf_token:
                raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set.")
            if engine_name == "sd21" or engine_name == "hf_diffusion":
                model_name = "stabilityai/stable-diffusion-2-1"
            elif engine_name == "flux.1-schnell":
                model_name = "black-forest-labs/FLUX.1-schnell"
            else:
                print(f"Warning: Unknown image engine '{engine_name}'. Defaulting to SD 2.1.")
                model_name = "stabilityai/stable-diffusion-2-1"
            client = InferenceClient(token=hf_token)
            return ModelWrapper(client, "huggingface", model_name=model_name, is_image_model=True)
    else:
        raise ValueError(f"Unknown request_type '{request_type}'. Use 'text' or 'image'.")