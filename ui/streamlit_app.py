import streamlit as st
import os
import shutil
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph.workflow import create_workflow
from utils.config import OUTPUT_DIR, PANELS_DIR, PAGES_DIR

# --- Page Configuration and Styling ---
st.set_page_config(page_title="DeepDoodle: AI Comic Generator", layout="wide", initial_sidebar_state="expanded")

# Inject custom CSS for better styling
st.markdown("""
    <style>
    /* Main container styling */
    .stApp {
        # background-color: #f0f2f6;
    }
    
    /* Center the title */
    h1 {
        text-align: center;
    }

    /* Improve button look */
    .stButton>button {
        border-radius: 10px;
        border: 2px solid #4A90E2;
        color: #4A90E2;
        font-weight: bold;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        border-color: #357ABD;
        background-color: #4A90E2;
        color: white;
    }
    .stButton>button:active {
        background-color: #357ABD;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)


st.title("✒️ DeepDoodle: AI Comic Generator")
st.markdown("<h4 style='text-align: center; color: #555;'>Turn your stories into visual comic strips with the power of AI Agents</h4>", unsafe_allow_html=True)
st.markdown("---")


def setup_directories():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(PANELS_DIR, exist_ok=True)

# --- Sidebar for Inputs ---
with st.sidebar:
    st.header("🎨 Story & Style")
    story_input = st.text_area("Write or paste your story here:", height=250, 
                               placeholder="A curious fox enters a haunted library...")
    
    style_options = ["auto", "Ghibli Animation", "Modern Anime", "Western Comic", "Minimalist Line Art"]
    style = st.selectbox("Select Visual Style", style_options)

    mood_options = ["auto", "Happy", "Dark & Brooding", "Mysterious", "Adventurous"]
    mood = st.selectbox("Select Mood", mood_options)
    
    st.header("📄 Page Layout")
    panel_count = st.slider("Number of Panels", min_value=1, max_value=8, value=4)
    layout_options = {
        "2x2 Grid": "grid_2x2", 
        "Horizontal Strip": "horizontal_strip",
        "Vertical Strip": "vertical_strip",
        "Featured Panel": "feature_left", 
        "Mixed Grid": "mixed_2x2"
    }
    selected_layout_name = st.selectbox("Select Panel Layout", list(layout_options.keys()))
    layout = layout_options[selected_layout_name]
    
    if panel_count < 3 and selected_layout_name == "Featured Panel":
        st.warning("'Featured Panel' layout requires at least 3 panels.")
    if panel_count < 4 and selected_layout_name in ["2x2 Grid", "Mixed Grid"]:
        st.warning(f"'{selected_layout_name}' layout requires at least 4 panels.")
    
    st.markdown("---")
    generate_button = st.button("✨ Generate Comic", use_container_width=True)

# --- Main Panel for Output ---
if 'result' not in st.session_state:
    st.session_state.result = None

if generate_button:
    is_valid = True
    if not story_input.strip():
        st.error("Please provide a story first!")
        is_valid = False
    if panel_count < 3 and selected_layout_name == "Featured Panel":
        is_valid = False
    if panel_count < 4 and selected_layout_name in ["2x2 Grid", "Mixed Grid"]:
        is_valid = False

    if is_valid:
        with st.spinner("🧙‍♂️ The AI agents are doodling... Please wait."):
            setup_directories()
            
            inputs = {
                "story_text": story_input,
                "panel_count": panel_count,
                "style_preset": style if style != "auto" else "Gritty Noir Comic Art",
                "genre_preset": mood if mood != "auto" else "Suspenseful",
                "layout_style": layout,
            }

            app = create_workflow()
            st.session_state.result = app.invoke(inputs)
    else:
        st.session_state.result = None

if st.session_state.result:
    result = st.session_state.result
    if result and result.get("final_page_images"):
        st.success("✅ Comic generated successfully!")
        
        # Create two columns to constrain the width of the comic page display
        col1, col2, col3 = st.columns([1, 6, 1]) 

        with col2: 
            # Display each page in a styled card
            for i, page_img in enumerate(result["final_page_images"]):
                with st.container(border=True): # Use border=True for a card effect
                    st.image(page_img, use_container_width=True)
                    st.markdown(f"<p style='text-align: center; color: #888;'>Page {i + 1}</p>", unsafe_allow_html=True)
        
        # Display individual panels in an expander with a grid layout
        with st.expander("Show Individual Panels"):
            cols = st.columns(4) 
            for idx, panel_path in enumerate(result["panel_image_paths"]):
                with cols[idx % 4]:
                    st.image(panel_path, caption=f"Panel {idx + 1}", use_container_width=True)

    else:
        st.error("❌ An error occurred. The agents failed to generate the comic.")
else:
    st.info("Fill in the details on the left and click 'Generate Comic' to see the magic!")