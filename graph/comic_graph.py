from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict, Any
from agents.scene_splitter import scene_splitter
from agents.metadata_extractor import extract_metadata
from agents.prompt_generator import generate_prompts
from agents.image_generator import generate_image  # updated import (singular)
from agents.character_memory import manage_character_memory
from agents.renderer import render_comic

class ComicState(TypedDict):
    story: str
    scenes: List[str]
    metadata: Dict[str, str]
    prompts: List[str]
    images: List[str]
    memory: Dict[str, Any]
    output: str

builder = StateGraph(ComicState)

builder.add_node("split", lambda state: {**state, "scenes": scene_splitter(state["story"])})
builder.add_node("meta", lambda state: {**state, "metadata": extract_metadata(state["story"])})
builder.add_node("prompt", lambda state: {**state, "prompts": generate_prompts(state["scenes"], state["metadata"]["style"], state["metadata"]["mood"])})

# NEW: generate images one by one using huggingface inference API
def generate_images_hf(state):
    prompts = state.get("prompts", [])
    style = state.get("metadata", {}).get("style", "manga")
    images = []
    for prompt in prompts:
        img_path = generate_image(prompt, style)
        images.append(img_path)
    return {**state, "images": images}

builder.add_node("image", generate_images_hf)

builder.add_node("character_memory_node", lambda state: {**state, "memory": manage_character_memory(state["images"])})
builder.add_node("render", lambda state: {**state, **render_comic(state["images"])})

builder.set_entry_point("split")
builder.add_edge("split", "meta")
builder.add_edge("meta", "prompt")
builder.add_edge("prompt", "image")
builder.add_edge("image", "character_memory_node")
builder.add_edge("character_memory_node", "render")
builder.set_finish_point("render")

graph = builder.compile()