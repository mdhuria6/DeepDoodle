import os
import nltk
import pandas as pd
from agents.story_generator import story_generator
from models.comic_generation_state import ComicGenerationState
from evaluation.agent_text_validator import run_text_generation_evaluation
from evaluation.visualize_metrics import plot_average_scores, plot_text_generation_metrics_combined
from evaluation.test_cases import test_cases

# Download required NLTK resources
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Set base output directory
base_output_dir = "output/story_generator"
os.makedirs(base_output_dir, exist_ok=True)

# Define your prompt variants and model names
prompt_variants = [
    "zero_shot_prompt.txt",
    "few_shot_prompt.txt",
    "genre_stylized_prompt.txt",
    "cot_structured_prompt.txt"
]

model_variants = [
    "mistral_mixtral_8x7b_instruct"
    ]
def summarize_average_scores(df: pd.DataFrame):
    """
    Compute and print average metric scores grouped by model and prompt.
    """
    grouped = df.groupby(["model", "prompt"]).agg({
        "meteor": "mean",
        "rougeL_f1": "mean",
        "bert_f1": "mean"
    }).reset_index()

    # Round for display
    grouped = grouped.round(4)
    
    print("\n📊 Average Scores Per (Model, Prompt):")
    print(grouped.to_string(index=False))

    return grouped

def call_story_generator(input_dict):
    state = ComicGenerationState(input_dict)
    prompt_file = input_dict.get("prompt", "cot_structured_prompt.txt")
    return story_generator(state,prompt_file)

all_result_dfs = []

# Loop through all combinations of prompt and model
for prompt_file in prompt_variants:
    prompt_name = prompt_file.replace(".txt", "")
    for model_name in model_variants:
        print(f"\n🚀 Running evaluation with Prompt: {prompt_name}, Model: {model_name}")

        # Set unique CSV path
        result_csv = os.path.join(
            base_output_dir, f"results_{prompt_name}_{model_name}.csv"
        )

        # Define wrapper that injects prompt/model into input_dict
        def configured_story_generator(input_dict):
            input_dict = input_dict.copy()
            input_dict["prompt"] = prompt_file
            input_dict["text_engine"] = model_name
            return call_story_generator(input_dict)

        # Run evaluation
        df = run_text_generation_evaluation(
            agent_func=configured_story_generator,
            test_cases=test_cases,
            output_key="story_text",
            input_keys=["story_text", "style_preset", "genre_preset", "layout_style", "character_description", "prompt", "text_engine"],
            save_path=result_csv
        )

        df["prompt"] = prompt_name
        df["model"] = model_name
        all_result_dfs.append(df)

# Combine all results and plot
final_df = pd.concat(all_result_dfs, ignore_index=True)
plot_text_generation_metrics_combined(final_df, output_dir=base_output_dir)
summary_df = summarize_average_scores(final_df)
summary_df.to_csv(base_output_dir+"/summary_metrics.csv", index=False)
plot_average_scores(summary_df, output_dir=base_output_dir)
