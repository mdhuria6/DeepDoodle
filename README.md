# deepDoodle: AI-Powered Text-to-Comic Generator

## Overview

This project transforms textual stories (1-200 words) into fully illustrated comic pages containing 3-5 colorful and detailed panels. The system intelligently handles very short inputs by generating expanded stories, breaks stories into comic scenes, generates images with consistent style, adds speech/thought bubble captions, and assembles the final comic page.

---

## Features

- **Input Validation:** Ensures input text length is within 1 to 200 words.
- **Story Generation:** Automatically expands very short inputs (less than 3 words) into a richer story for better visualization.
- **Scene & Prompt Generation:** Segments stories into coherent comic scenes and generates detailed image prompts.
- **Image Generation:** Uses AI models (e.g., Stable Diffusion) to create comic-style images based on prompts.
- **Image Validation:** Checks generated images for relevance and quality, enabling retries.
- **Caption Generation & Overlay:** Creates and overlays comic-style speech/thought bubbles on images.
- **Final Assembly:** Combines panels into a complete comic page for display or export.
- **Multilingual & Style Adaptation:** Designed for extensibility in languages and artistic styles.

---

## Architecture & Workflow

```plaintext
User (Web/Mobile UI)
        |
        v
[Frontend Interface]
        |
        v
[Backend API Gateway]
        |
        v
[LangChain Orchestrator / LangGraph Pipeline]
        |
        +--------------------------+
        |                          |
        |                  [Input Validation Agent]
        |                          |
        |                If text < 3 words → 
        |                  [Story Generator Agent]
        +--------------------------+
                   |
        [Scene & Prompt Generation Agent]
                   |
        [Image Generation Agent]
                   |
        [Image Validation Agent]
                   |
        [Caption Generation Agent]
                   |
        [Caption Overlay Module]
                   |
        [Final Comic Page Assembly]
                   |
        [Frontend Display]
