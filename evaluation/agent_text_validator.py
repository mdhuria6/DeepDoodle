from utils.metrics import evaluate_meteor, evaluate_rouge, evaluate_bertscore
import pandas as pd
import os

def evaluate_case(args):
    idx, case, agent_func, output_key, input_keys = args
    agent_input = {key: case[key] for key in input_keys if key in case}
    output = agent_func(agent_input)
    generated = output[output_key]
    reference = case["expanded_story"]

    meteor = evaluate_meteor(generated, reference)
    rouge = evaluate_rouge(generated, reference)
    bert = evaluate_bertscore(generated, reference)

    return {
        "case_id": idx + 1,
        "meteor": meteor,
        **rouge,
        **bert
    }

def run_text_generation_evaluation_multiprocessing(
    agent_func,
    test_cases,
    output_key="story_text",
    input_keys=None,
    save_path="evaluation_results.csv",
    max_workers=4
):
    import multiprocessing
    with multiprocessing.Pool(processes=max_workers) as pool:
        args_list = [(idx, case, agent_func, output_key, input_keys) for idx, case in enumerate(test_cases)]
        results = pool.map(evaluate_case, args_list)

    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    return df