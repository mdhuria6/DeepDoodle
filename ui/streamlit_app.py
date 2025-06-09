import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph.comic_graph import graph  # assuming this runs your chain
from utils.config import OPENAI_API_KEY


st.set_page_config(page_title="DeepDoodle: AI Comic Generator", layout="wide")

st.title("DeepDoodle: Turn Stories into Comics")

# --- Left Sidebar: Input & Options ---
with st.sidebar:
    st.header("Story Input")

    story_input = st.text_area("Write or paste your story:", height=300, placeholder="e.g., A curious fox enters a haunted library...")

    st.markdown("---")

    st.header("Style Settings")
    mood = st.selectbox("Select Mood", ["auto", "happy", "dark", "mysterious"])
    style = st.selectbox("Select Visual Style", ["auto", "Ghibli", "Manga", "Western", "Minimalist"])
    panel_count = st.slider("Number of Panels", min_value=1, max_value=6, value=4)

    st.markdown("---")
    st.subheader("Load a Sample Story")
    if st.button("Load Sample"):
        story_input = "A small fox sets out on a journey through an enchanted forest to find the moonflower. Along the way, she meets a grumpy owl and a curious hedgehog."

    st.markdown("---")
    st.subheader("Export Options")
    export_pdf = st.checkbox("Export as PDF")

# --- Main Panel: Comic Output ---
if st.button("Generate Comic"):
    if not story_input.strip():
        st.error("Please provide a story first!")
    else:
        st.info("⏳ Generating comic, please wait...")
        
        # Execute LangGraph chain
        result = graph.invoke({
            "story": story_input,
            "mood": mood,
            "style": style,
            "panel_count": panel_count
        })

        if "panels" in result:
            st.success("✅ Comic generated!")
            for i, img_url in enumerate(result["panels"]):
                st.image(img_url, caption=f"Panel {i+1}", use_column_width=True)
        else:
            st.error("❌ Failed to generate comic panels.")

else:
    st.markdown("Use the sidebar to input your story and customize your comic.")

