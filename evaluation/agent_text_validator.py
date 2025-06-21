import pandas as pd
from utils.metrics import evaluate_meteor, evaluate_rouge, evaluate_bertscore
import os
def run_text_generation_evaluation(
    agent_func,
    test_cases,
    output_key="story_text",
    input_keys=None,
    save_path="evaluation_results.csv"
):
    """
    Generic evaluation runner for any text generation agent.

    Parameters:
    - agent_func: callable(agent_input_dict) -> Dict[str, str]
    - test_cases: list of dicts with 'input', 'reference', and possibly other metadata
    - output_key: the key in the agent output that contains generated text
    - input_keys: list of keys to copy from test_case to agent input
    - save_path: filename to save results

    Returns:
    - DataFrame of evaluation results
    """
    results = []

    for idx, case in enumerate(test_cases):
        print(f"\n🔍 Evaluating Test Case {idx + 1}...")
        
        agent_input = {key: case[key] for key in input_keys if key in case} if input_keys else {"story_text": case["input"]}


        # Run the agent
        output = agent_func(agent_input)
        generated = output[output_key]
        reference = case["expanded_story"]

        # Evaluate
        meteor = evaluate_meteor(generated, reference)
        rouge = evaluate_rouge(generated, reference)
        bert = evaluate_bertscore(generated, reference)

        # Collect
        results.append({
            #"input": case.get(input_keys[0], "[MISSING]"),
            #"reference": reference,
            "case_id": idx + 1,
            #"generated": generated,
            "meteor": meteor,
            **rouge,
            **bert
        })

    # Save
    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    print(f"\n✅ Evaluation complete. Results saved to {save_path}")
    return df
