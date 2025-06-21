import re
import logging

logger = logging.getLogger(__name__)

class LLMUtils:
    @staticmethod
    def sanitize_llm_response(llm_content):
        llm_content = llm_content.strip()
        # Remove Markdown code block formatting if present
        if llm_content.lstrip().startswith("```"):
            logger.info("Detected Markdown code block formatting in LLM response.")
            llm_content = re.sub(r"^```[a-zA-Z]*\n?", "", llm_content)
            llm_content = re.sub(r"\n?```$", "", llm_content)
            llm_content = llm_content.strip()
        return llm_content
