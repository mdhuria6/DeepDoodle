import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

    # 📊 1. Bar plot for BERT F1
    plt.figure(figsize=(12, 6))
    sns.barplot(x="case_id", y="bert_f1", data=df, palette="viridis")
    plt.title("BERT F1 Score by Test Case")
    plt.xlabel("Test Case")
    plt.ylabel("BERT F1 Score")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "bert_f1_barplot.png"))
    plt.close()

    # 📈 2. Line plot for all metrics
    plt.figure(figsize=(12, 6))
    for metric in ["meteor", "rougeL_f1", "bert_f1"]:
        plt.plot(df["case_id"], df[metric], marker="o", label=metric)
    plt.title("Metric Scores by Test Case")
    plt.xlabel("Test Case")
    plt.ylabel("Score")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "metric_lineplot.png"))
    plt.close()

    # 📦 3. Boxplot for metric distribution
    plt.figure(figsize=(10, 6))
    melted_df = df.melt(id_vars=["case_id"], value_vars=["meteor", "rougeL_f1", "bert_f1"])
    sns.boxplot(x="variable", y="value", data=melted_df)
    plt.title("Distribution of Text Generation Metrics")
    plt.xlabel("Metric")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "metric_boxplot.png"))
    plt.close()

    print(f"✅ Plots saved to {output_dir}")
