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
      {
        "panel": 1,
        "description": "A lonely astronomer, Elara, sits in a dark observatory, her face illuminated by a screen of static.",
        "captions": ["Elara: (Sighs) Another night, same old static..."]
      },
      {
        "panel": 2,
        "description": "Close-up on the monitor where the static is replaced by a single, perfect, glowing green sine wave. Two scientists are looking at it.",
        "captions": ["Scientist 1: What is that?", "Scientist 2: I've never seen anything like it!"]
      },
      {
        "panel": 3,
        "description": "A shocking image of a red giant star violently exploding in a supernova, sending a shockwave through space.",
        "captions": ["SFX: KABOOOM!", "Narrator: The universe trembled."]
      },
      {
        "panel": 4,
        "description": "Elara's face, a mix of terror and awe, as she realizes the signal and the supernova are connected.",
        "captions": ["Elara: It can't be... the signal... it's a countdown?"]
      },
      {
        "panel": 5,
        "description": "Years later, an older Elara stands on a lush, green alien planet, looking at a new sky. The air is filled with the scent of unknown, exotic flowers and the sounds of strange, melodic bird calls.",
        "captions": ["Elara: We made it. After all these years, and all those hardships, this new home seems like a paradise. I hope humanity can learn from its past mistakes here."]
      },
      {
        "panel": 6,
        "description": "A wide shot of a futuristic city on the new planet, with two suns in the sky, a symbol of a new beginning.",
        "captions": ["Narrator: And so, humanity found a new dawn, a chance to build again among the stars."]
      },
      {
        "panel": 7,
        "description": "Close-up on a futuristic data pad in Elara's hand showing the original green sine wave, now labeled 'The Invitation'. The screen flickers slightly, displaying complex astronomical data scrolling beneath the main message.",
        "captions": ["Datapad: Signal Source: Kepler-186f. Status: Welcoming. Additional telemetry indicates complex life forms and a breathable atmosphere. Proceed with cautious optimism and standard diplomatic protocols."]
      },
      {
        "panel": 8,
        "description": "Elara smiles, looking towards the horizon of the new world, full of hope. Another colonist stands beside her.",
        "captions": ["Elara: The start of a new adventure.", "Colonist: Indeed. A fresh start for us all."]
      }
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
