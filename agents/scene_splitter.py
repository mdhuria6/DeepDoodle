from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from utils.config import OPENAI_API_KEY

def scene_splitter(story: str) -> list:
    llm = ChatOpenAI(model="gpt-4o")
    prompt = f"Split the following story into scenes:\n{story}"
    result = llm.invoke([HumanMessage(content=prompt)])

    # Fix: use .content of the AIMessage
    text = result.content if hasattr(result, "content") else str(result)

    scenes = [s.strip() for s in text.split("\n") if s.strip()]
    return scenes