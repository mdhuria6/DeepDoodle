def generate_prompts(scenes: list, style: str, mood: str) -> list:
    return [f"{scene}, in {style} style, with a {mood} mood" for scene in scenes]