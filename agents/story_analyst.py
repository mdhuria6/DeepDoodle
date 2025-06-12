from models.comic_generation_state import ComicGenerationState # Updated import

def story_analyst(state: ComicGenerationState) -> dict:
    """Analyzes the story and sets up initial style, mood, and character."""
    print("---AGENT: Story Analyst---")

    # Define a consistent character description based on the new story
    character_description = "Elara, a veteran astronomer, with hair streaked with grey later in the story."
    print(f"   > Character Defined: {character_description}")

    # Pass through the style and mood from the input state.
    # The prompt engineer expects the key 'artistic_style'.
    # Ensure these keys match ComicGenerationState and Streamlit inputs
    artistic_style = state.get('style_preset', 'default comic style') 
    mood = state.get('genre_preset', 'neutral')
    layout_style = state.get('layout_style', 'grid_2x2')

    print(f"   > Style set to: {artistic_style}")
    print(f"   > Mood set to: {mood}")
    print(f"   > Layout style set to: {layout_style}")

    # Return all the necessary keys for the downstream nodes.
    return {
        "character_description": character_description,
        "artistic_style": artistic_style,
        "mood": mood,
        "layout_style": layout_style
    }