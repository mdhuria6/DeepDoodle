import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# File paths from uploaded files
files = {
    "cot_structured_prompt": "../output/story_analyst/results_cot_prompt_mistral_mixtral_8x7b_instruct.csv",
    "few_shot_prompt": "../output/story_analyst/results_few_shot_prompt_mistral_mixtral_8x7b_instruct.csv",
    "genre_stylized_prompt": "../output/story_analyst/esults_hybrid_prompt_mistral_mixtral_8x7b_instruct.csv",
    "role_based_prompt": "../output/story_analyst/results_role_based_prompt_mistral_mixtral_8x7b_instruct.csv",
    "structured_prompt": "../output/story_analyst/results_structured_prompt_mistral_mixtral_8x7b_instruct.csv",
    "zero_shot_prompt": "../output/story_analyst/results_zero_shot_prompt_mistral_mixtral_8x7b_instruct.csv",
}

# Read and concatenate all CSVs with prompt and model info
all_dfs = []
for prompt, path in files.items():
    df = pd.read_csv(path)
    df["prompt"] = prompt
    df["model"] = "mistral_mixtral_8x7b_instruct"
    all_dfs.append(df)

combined_df = pd.concat(all_dfs, ignore_index=True)

# Melt the combined dataframe
melted_df = combined_df.melt(
    id_vars=["case_id", "model", "prompt"],
    value_vars=["meteor", "rougeL_f1", "cosine_sim"],
    var_name="metric",
    value_name="score"
)

# Function to plot line graphs for individual metrics
def plot_metric_lines(melted_df, metric):
    plt.figure(figsize=(12, 6))
    metric_df = melted_df[melted_df["metric"] == metric].copy()
    metric_df["label"] = metric_df["model"] + " | " + metric_df["prompt"]
    sns.lineplot(data=metric_df, x="case_id", y="score", hue="label", marker="o")
    plt.title(f"{metric.upper()} Score Across Test Cases")
    plt.xlabel("Test Case")
    plt.ylabel("Score")
    plt.ylim(0, 1)
    plt.xticks(rotation=90)
    plt.tight_layout()
    path = f"../output/story_analyst/combined_{metric}.png"
    plt.savefig(path)
    plt.close()
    return path

# Plot individual metric graphs
meteor_path = plot_metric_lines(melted_df, "meteor")
rouge_path = plot_metric_lines(melted_df, "rougeL_f1")
cosine_path = plot_metric_lines(melted_df, "cosine_sim")

# Average plot
avg_df = (
    combined_df[["model", "prompt", "meteor", "rougeL_f1", "cosine_sim"]]
    .groupby(["model", "prompt"], as_index=False)
    .mean()
)

melt_avg = avg_df.melt(id_vars=["model", "prompt"], 
                       value_vars=["meteor", "rougeL_f1", "cosine_sim"],
                       var_name="metric", value_name="score")
melt_avg["label"] = melt_avg["model"] + " | " + melt_avg["prompt"]

plt.figure(figsize=(14, 6))
sns.barplot(data=melt_avg, x="label", y="score", hue="metric")
plt.xticks(rotation=45, ha='right')
plt.title("Average Metric Scores by Model | Prompt")
plt.tight_layout()
avg_plot_path = "../output/story_analyst/average_metrics_barplot_updated.png"
plt.savefig(avg_plot_path)
plt.close()

avg_plot_path, meteor_path, rouge_path, cosine_path