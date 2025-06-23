# 🖼️ DeepDoodle: AI-Powered Comic Generator

DeepDoodle is an Agentic AI framework that transforms natural language stories into illustrated, style-consistent comic panels. 

---
## 📜 Abstract:
In today’s visually driven digital culture, many rich narratives ranging from ancient folk tales to personal memories and imaginative ideas often remain confined to text, limiting their reach and experiential impact. Enabling users to visualize these stories as immersive visual narratives can inspire creativity, preserve cultural heritage, and engage younger, media savvy audiences. We introduce an agentic AI framework that transforms such rich texts into fully illustrated, style-consistent comic panels, enabling end-to-end visual storytelling from natural language. The system accepts user-provided inputs including the story, genre, artistic style, and desired panel count. In the absence of any of these, dedicated agents automatically infer the narrative mood, assign thematic tags, suggest a visual style, and segment the story into coherent scenes. The architecture is composed of modular agents orchestrated using LangChain responsible for metadata extraction, narrative decomposition, prompt engineering, and image generation. Leveraging LLMs, Stable Diffusion XL, the system generates and stylizes story panels based on detailed visual prompts. These panels are composed with consistency in character identity and setting maintained throughout the narrative. Designed with modularity and extensibility in mind, the framework supports multilingual storytelling, artistic style adaptation, and scalable deployment. Potential applications span digital storytelling, education, visual media, and cultural preservation.

---

## 🔧 Project Structure

```
DeepDoodle/
│
├── main.py                      # CLI entry point for comic generation (runs the workflow)
├── requirements.txt             # Python dependencies
├── .env                         # API keys and environment variables
├── README.md                    # Project documentation
│
├── agents/                      # Modular AI agent implementations (each is a workflow node)
│   ├── __init__.py
│   ├── story_generator.py       # Expands a short user prompt into a full story
│   ├── story_analyst.py         # Analyzes story, extracts genre/style/mood
│   ├── detailed_story_analyst.py# Analyzes a detailed story for key elements
│   ├── scene_decomposer.py      # Splits story into visual scenes/panels
│   ├── layout_planner.py        # Determines panel dimensions and page layouts
│   ├── prompt_engineer.py       # Crafts prompts for image generation
│   ├── image_generator.py       # Generates panel images at target dimensions
│   ├── image_validator.py       # (Async) Validates generated images for quality
│   ├── panel_sizer.py           # Resizes/crops raw panels to ideal dimensions from layout plan
│   ├── captioner.py             # Adds captions/text to sized panels
│   ├── page_composer.py         # Stitches panels onto pages using offsets from layout plan
│   └── sarvam.py                # Handles text translation for multi-language support
│
├── configs/                     # Configuration files for different aspects of the project
│   ├── __init__.py
│   ├── base_config.py           # Core project settings (API keys, root path)
│   ├── image_opts_config.py     # Image generation options
│   ├── llm_api_config.py        # LLM provider configurations
│   ├── paths_config.py          # Directory and file paths
│   ├── prompt_styles.py         # Style presets for prompt engineering
│   ├── story_elements_config.py # Story-related configurations
│   ├── text_style_config.py     # Caption and text styling
│   └── ui_options_config.py     # Options for the Streamlit UI
│
├── graph/                       # Workflow orchestration (LangGraph)
│   ├── __init__.py
│   └── workflow.py              # Defines the LangGraph state machine and agent connections
│
├── models/                      # Data structures and type definitions (TypedDicts)
│   ├── __init__.py
│   ├── comic_generation_state.py # Defines the main state object for the graph
│   ├── panel_layout_detail.py   # Details for each panel's layout
│   ├── scene.py                 # A single panel's description and captions
│   ├── caption.py               # A single caption's text, speaker, and type
│   └── caption_style_metadata.py# Styling information for captions
│
├── utils/                       # Shared utility functions
│   ├── __init__.py
│   ├── caption_util.py          # Functions for drawing and styling captions
│   ├── layout_util.py           # Comic page layout and composition functions
│   ├── llm_factory.py           # Factory for creating different LLM clients
│   ├── load_prompts.py          # Helper to load prompt templates from files
│   ├── metrics.py               # Evaluation metrics (e.g., ROUGE, BERTScore)
│   └── response_util.py         # Utilities for parsing and cleaning LLM responses
│
├── output/                      # Generated images (created at runtime)
│   ├── panels/                  # Raw individual panel images from image_generator
│   ├── panels_sized/            # Panels after sizing by panel_sizer
│   ├── panels_with_captions/    # Panels after captioning by captioner
│   └── pages/                   # Final composed comic pages
│
├── ui/                          # Streamlit web interface
│   ├── __init__.py
│   └── streamlit_app.py         # Streamlit app for interactive comic generation
│
├── prompts/                     # Text files containing prompts for LLM agents
│   └── ...
│
├── data/                        # Sample data and stories
│   └── samples/
│       └── example_story.txt
│
└── test/                        # Test scripts
    └── ...
```

---

## ▶️ Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/DeepDoodle.git
cd DeepDoodle
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

#### 3.1. Special Instructions for Pillow (Text Shaping)

For optimal text rendering, especially for complex scripts, Pillow should be compiled with `libraqm` support.

**On macOS:**

1.  **Install dependencies for `libraqm`**:
    ```bash
    brew install freetype harfbuzz fribidi
    ```
2.  **Install `libraqm`**:
    ```bash
    brew install libraqm
    ```
3.  **Reinstall Pillow from source**:
    It's crucial to reinstall Pillow after `libraqm` is available to ensure it's detected during the build.
    ```bash
    pip uninstall Pillow -y
    pip install Pillow --no-cache-dir --no-binary :all: --verbose
    ```
    During the verbose output of the Pillow installation, look for a line confirming "RAQM (Text shaping) support available".

**On Linux (Debian/Ubuntu):**

1.  **Install dependencies for `libraqm`**:
    ```bash
    sudo apt-get install libfreetype6-dev libharfbuzz-dev libfribidi-dev libjpeg-dev libtiff5-dev liblcms2-dev
    ```
2.  **Install `libraqm`**:
    ```bash
    sudo apt-get install libraqm-dev
    ```
3.  **Reinstall Pillow from source**:
    ```bash
    pip uninstall Pillow -y
    pip install Pillow --no-cache-dir --no-binary :all: --verbose
    ```
    Check for "RAQM (Text shaping) support available" in the build log.

**Font Selection for Text Rendering:**
Equally important as `libraqm` support is the choice of font. The font used for rendering text (e.g., in captions) **must contain the glyphs for the specific language or script** you intend to use. If the font lacks the necessary glyphs, you may see empty boxes (tofu) or incorrect characters. For example, to render Arabic text, use a font like "Noto Sans Arabic" or another font with comprehensive Arabic support. Ensure the `font_path` in your project's configuration (e.g., `utils/config.py` or relevant scripts) points to such a font file.

**Verification (Optional but Recommended):**

After installation, you can run the `verify_text_shaping.py` script (located in `test/setup/`) to check if Pillow has RAQM support and can render a sample of complex text:
```bash
python test/setup/verify_text_shaping.py
```
This will create an image `text_shaping_verification.png` in the root directory. Open it to visually confirm.

### 4. Add environment variables
Create a `.env` file in the root directory with this content:
```env
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_TOKEN=your_hf_token
```

### 5. (Optional) Place sample images
Put some sample images `sample-panel-<i>.png` in the `output/panels/` folder if you want to test parts of the UI or pipeline with static images.

### 6. Run the Streamlit app
```bash
streamlit run ui/streamlit_app.py
```

---

## 🧠 Features

- **Story Generator**: If the user provides a short prompt, this agent expands it into a complete story.
- **Story Analyst**: Analyzes the story to extract key elements like genre, artistic style, mood, and character descriptions.
- **Scene Decomposer**: Breaks down the full story into a sequence of distinct scenes, with one scene corresponding to one comic panel.
- **Layout Planner**: Determines the detailed layout for each panel on each page, including ideal dimensions for final placement, target dimensions for image generation (multiple of 64), and precise x/y offsets for composition. It prioritizes UI-selected layouts and dynamically adapts for remaining panels.
- **Prompt Engineer**: Converts scene descriptions and style metadata into detailed, effective prompts for the image generation model.
- **Image Generator**: Generates an image for each panel based on its prompt, adhering to the target dimensions specified by the `Layout Planner`.
- **Image Validator**: (Asynchronous) Runs after image generation to check for common issues like blank or corrupted images. This step is designed not to block the main workflow.
- **Panel Sizer**: Takes the generated images and resizes/crops them to the ideal dimensions defined in the layout plan, preparing them for final page composition.
- **Captioner**: Renders dialogue, narration, and sound effects onto the sized panel images.
- **Page Composer**: Arranges the sized and captioned panels onto a blank page according to the ideal dimensions and x/y offsets provided by the `Layout Planner`.
- **Sarvam Translator**: Provides multi-language support by translating caption text on-the-fly.
- **LangGraph-based Orchestration**: Uses a state machine to manage the flow of data and control the execution of agents, enabling complex conditional logic and loops.

---

## 📌 Notes
- Requires valid OpenAI and HuggingFace API keys for full functionality.
- All generated images and pages are saved in the `output/` directory.
- The UI is built with Streamlit for easy interaction.

---

## ✅ To-Do / Future Enhancements
- Add support for more panel layouts and custom user layouts.
- Integrate real image generation models (DALL-E, SDXL, etc.).
- Improve character consistency and memory.
- Add multi-language support.
- Enhance error handling and logging.
- Add automated tests and CI/CD.

---

## 👨‍💻 Authors

Team of 5 students – M.Tech in AI (IISc Bangalore)  
- Jyoti Pal, 
- Kshitiz Singh, 
- Meenal Dhuria, 
- Nirmit Srivastava, 
- Rishav Kumar Goswami

Course: **DA225o - Deep Learning**, Summer 2025  

---

## 📄 License

MIT License — feel free to fork and build!
