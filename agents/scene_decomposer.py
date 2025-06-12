# agents/scene_decomposer.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from graph.state import ComicGenerationState

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def scene_decomposer(state: ComicGenerationState) -> dict:
    """
    Node 2: Decomposes the story into a sequence of visual scenes for each panel.
    Returns scene descriptions for the requested number of comic panels.
    """
    print("---AGENT: Scene Decomposer---")

    story_text = state.get("story_text", "").strip()
    panel_count = state.get("panel_count", 6)

    if not story_text:
        raise ValueError("No story text found in state for scene decomposition.")

    print(f"   > Decomposing story into {panel_count} scenes...")

    system_prompt = (
        "You're a comic panel planner. Given a short story, break it into a JSON list of scenes. "
        "Each scene should contain:\n"
        "- panel (int): panel number\n"
        "- description (str): a short visual description of what to draw\n"
        "- caption (str, optional): narration or character dialogue\n\n"
        f"Limit to {panel_count} scenes max. Return JSON only, without markdown formatting."
    )

    user_prompt = f"Story:\n{story_text}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )


        content = response.choices[0].message.content.strip()
        scenes = json.loads(content)
        final_scenes = scenes[:panel_count]
        print("final scnenes:: " , final_scenes)

    except Exception as e:
        print("❌ Error parsing LLM output, using fallback scenes instead.\nError:", e)
        final_scenes = _fallback_scenes()[:panel_count]

    return {
        "scenes": final_scenes,
        "current_panel_index": 0,
        "panel_prompts": [],
        "panel_images": [],
    }

def _fallback_scenes():
    """Returns sample hardcoded scenes (for dev fallback)."""
    return [
        {
            "panel": 1,
            "description": "A lonely robot sits in a junkyard surrounded by twisted metal.",
            "caption": "Narrator: In the silence of scrap, hope sparked."
        },
        {
            "panel": 2,
            "description": "The robot finds a blooming flower among the debris.",
            "caption": "Robot: What... is this?"
        },
        {
            "panel": 3,
            "description": "The robot shelters the flower with a rusty umbrella as acid rain begins to fall.",
            "caption": "Narrator: Even steel can care."
        },
        {
            "panel": 4,
            "description": "More flowers begin sprouting around the robot in vibrant color.",
            "caption": ""
        },
        {
            "panel": 5,
            "description": "The robot stands in a now-green junkyard, smiling faintly.",
            "caption": "Robot: Beautiful."
        },
        {
            "panel": 6,
            "description": "A drone observes from afar, recording the moment.",
            "caption": "Drone Log: Emotional anomaly detected."
        }
    ]
