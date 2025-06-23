import os
from langgraph.graph import StateGraph, END
from models.comic_generation_state import ComicGenerationState
from configs import STORY_EXPANSION_WORD_THRESHOLD
import agents

def should_expand_story(state: ComicGenerationState) -> str:
    """Decides the initial routing of the workflow based on story length."""
    print("---CONDITION: Initial routing---")
    story_text = state.get("story_text", "")
    word_count = len(story_text.strip().split())

    if word_count < STORY_EXPANSION_WORD_THRESHOLD:
        print(f"   > Story is short ({word_count} words). Routing to story_generator.")
        return "expand_story"
    else:
        print(f"   > Story is long enough ({word_count} words). Routing to story_analyst.")
        return "analyze_story"

def should_continue_generating(state: ComicGenerationState) -> str:
    """Decides whether to continue generating panels or move to sizing and captioning."""
    print("---CONDITION: Should we continue generating panels?---")
    if state["current_panel_index"] < len(state["scenes"]):
        print(f"   > More panels to generate. Continuing loop. ({state['current_panel_index']} / {len(state['scenes'])})")
        return "continue_generation"
    else:
        print("   > All panels generated. Routing to panel sizer for batch processing.")
        return "process_all_panels"

def create_workflow():
    """Creates and compiles the LangGraph workflow with internalized routing."""
    workflow = StateGraph(ComicGenerationState)

    # Add all nodes to the graph
    workflow.add_node("story_generator", agents.story_generator)
    workflow.add_node("story_analyst", agents.story_analyst)
    workflow.add_node("scene_decomposer", agents.scene_decomposer)
    workflow.add_node("layout_planner", agents.layout_planner)
    workflow.add_node("prompt_engineer", agents.prompt_engineer)
    workflow.add_node("image_generator", agents.image_generator)
    workflow.add_node("panel_sizer", agents.panel_sizer)
    workflow.add_node("captioner", agents.captioner)
    workflow.add_node("page_composer", agents.page_composer)

    # 1. Set a conditional entry point to handle all initial routing
    workflow.set_conditional_entry_point(
        should_expand_story,
        {
            "expand_story": "story_generator",
            "analyze_story": "story_analyst",
        },
    )

    # 2. From story_generator, route directly to the story analyst
    workflow.add_edge("story_generator", "story_analyst")

    # 3. Define the main generation flow
    workflow.add_edge("story_analyst", "scene_decomposer")
    workflow.add_edge("scene_decomposer", "layout_planner")
    workflow.add_edge("layout_planner", "prompt_engineer")
    workflow.add_edge("prompt_engineer", "image_generator")

    # 4. Create the generation loop
    workflow.add_conditional_edges(
        "image_generator",
        should_continue_generating,
        {
            "continue_generation": "prompt_engineer",
            "process_all_panels": "panel_sizer",
        },
    )

    # 5. Define the post-generation sequential flow
    workflow.add_edge("panel_sizer", "captioner")
    workflow.add_edge("captioner", "page_composer")
    workflow.add_edge("page_composer", END)

    # Compile the workflow into a runnable app
    app = workflow.compile()
    return app