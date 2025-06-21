import re
import logging

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
