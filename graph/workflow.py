from langgraph.graph import StateGraph, END
from models.comic_generation_state import ComicGenerationState # Import from models
import agents
from configs import STORY_EXPANSION_WORD_THRESHOLD

def should_expand_story(state: ComicGenerationState) -> str:
    story_text = state.get("story_text", "")
    word_count = len(story_text.strip().split())
    if word_count < STORY_EXPANSION_WORD_THRESHOLD:
        return "short_prompt"
    else:
        return "full_story"


def should_continue_generating(state: ComicGenerationState) -> str:
    """Decides whether to continue generating panels or compose pages."""
    print("---CONDITION: Should we continue generating panels?---")
    if state["current_panel_index"] < len(state["scenes"]):
        print("   > YES, more panels to generate.")
        return "continue_generation"
    else:
        print("   > NO, all panels have been generated.")
        return "compose_pages"

def create_workflow(entry_point: str = "story_analyst"):
    """Creates and compiles the LangGraph workflow."""
    workflow = StateGraph(ComicGenerationState)
    workflow.add_node("story_analyst", agents.story_analyst)
    workflow.add_node("story_generator", agents.story_generator)
    workflow.add_node("scene_decomposer", agents.scene_decomposer)
    workflow.add_node("layout_planner", agents.layout_planner)
    workflow.add_node("prompt_engineer", agents.prompt_engineer)
    workflow.add_node("image_generator", agents.image_generator)
    workflow.add_node("image_validator", agents.image_validator)
    workflow.add_node("panel_sizer", agents.panel_sizer) 
    workflow.add_node("captioner", agents.captioner) 
    workflow.add_node("page_composer", agents.page_composer)
    # workflow.add_node("sarvam", agents.sarvamAgent)
    
    workflow.set_entry_point(entry_point)
    workflow.add_edge("story_generator", "story_analyst") # story_generator goes to story_analyst
    workflow.add_edge("story_analyst", "scene_decomposer") # story_analyst goes to scene_decomposer
    workflow.add_edge("scene_decomposer", "layout_planner") # scene_decomposer now goes to layout_planner
    workflow.add_edge("layout_planner", "prompt_engineer") # layout_planner goes to prompt_engineer
    workflow.add_edge("prompt_engineer", "image_generator")
    workflow.add_edge("image_generator", "image_validator")
    
    # After image_validator, decide if more panels or move to panel_sizer_agent
    workflow.add_conditional_edges(
        "image_validator",
        should_continue_generating,
        {
            "continue_generation": "prompt_engineer", 
            "compose_pages": "panel_sizer"
        }
    )

    # After panel_sizer, go to captioner
    workflow.add_edge("panel_sizer", "captioner") # Renamed
    # After captioner, go to page_composer
    workflow.add_edge("captioner", "page_composer") # Renamed
    workflow.add_edge("page_composer", END)
    return workflow.compile()