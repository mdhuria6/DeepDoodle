from graph.state import ComicGenerationState
from openai import OpenAI
from dotenv import load_dotenv
import os
import random

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Predefined fallback sets
KNOWN_GENRES = ["Sci-Fi", "Fantasy", "Comedy", "Mysterious", "Drama", "Adventure"]
KNOWN_STYLES = ["Western Comic", "Manga", "Digital Painting", "Cartoon", "Ink Sketch"]

def story_analyst(state: ComicGenerationState) -> dict:
    print("---AGENT: Story Analyst---")

    story_text = state.get("story_text", "")
    word_count = len(story_text.split())
    genre = state.get("genre_preset", "auto")
    style = state.get("style_preset", "auto")
    panel_count = int(state.get("panel_count", 4))
    layout_style = state.get("layout_style", "grid_2x2")

    # Generate a longer story if the input is too short
    if word_count < 50:
        print(f"   > Short input detected ({word_count} words). Expanding story...")
        expansion_prompt = (
            f"Write a {genre} short story titled '{story_text}' "
            f"with {panel_count} visual scenes. Use 100-200 words."
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're a creative short story writer."},
                {"role": "user", "content": expansion_prompt}
            ]
        )
        story_text = response.choices[0].message.content.strip()

    print(f"   > Final Genre: " + genre)
    print(f"   > Final Style: " + style)
        
    return {
        "story_text": story_text,
        "character_description": "A curious protagonist caught in a strange "+ genre,
        "artistic_style": style,
        "mood": genre,
        "layout_style": layout_style,
    }
