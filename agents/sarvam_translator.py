import os
import re
from huggingface_hub import InferenceClient
from models.comic_generation_state import ComicGenerationState

_client = None
_model = "sarvamai/sarvam-m"

def get_sarvam_client():
    global _client
    if _client is None:
        token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not token:
            raise ValueError("HUGGINGFACE_API_TOKEN (Hugging Face API key) is not set.")
        _client = InferenceClient(
            provider="hf-inference",
            token=token)
    return _client

def sarvam_agent(state: ComicGenerationState) -> dict:
    """
    Agent entry point. Expects state to have 'prompt' and optionally 'target_language'.
    Returns a dict with the Sarvam model's output.
    """
    print(f"--- AGENT: Sarvam --- {state}")
    prompt = state.get("prompt", "")
    target_language = state.get("target_language", "English")

    if not prompt.strip():
        return {"sarvam_output": ""}

    if target_language == 'English':
        print(f"   > Sarvam output (no translation): {prompt}")
        return {"sarvam_output": prompt}

    client = get_sarvam_client()

    system_prompt = (
        f"You are an expert translator. Your task is to translate the user\'s text into {target_language}. "
        "Provide only the translated text. Do not shorten or summarize the original text. "
        "Translate the entire text accurately. "
        "Do not include any explanations, analysis, or extra formatting. "
        "Your entire response must be only the translation."
    )

    try:
        result = client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
        )
        output_text = result.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling Sarvam API: {e}")
        return {"sarvam_output": prompt} # Fallback to original prompt

    # --- Robust Parsing Logic ---
    content = ""
    if "</think>" in output_text:
        content = output_text.split("</think>")[-1].strip()
    else:
        quoted_translations = re.findall(r'["“]([^"”]+)["”]\'?', output_text)
        if quoted_translations:
            content = quoted_translations[-1].strip()
        else:
            lines = [line.strip() for line in output_text.split('\n') if line.strip()]
            if lines:
                content = lines[-1]
            else:
                content = output_text

    # Final cleanup of common prefixes
    prefixes_to_remove = [f"{target_language.lower()}:", "translation:"]
    for prefix in prefixes_to_remove:
        if content.lower().startswith(prefix):
            content = content[len(prefix):].strip()

    # Handle cases where the model echoes the prompt
    if content.strip('\'"') == prompt.strip():
        lines = [line.strip() for line in output_text.split('\n') if line.strip()]
        non_prompt_lines = [line for line in lines if line.strip('\'"') != prompt.strip()]
        if non_prompt_lines:
            content = non_prompt_lines[-1]

    print(f"   > Sarvam output: {content}")
    return {"sarvam_output": content}

