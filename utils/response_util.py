import re
import logging
import json

logger = logging.getLogger(__name__)

@staticmethod
def sanitize_llm_response(response):
    print("Sanitizing LLM response...")
    response = response.strip()
    print(f"Initial response: {response}")
    # Remove Markdown code block formatting if present
    if response.lstrip().startswith("```"):
        logger.info("Detected Markdown code block formatting in LLM response.")
        response = re.sub(r"^```[a-zA-Z]*\n?", "", response)
        response = re.sub(r"\n?```$", "", response)
        response = response.strip()
    return response

@staticmethod
def sanitize_llm_response_scene_decomposer(response):
    print("Sanitizing LLM response...")
    response = response.strip()
    print(f"Initial response: {response}")
    # Remove Markdown code block formatting if present
    start_index = response.find("[")
    end_index = response.rfind("]") + 1
    json_string = response[start_index:end_index]
    json_string = re.sub(r"(\d)'\d{1,2}\"", lambda m: m.group(0).replace('"', '\\"'), json_string)
    return json_string

@staticmethod
def sanitize_llm_response_character_description(response):
    print("Sanitizing LLM response...")
    response = response.strip()
    print(f"Initial response: {response}")
    # Remove Markdown code block formatting if present
    start_index = response.find("{")
    end_index = response.rfind("}") + 1
    json_string = response[start_index:end_index]
    json_string = re.sub(r"(\d)'\d{1,2}\"", lambda m: m.group(0).replace('"', '\\"'), json_string)
    return json_string


def sanitize_story_output(text: str) -> str:
    """
    Cleans up LLM-generated story output by removing unwanted lines and characters.
    """
    text = text.strip()
    lines = text.splitlines()
    lines = [line for line in lines if not re.match(r"^\s*-{2,}\s*$", line)]
    cleaned = "\n".join(lines).strip()
    return cleaned