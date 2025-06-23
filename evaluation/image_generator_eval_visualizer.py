import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def image_generator_eval_visualizer():
    # Load the CSV
    df = pd.read_csv("evaluation/image_generator_eval_results/image_panel_metrics.csv")

    # Average scores across panels for each test_case, image_engine, text_engine
    df_avg = df.groupby(
        ["test_case", "image_engine", "text_engine"], as_index=False
    ).agg({
        "blip/bert_f1": "mean",
        "clip_score": "mean"
    })

    # 1. Bar Plot: BERT F1 vs CLIP Score per Test Case (Grouped by Image Model)
    df_bar = df_avg.melt(
        id_vars=["test_case", "image_engine", "text_engine"],
        value_vars=["blip/bert_f1", "clip_score"],
        var_name="score_type",
        value_name="score"
    )
    print("Bar Plot DataFrame:",df_bar)
    plt.figure(figsize=(14, 6))
    sns.barplot(
        data=df_bar,
        x="test_case",
        y="score",
        hue="score_type",
        ci=None,
        palette="Set2"
    )
    plt.title("Mean BERT F1 and CLIP Score per Test Case (Averaged Across Panels)")
    plt.xlabel("Test Case Number")
    plt.ylabel("Mean Score")
    plt.ylim(0, 1)
    plt.legend(title="Score Type")
    plt.tight_layout()
    plt.savefig("evaluation/image_generator_eval_results/bert_clip_bar_per_test_case_mean.png")
    plt.show()

    # 2. Line Plot: Score Trends Across Test Cases for Each Image Model
    plt.figure(figsize=(14, 6))
    for model in df_avg["image_engine"].unique():
        sub = df_avg[df_avg["image_engine"] == model]
        plt.plot(sub["test_case"], sub["blip/bert_f1"], marker="o", label=f"{model} BERT F1")
        plt.plot(sub["test_case"], sub["clip_score"], marker="x", label=f"{model} CLIP")
    plt.title("Mean Score Trends Across Test Cases by Model (Averaged Across Panels)")
    plt.xlabel("Test Case Number")
    plt.ylabel("Mean Score")
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig("evaluation/image_generator_eval_results/bert_clip_line_trends_mean.png")
    plt.show()

    # 3. Box Plot: Score Distribution by Model
    df_box = df_avg.melt(
        id_vars=["image_engine"],
        value_vars=["blip/bert_f1", "clip_score"],
        var_name="score_type",
        value_name="score"
    )

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df_box, x="image_engine", y="score", hue="score_type")
    plt.title("Mean Score Distribution by Model (Averaged Across Panels)")
    plt.xlabel("Image Model")
    plt.ylabel("Mean Score")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig("evaluation/image_generator_eval_results/bert_clip_box_by_model_mean.png")
    plt.show()

    # 4. Scatter Plot: BERT F1 vs CLIP Score (Mean per Test Case)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df_avg, x="blip/bert_f1", y="clip_score", hue="image_engine")
    plt.title("Mean BERT F1 vs Mean CLIP Score per Test Case (Averaged Across Panels)")
    plt.xlabel("Mean BERT F1")
    plt.ylabel("Mean CLIP Score")
    plt.tight_layout()
    plt.savefig("evaluation/image_generator_eval_results/bert_vs_clip_scatter_mean.png")
    plt.show()

if __name__ == "__main__":
    image_generator_eval_visualizer()