import os
import nltk
import sys
import pandas as pd
import argparse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from agents.story_analyst import story_analyst
from models.comic_generation_state import ComicGenerationState
from evaluation.agent_text_validator import run_agent_evaluation, run_text_generation_evaluation, run_text_generation_evaluation_multiprocessing
from evaluation.visualize_metrics import plot_average_scores, plot_text_generation_metrics_combined
from evaluation.test_cases import test_cases

# Download required NLTK resources
nltk.download("punkt")
nltk.download("wordnet")
nltk.download("omw-1.4")

base_output_dir = "output/story_analyst"
os.makedirs(base_output_dir, exist_ok=True)
prompt_variants = [
    "zero_shot_prompt.txt",
    "hybrid_prompt.txt",
    "few_shot_prompt.txt",
    "cot_prompt.txt",
    "role_based_prompt.txt",
    "structured_prompt.txt",
]

model_variants = ["mistral_mixtral_8x7b_instruct"]

def call_story_analyst(input_dict):
    state = ComicGenerationState(input_dict)
    prompt_file = input_dict.get("prompt", "cot_structured_prompt.txt")
    return story_analyst(state, prompt_file)

def summarize_average_scores(df: pd.DataFrame):
    grouped = df.groupby(["model", "prompt"]).agg({
        "meteor": "mean",
        "rougeL_f1": "mean",
        "bert_f1": "mean"
    }).reset_index().round(4)

    print("\nAverage Scores Per (Model, Prompt):")
    print(grouped.to_string(index=False))
    return grouped

def main(use_multiprocessing=False):
    all_result_dfs = []

    for prompt_file in prompt_variants:
        prompt_name = prompt_file.replace(".txt", "")
        for model_name in model_variants:
            print(f"\nRunning evaluation with Prompt: {prompt_name}, Model: {model_name}")

            result_csv = os.path.join(base_output_dir, f"results_{prompt_name}_{model_name}.csv")

            def configured_story_analyst(input_dict):
                input_dict = input_dict.copy()
                input_dict["prompt"] = prompt_file
                input_dict["text_engine"] = model_name
                return call_story_analyst(input_dict)

            if use_multiprocessing:
                df = run_text_generation_evaluation_multiprocessing(
                    agent_func=configured_story_analyst,
                    test_cases=test_cases,
                    output_key="character_descriptions",
                    input_keys=["story_text", "style_preset", "genre_preset", "layout_style", "character_descriptions", "prompt", "text_engine"],
                    save_path=result_csv,
                    max_workers=4
                )
            else:
                df = run_agent_evaluation(
                    agent_func=configured_story_analyst,
                    test_cases=test_cases,
                    output_key="character_descriptions",
                    input_keys=["story_text", "style_preset", "genre_preset", "layout_style", "character_descriptions", "prompt", "text_engine"],
                    save_path=result_csv,
                    task_type="story_analyst"
                )

            df["prompt"] = prompt_name
            df["model"] = model_name
            all_result_dfs.append(df)

    final_df = pd.concat(all_result_dfs, ignore_index=True)
    plot_text_generation_metrics_combined(final_df, output_dir=base_output_dir)
    summary_df = summarize_average_scores(final_df)
    summary_df.to_csv(base_output_dir + "/summary_metrics.csv", index=False)
    plot_average_scores(summary_df, output_dir=base_output_dir)

if __name__ == "__main__":
    import multiprocessing

    # Use argparse to allow --multiprocessing flag
    parser = argparse.ArgumentParser()
    parser.add_argument("--multiprocessing", action="store_true", help="Use multiprocessing for evaluation")
    args = parser.parse_args()

    if args.multiprocessing:
        multiprocessing.set_start_method("spawn", force=True)

    main(use_multiprocessing=args.multiprocessing)