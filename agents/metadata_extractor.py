from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from utils.config import OPENAI_API_KEY

def extract_metadata(story: str) -> dict:
    llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o")
    prompt = f"Identify mood, theme, and visual style for this story:\n{story}"
    response = llm.invoke(prompt)
    return {
        "mood": "serene",
        "theme": "fantasy",
        "style": "ghibli"
    }