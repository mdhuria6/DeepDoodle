from models.comic_generation_state import ComicGenerationState # Updated import

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
        "description": "Elara in a space observatory, looking at a screen with static. Room has some equipment. Clear outlines, simple shapes.",
        "captions": [
            {"type": "caption", "speaker": "Narrator", "text": "The silent hum of the deep space observatory... a familiar vigil."},
            {"type": "dialogue", "speaker": "Elara", "text": "(Muttering to self) Years of this... just static..."}
        ]
      },
      {
        "panel": 2,
        "description": "Close up: Monitor screen shows a green sine wave through static. Elara's surprised face reflected. Simple line art.",
        "captions": [
            {"type": "caption", "speaker": "Narrator", "text": "Tonight, the void answered."},
            {"type": "sfx", "speaker": None, "text": "*Ping!*"}
        ]
      },
      {
        "panel": 3,
        "description": "Split panel: Left - Red alert lights in observatory. Right - Hologram of star exploding (supernova). Bold outlines.",
        "captions": [
            {"type": "sfx", "speaker": None, "text": "KLAXON! WARNING!"},
            {"type": "dialogue", "speaker": "Observatory AI (voiceover)", "text": "Catastrophic stellar event imminent! Red Giant 7GL-F, unscheduled detonation!"}
        ]
      },
      {
        "panel": 4,
        "description": "Elara looking at a transparent screen showing data: green sine wave over supernova shockwave. Clear, simple forms.",
        "captions": [
            {"type": "dialogue", "speaker": "Elara", "text": "The energy... it's being focused! The signal... it's riding the shockwave! An invitation..."}
        ]
      },
      {
        "panel": 5,
        "description": "Elara (grey streaks in hair) on an alien planet with two suns. Simple plants around. Wears explorer suit. Line art style.",
        "captions": [
            {"type": "caption", "speaker": "Narrator", "text": "The journey was long, the destination, a revelation."},
            {"type": "dialogue", "speaker": "Elara", "text": "(Awe-struck whisper) Incredible..."}
        ]
      },
      {
        "panel": 6,
        "description": "Wide shot: Alien city in distance under two suns. Sleek buildings, simple shapes. Minimal shading.",
        "captions": [
            {"type": "caption", "speaker": "Narrator", "text": "A civilization that had mastered the stars, and sent a welcome."}
        ]
      },
      {
        "panel": 7,
        "description": "Close up: Elara's hand holds a device showing a green sine wave on its screen. She smiles. Bold outlines.",
        "captions": [
            #{"type": "caption", "speaker": "Device Screen", "text": "Signal Source: Kepler-186f. Status: Welcome Home."},
            {"type": "dialogue", "speaker": "Elara", "text": "(Softly) So this is it. Home."}
        ]
      },
      {
        "panel": 8,
        "description": "Elara overlooking the alien city. Twin suns setting. Hopeful expression. Simple line art, clear landscape forms.",
        "captions": [
            {"type": "caption", "speaker": "Narrator", "text": "She was not just a discoverer, but the guest of honor. A new chapter for humanity, and for Elara, had begun."},
            {"type": "dialogue", "speaker": "Elara", "text": "Let's see what tomorrow brings."}
        ]
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
