from langchain_core.prompts import PromptTemplate
import os

def load_prompt_template(prompt_folder: str, prompt_file: str, input_variables: list) -> PromptTemplate:
    """
    Load a LangChain PromptTemplate from a text file with {variable} placeholders.

    Args:
        prompt_folder (str): The folder containing the prompt file.
        prompt_file (str): The filename of the prompt template.
        input_variables (list): List of variables used in the template (e.g., ["story_text", "genre", "style"]).

    Returns:
        PromptTemplate: A LangChain PromptTemplate instance.
    """
    path = os.path.join(prompt_folder, prompt_file)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        template_string = f.read()

    return PromptTemplate(template=template_string, input_variables=input_variables)
