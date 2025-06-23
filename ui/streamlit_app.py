import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import streamlit as st
from PIL import Image
import shutil # Added shutil import

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configs import STORY_EXPANSION_WORD_THRESHOLD, PROMPT
from main import run_comic_generation_workflow #type: ignore
from configs import (
    DEFAULT_LAYOUT_STYLE, SUPPORTED_LAYOUT_STYLES, 
    DEFAULT_STYLE_PRESET, SUPPORTED_STYLE_PRESETS, 
    DEFAULT_GENRE_PRESET, SUPPORTED_GENRE_PRESETS,
    OUTPUT_DIR, COMIC_PAGES_DIR, RAW_PANELS_DIR # Added missing imports
) #type: ignore
from models.comic_generation_state import ComicGenerationState # Import from models

# --- Page Configuration ---
# Constants for layout options
LAYOUT_2X2_GRID = "2x2 Grid"
LAYOUT_FEATURED_PANEL = "Featured Panel"
LAYOUT_MIXED_GRID = "Mixed Grid"
LAYOUT_HORIZONTAL_STRIP = "Horizontal Strip"
LAYOUT_VERTICAL_STRIP = "Vertical Strip"

st.set_page_config(page_title="DeepDoodle: AI Comic Generator", layout="wide", initial_sidebar_state="expanded")

# --- CSS Styling ---
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

# --- Title and Subtitle ---
st.title("✒️ DeepDoodle: AI Comic Generator")
st.markdown("<h4 style='text-align: center; color: #555;'>Turn your stories into visual comic strips with the power of AI Agents</h4>", unsafe_allow_html=True)
st.markdown("---")

# --- Directory Setup ---
def setup_directories():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(COMIC_PAGES_DIR, exist_ok=True)
    os.makedirs(RAW_PANELS_DIR, exist_ok=True)

# --- Sidebar for Inputs ---
with st.sidebar:
    st.header("⚙️ Model Configuration")
    text_engine_options = {
        "OpenAI (gpt-4o)": "openai_gpt4o",
        "OpenAI (gpt-4-turbo)": "openai_gpt4",
        "Mistral AI (Mixtral-8x7B-Instruct)": "mistral_mixtral_8x7b_instruct",
        "Google (Gemini 1.5 Flash)": "gemini_1.5_flash",
    }
    selected_text_engine_name = st.selectbox("Select Text Engine", list(text_engine_options.keys()))
    text_engine = text_engine_options[selected_text_engine_name]

    image_engine_options = {
        "Black Forest Labs (FLUX.1-schnell)": "flux.1-schnell",
        "Stability AI (stable-diffusion-2-1)": "sd21",
    }
    selected_image_engine_name = st.selectbox("Select Image Engine", list(image_engine_options.keys()))
    image_engine = image_engine_options[selected_image_engine_name]

    st.header("🎨 Story & Style")
    story_input = st.text_area("Write or paste your story here:", height=250, 
                               placeholder="A curious fox enters a haunted library...")
    
    # Updated style_options to match keys from STYLE_CONFIGS
    # Assuming 'auto' is still desired as an option for future development or default handling
    style_options = ["auto", "Simple Line Art Comic", "Black and White Manga", "Ghibli Animation", "Modern Anime", "Classic Western Comic"]
    style = st.selectbox("Select Visual Style", style_options, index=0) # Default to 'auto'

    mood_options = ["auto", "Sci-Fi", "Fantasy", "Horror", "Comedy", "Drama", "Mystery", "Adventure", "Whimsical", "Noir", "Cyberpunk", "Steampunk"]
    mood = st.selectbox("Select Mood", mood_options, index=0) # Default to 'auto'
    
    # --- Add Sarvam language dropdown here ---
    sarvam_languages = [
        "English", "Hindi", "Tamil", "Telugu"
    ]
    selected_sarvam_language = st.selectbox("Select Sarvam Output Language", sarvam_languages, index=0)
    # -----------------------------------------

    st.header("📄 Page Layout")
    panel_count = st.slider("Number of Panels", min_value=1, max_value=8, value=4)
    layout_options = {
        LAYOUT_2X2_GRID: "grid_2x2", 
        LAYOUT_HORIZONTAL_STRIP: "horizontal_strip",
        LAYOUT_VERTICAL_STRIP: "vertical_strip",
        LAYOUT_FEATURED_PANEL: "feature_left", 
        LAYOUT_MIXED_GRID: "mixed_2x2"
    }
    selected_layout_name = st.selectbox("Select Panel Layout", list(layout_options.keys()))
    layout = layout_options[selected_layout_name]
    
    if panel_count < 3 and selected_layout_name == LAYOUT_FEATURED_PANEL:
        st.warning(f"'{LAYOUT_FEATURED_PANEL}' layout requires at least 3 panels.")
    if panel_count < 4 and selected_layout_name in [LAYOUT_2X2_GRID, LAYOUT_MIXED_GRID]:
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
    if panel_count < 3 and selected_layout_name == LAYOUT_FEATURED_PANEL:
        is_valid = False
    if panel_count < 4 and selected_layout_name in [LAYOUT_2X2_GRID, LAYOUT_MIXED_GRID]:
        is_valid = False

    if is_valid:
        with st.spinner("🧙‍♂️ The AI agents are doodling... Please wait."):
            setup_directories()
            from graph.workflow import create_workflow # Lazy import
            inputs = {
                "story_text": story_input,
                "panel_count": panel_count,
                "style_preset": style,
                "genre_preset": mood,
                "layout_style": layout,
                "text_engine": text_engine,
                "image_engine": image_engine,
                "prompt": PROMPT,
                "target_language": selected_sarvam_language,
            }
            word_count = len(story_input.strip().split())
            # Create and run the workflow
            if word_count < STORY_EXPANSION_WORD_THRESHOLD:
                entry = "story_generator"
            else:
                if PROMPT == "Simple":
                    entry = "story_analyst"
                elif PROMPT == "Detailed":
                    entry = "detailed_story_analyst"
                else:
                    raise ValueError("Incorrect prompt. Expected 'Simple' or 'Detailed'.")
            app = create_workflow(entry)
            st.session_state.result = app.invoke(inputs, {"recursion_limit": 100})
    else:
        st.session_state.result = None

if st.session_state.result:
    result = st.session_state.result
    if result and result.get("final_page_images"):
        st.success("Comic generated successfully!")
        
        # Create two columns to constrain the width of the comic page display
        col1, col2, col3 = st.columns([1, 6, 1]) 

        with col2: 
            # Display each page in a styled card
            for i, page_img in enumerate(result["final_page_images"]):
                with st.container(border=True): # Use border=True for a card effect
                    st.image(page_img, use_container_width=True)
                    st.markdown(f"<p style='text-align: center; color: #888;'>Page {i + 1}</p>", unsafe_allow_html=True)
        
        # Display individual panels in an expander with a grid layout
        with st.expander("Show Individual Panels & Validation"):
            cols = st.columns(4)
            validation_results = result.get("validation_scores")

            for idx, panel_path in enumerate(result["panel_image_paths"]):
                with cols[idx % 4]:
                    st.image(panel_path, caption=f"Panel {idx + 1}", use_container_width=True)

                    # commented out validation code for now
                    if validation_results and idx < len(validation_results):
                        validation = validation_results[idx]
                        st.markdown(
                            f"**Score:** {validation.get('final_score', 'N/A')}<br>"
                            f"**Decision:** {validation.get('final_decision', 'N/A')}",
                            unsafe_allow_html=True
                        )
                    else:
                        st.info("No validation score available.")

    else:
        st.error("An error occurred. The agents failed to generate the comic.")
else:
    st.info("Fill in the details on the left and click 'Generate Comic' to see the magic!")