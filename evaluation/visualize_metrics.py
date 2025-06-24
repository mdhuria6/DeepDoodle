import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_average_scores(summary_df: pd.DataFrame, output_dir: str):
    melt_avg = summary_df.melt(id_vars=["model", "prompt"], 
                                value_vars=["meteor", "rougeL_f1", "bert_f1"],
                                var_name="metric", value_name="score")
    melt_avg["label"] = melt_avg["model"] + " | " + melt_avg["prompt"]

    plt.figure(figsize=(12, 12))
    sns.barplot(data=melt_avg, x="label", y="score", hue="metric")
    plt.xticks(rotation=45, ha='right')
    plt.title("Average Metric Scores by Model | Prompt")
    plt.tight_layout()

    avg_plot_path = os.path.join(output_dir, "average_metrics_barplot.png")
    plt.savefig(avg_plot_path)
    plt.close()
    print(f"Saved: {avg_plot_path}")
    
def plot_text_generation_metrics_combined(df: pd.DataFrame, output_dir: str):
    """
    Plots comparison graphs for multiple models and prompts across metrics.
    """
    os.makedirs(output_dir, exist_ok=True)
    metric_cols = [col for col in ["meteor", "rougeL_f1", "bert_f1", "cosine_sim"] if col in df.columns]

    
    # Melt the DataFrame for easier plotting
    melt_df = df.melt(
        id_vars=["case_id", "model", "prompt"],
        value_vars=metric_cols,
        var_name="metric",
        value_name="score"
    )

    # Create a separate line plot for each metric
    for metric_name in melt_df["metric"].unique():
        plt.figure(figsize=(10, 6))
        metric_df = melt_df[melt_df["metric"] == metric_name]

        # Construct label as model+prompt for clarity
        metric_df["label"] = metric_df["model"] + " | " + metric_df["prompt"]

        sns.lineplot(
            data=metric_df,
            x="case_id",
            y="score",
            hue="label",
            marker="o"
        )

        plt.title(f"{metric_name.upper()} Score Across Test Cases")
        plt.xlabel("Test Case")
        plt.ylabel("Score")
        plt.ylim(0, 1)
        plt.xticks(metric_df["case_id"].unique())
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        plot_path = os.path.join(output_dir, f"combined_{metric_name}.png")
        plt.savefig(plot_path)
        plt.close()

        print(f"Saved: {plot_path}")

def plot_text_generation_metrics(csv_path: str, output_dir: str):
    """
    Load metrics from CSV and save plots to the specified output directory.
    
    Args:
        csv_path (str): Path to the evaluation CSV file.
        output_dir (str): Directory to save plots.
    """
    df = pd.read_csv(csv_path)

    # Ensure output_dir exists
    os.makedirs(output_dir, exist_ok=True)

    sns.set(style="whitegrid")

    # 1. Bar plot for BERT F1
    plt.figure(figsize=(8, 16))
    sns.barplot(x="case_id", y="bert_f1", data=df, palette="viridis")
    plt.title("BERT F1 Score by Test Case")
    plt.xlabel("Test Case")
    plt.ylabel("BERT F1 Score")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "bert_f1_barplot.png"))
    plt.close()

    # 2. Line plot for all metrics
    plt.figure(figsize=(12, 8))
    for metric in ["meteor", "rougeL_f1", "bert_f1"]:
        plt.plot(df["case_id"], df[metric], marker="o", label=metric)
    plt.title("Metric Scores by Test Case")
    plt.xlabel("Test Case")
    plt.ylabel("Score")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "metric_lineplot.png"))
    plt.close()

    # 3. Boxplot for metric distribution
    plt.figure(figsize=(12, 8))
    melted_df = df.melt(id_vars=["case_id"], value_vars=["meteor", "rougeL_f1", "bert_f1"])
    sns.boxplot(x="variable", y="value", data=melted_df)
    plt.title("Distribution of Text Generation Metrics")
    plt.xlabel("Metric")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "metric_boxplot.png"))
    plt.close()

    print(f"Plots saved to {output_dir}")
