from utils.metrics import evaluate_character_descriptions, evaluate_meteor, evaluate_rouge, evaluate_bertscore
import pandas as pd
import os
import logging
from typing import Callable, List, Dict


logger = logging.getLogger(__name__)

def evaluate_case(args):
    idx, case, agent_func, output_key, input_keys, task_type = args
    agent_input = {key: case[key] for key in input_keys if key in case}
    output = agent_func(agent_input)
    if task_type == "story_generator":
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
    elif task_type == "story_analyst":
        extracted = output["character_descriptions"]
        reference = case["character_description"]
        metrics = evaluate_character_descriptions(extracted, reference)
        return {
            "case_id": idx + 1,
            **metrics
        }
    else:
        raise ValueError(f"Unsupported task_type: {task_type}")

def run_agent_evaluation(
    agent_func: Callable,
    test_cases: List[Dict],
    output_key: str,
    input_keys: List[str],
    save_path: str,
    task_type: str = "story_generator",
    use_multiprocessing: bool = False,
    max_workers: int = 4
) -> pd.DataFrame:
    results = []
    args_list = [(idx, case, agent_func, output_key, input_keys, task_type) for idx, case in enumerate(test_cases)]

    if use_multiprocessing:
        import multiprocessing
        with multiprocessing.Pool(processes=max_workers) as pool:
            results = pool.map(evaluate_case, args_list)
    else:
        for args in args_list:
            results.append(evaluate_case(args))

    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    print(f"\n✅ Evaluation complete. Results saved to {save_path}")
    return df

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
        logger.debug(f"output: {generated} and reference: {reference}")


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

def run_text_generation_evaluation_multiprocessing(
    agent_func,
    test_cases,
    output_key="story_text",
    input_keys=None,
    save_path="evaluation_results.csv",
    max_workers=1
):
    import multiprocessing
    with multiprocessing.Pool(processes=max_workers) as pool:
        args_list = [(idx, case, agent_func, output_key, input_keys) for idx, case in enumerate(test_cases)]
        results = pool.map(evaluate_case, args_list)

    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    return df