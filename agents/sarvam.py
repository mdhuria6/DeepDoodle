import os
from huggingface_hub import InferenceClient

class SarvamAgent:
    def __init__(self, api_key='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', model="sarvamai/sarvam-m"):
        """
        Initialize SarvamAgent using Hugging Face Inference API.

        Args:
            api_key (str): Hugging Face API token (or set as HF_TOKEN env variable).
            model (str): Name of the model to use (default: sarvamai/sarvam-m).
        """
        self.api_key = api_key or os.getenv("HF_TOKEN")
        if not self.api_key:
            raise ValueError("HF_TOKEN (Hugging Face API key) is not set.")

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=self.api_key
        )
        self.model = model
        print(f"[SARVAM INIT] Using Hugging Face API for model: {self.model}")

    def run(self, prompt: str, target_language: str = None) -> str:
        """
        Generate a response from the Sarvam model using a prompt.

        Args:
            prompt (str): The input text to send to the model.
            target_language (str): Optional target output language (e.g., 'Hindi').

        Returns:
            str: The generated text from the model.
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        # Inject language instruction
        if target_language:
            prompt = f"Respond in {target_language}:\n{prompt}"

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message["content"].strip()
        except Exception as e:
            raise RuntimeError(f"API call failed: {e}")
