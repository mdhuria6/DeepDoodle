from graph.state import ComicGenerationState

def scene_decomposer(state: ComicGenerationState) -> dict:
    """
    Node 2: Decomposes the story into a sequence of visual scenes for each panel.
    This is a placeholder for an LLM call.
    """
    print("---AGENT: Scene Decomposer---")

    # --- LLM Call Placeholder ---
    # llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)
    # prompt = f"""Read... STORY: {state['story_text']}... Decompose into {state['panel_count']} scenes... Return JSON array."""
    # response = llm.invoke(prompt)
    # scenes = json.loads(response.content)
    # --- End Placeholder ---

    # Placeholder result for demonstration
    print(f"   > Decomposing story into {state['panel_count']} scenes...")
    scenes = [
      {"panel": 1, "description": "A lonely astronomer, Elara, sits in a dark observatory, her face illuminated by a screen of static."},
      {"panel": 2, "description": "Close-up on the monitor where the static is replaced by a single, perfect, glowing green sine wave."},
      {"panel": 3, "description": "A shocking image of a red giant star violently exploding in a supernova, sending a shockwave through space."},
      {"panel": 4, "description": "Elara's face, a mix of terror and awe, as she realizes the signal and the supernova are connected."},
      {"panel": 5, "description": "Years later, an older Elara stands on a lush, green alien planet, looking at a new sky."},
      {"panel": 6, "description": "A wide shot of a futuristic city on the new planet, with two suns in the sky, a symbol of a new beginning."},
      {"panel": 7, "description": "Close-up on a futuristic data pad in Elara's hand showing the original green sine wave, now labeled 'The Invitation'."},
      {"panel": 8, "description": "Elara smiles, looking towards the horizon of the new world, full of hope."}
    ]

    # Ensure the number of scenes matches the requested panel count
    final_scenes = scenes[:state['panel_count']]

    # Initialize the state for the panel generation loop
    return {
        "scenes": final_scenes,
        "current_panel_index": 0,
        "panel_prompts": [],
        "panel_images": [],
    }
