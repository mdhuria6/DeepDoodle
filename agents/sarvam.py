import os
from huggingface_hub import InferenceClient
from models.comic_generation_state import ComicGenerationState

_client = None
_model = "sarvamai/sarvam-m"

def get_sarvam_client():
    global _client
    if _client is None:
        api_key = os.getenv("HF_TOKEN")
        if not api_key:
            raise ValueError("HF_TOKEN (Hugging Face API key) is not set.")
        _client = InferenceClient(
            provider="hf-inference",
            api_key=api_key)
    return _client

def sarvam_agent(state: ComicGenerationState) -> dict:
    """
    Agent entry point. Expects state to have 'prompt' and optionally 'target_language'.
    Returns a dict with the Sarvam model's output.
    """
    print("--- AGENT: Sarvam ---", state)
    prompt = state.get("prompt", "")
    target_language = state.get("target_language", None)
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")
    if target_language:
        # prompt = f"Translate the following to {target_language}. Only translate, do not explain or add anything else.:\n{prompt}"
        client = get_sarvam_client()
        # Use text_generation for Hugging Face models
        # result = client.text_generation(prompt, model=_model)
        result = client.chat.completions.create(
                    model=_model,
                    messages=[
                        {"role": "system", "content": f"Translate the text below to {target_language}.NEGATIVE PROMT: Only return the full translated text. DO NOT GIVE ME THE EXPLAINATION AND THINKING"},
                        {"role": "user", "content": prompt}
                    ],
                )
        output_text = result.choices[0].message.content
        if "</think>" in output_text:
            reasoning_content = output_text.split("</think>")[0].rstrip("\n")
            content = output_text.split("</think>")[-1].lstrip("\n")
        else:
            reasoning_content = ""
            content = output_text
    print(f"   > Sarvam output type: {content}")
    return {"sarvam_output": content}

