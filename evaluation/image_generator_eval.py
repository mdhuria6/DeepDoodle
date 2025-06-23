import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import shutil
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.test_cases import test_cases
from agents.story_generator import story_generator
from agents.story_analyst import story_analyst
from agents.scene_decomposer import scene_decomposer
from agents.layout_planner import layout_planner
from agents.prompt_engineer import prompt_engineer
from agents.image_generator import image_generator
from utils.blip_captioner import blip_caption_image
from utils.metrics import evaluate_bertscore
from agents.image_validator import image_validator
from models.comic_generation_state import ComicGenerationState

def test_image_generator_pipeline():
    # Set your models here
    image_models = ["flux.1-schnell"]  # Add more as needed
    text_models = ["openai_gpt4"]  # Add more as needed

    all_results = []

    for image_engine in image_models:
        for text_engine in text_models:
            for case_idx, case in enumerate(test_cases):
                print(f"\n=== Test Case {case_idx+1} | Image Model: {image_engine} | Text Model: {text_engine} ===")
                state = dict(case)
                state["image_engine"] = image_engine
                state["text_engine"] = text_engine
                state["layout_style"] = "Horizontal Strip"
                state["panel_count"] =  2
                state = ComicGenerationState(state)

                # Run pipeline
                sg_result = story_generator(state)
                state.update(sg_result)
                sa_result = story_analyst(state)
                state.update(sa_result)
                sd_result = scene_decomposer(state)
                state.update(sd_result)
                lp_result = layout_planner(state)
                state.update(lp_result)

                # Prompt engineering for each panel
                panel_count = state.get("panel_count", 1)
                panel_prompts = []
                for panel_idx in range(panel_count):
                    state["current_panel_index"] = panel_idx
                    pe_result = prompt_engineer(state)
                    if "panel_prompts" in pe_result and len(pe_result["panel_prompts"]) > panel_idx:
                        panel_prompts.append(pe_result["panel_prompts"][panel_idx])
                    elif "panel_prompts" in pe_result and pe_result["panel_prompts"]:
                        panel_prompts.append(pe_result["panel_prompts"][-1])
                    else:
                        panel_prompts.append("")
                state["panel_prompts"] = panel_prompts

                # Image generation for each panel
                state["panel_image_paths"] = []
                for panel_idx in range(panel_count):
                    state["current_panel_index"] = panel_idx
                    ig_result = image_generator(state)
                    if "panel_image_paths" in ig_result:
                        state["panel_image_paths"] = ig_result["panel_image_paths"]

                image_paths = state.get("panel_image_paths", [])
                scenes = state.get("scenes", [{} for _ in range(len(image_paths))])

                # Save images and state for this test case
                output_dir = f"evaluation/results/test_case_{case_idx+1}"
                os.makedirs(output_dir, exist_ok=True)

                for idx, image_path in enumerate(image_paths):
                    reference = scenes[idx].get("description", "No description available")
                    blip_caption = blip_caption_image(image_path)
                    bert_score = evaluate_bertscore(blip_caption, reference)
                    state["current_panel_index"] = idx
                    iv_result = image_validator(state)
                    validation_scores = iv_result.get("validation_scores", [])
                    iv_score = validation_scores[-1]["final_score"] if validation_scores else None

                    # Save/copy images
                    if os.path.exists(image_path):
                        dest_path = os.path.join(output_dir, f"panel_{idx+1}.png")
                        shutil.copy(image_path, dest_path)

                    all_results.append({
                        "test_case": case_idx + 1,
                        "panel_idx": idx + 1,
                        "image_engine": image_engine,
                        "text_engine": text_engine,
                        "bert_f1": bert_score["bert_f1"],
                        "bert_precision": bert_score["bert_precision"],
                        "bert_recall": bert_score["bert_recall"],
                        "clip_score": iv_score,
                        "reference": reference,
                        "blip_caption": blip_caption,
                    })

                # Save state as JSON
                state_json_path = os.path.join(output_dir, "final_state.json")
                with open(state_json_path, "w") as f:
                    json.dump(dict(state), f, indent=2, ensure_ascii=False)

    # Convert to DataFrame
    df = pd.DataFrame(all_results)
    df.to_csv("evaluation/image_panel_metrics.csv", index=False)
    print("Saved metrics to evaluation/image_panel_metrics.csv")

    # --- Visualization ---
    # sns.set(style="whitegrid")
    # plt.figure(figsize=(12, 6))
    # sns.barplot(data=df, x="panel_idx", y="bert_f1", hue="image_engine")
    # plt.title("BERT F1 Score per Panel by Image Model")
    # plt.xlabel("Panel Index")
    # plt.ylabel("BERT F1 Score")
    # plt.tight_layout()
    # plt.savefig("evaluation/bert_f1_per_panel.png")
    # plt.show()

    # plt.figure(figsize=(12, 6))
    # sns.barplot(data=df, x="panel_idx", y="clip_score", hue="image_engine")
    # plt.title("CLIP Score per Panel by Image Model")
    # plt.xlabel("Panel Index")
    # plt.ylabel("CLIP Score")
    # plt.tight_layout()
    # plt.savefig("evaluation/clip_score_per_panel.png")
    # plt.show()

if __name__ == "__main__":
    test_image_generator_pipeline()