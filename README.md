# 🖼️ DeepDoodle: AI-Powered Comic Generator

DeepDoodle is an Agentic AI framework that transforms natural language stories into illustrated, style-consistent comic panels. 

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
│   ├── story_analyst.py         # Analyzes story, extracts genre/style/mood
│   ├── scene_decomposer.py      # Splits story into visual scenes/panels
│   ├── prompt_engineer.py       # Crafts prompts for image generation
│   ├── image_generator.py       # Generates (or mocks) panel images
│   ├── character_memory.py      # (Optional) Maintains character consistency
│   └── page_composer.py         # Stitches panels into comic pages
│
├── graph/                       # Workflow orchestration (LangGraph)
│   ├── __init__.py
│   ├── workflow.py              # Defines the LangGraph workflow
│   └── state.py                 # Defines the ComicGenerationState (shared state dict)
│
├── utils/                       # Utility functions and configuration
│   ├── __init__.py
│   ├── config.py                # Constants (panel size, output dir, etc.)
│   └── layout.py                # Comic page layout functions (grid, strip, etc.)
│
├── output/                      # Generated images (created at runtime)
│   ├── panels/                  # Individual panel images
│   └── pages/                   # Final composed comic pages
│
├── ui/                          # Streamlit web interface
│   ├── __init__.py
│   └── streamlit_app.py         # Streamlit app for interactive comic generation
│
├── data/                        # Sample data and stories
│   └── samples/
│       └── example_story.txt
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

### 4. Add environment variables
Create a `.env` file in the root directory with this content:
```env
OPENAI_API_KEY=your_openai_key
HUGGINGFACEHUB_API_TOKEN=your_hf_token
```

### 5. (Optional) Place sample images
Put some sample images `sample-panel-<i>.png` in the `/output/panels` folder if you want to test the UI with static images.

### 6. Run the Streamlit app
```bash
streamlit run ui/streamlit_app.py
```

---

## 🧠 Features

- **Story Analyst**: Analyzes the story, extracts genre, style, and mood.
- **Scene Decomposer**: Splits the story into visual scenes/panels.
- **Prompt Engineer**: Converts scenes and metadata into image prompts.
- **Image Generator**: Generates images for each panel based on prompts (mocked or real).
- **Page Composer**: Stitches image panels into final comic pages.
- **(Optional) Character Memory**: Maintains character consistency across panels.
- **LangGraph-based orchestration**: Orchestrates agent communication and workflow.

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
- Member 1
- Member 2
- Member 3
- Member 4
- Member 5

Course: **DA225o - Deep Learning**, Summer 2025  

---

## 📄 License

MIT License — feel free to fork and build!
