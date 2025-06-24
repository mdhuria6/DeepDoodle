# DeepDoodle/evaluation/llm-as-judge/eval_story_analyst.py

import os
import sys
import json
import datetime

# Go up two directories to the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.llm_judge import LLMJudgeAgent

RUN_LOG_DIR = os.path.join(os.path.dirname(__file__), 'run-log')
LOG_FILE = os.path.join(RUN_LOG_DIR, 'eval_story_analyst_run.log')
os.makedirs(RUN_LOG_DIR, exist_ok=True)

def log_run(message: str):
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def run_happy_path_test(judge: LLMJudgeAgent):
    """
    Test Case 1: The "Happy Path".
    The agent receives a clear story and the LLM is simulated to return a perfect JSON response.
    """
    log_run("--- Running Test Case 1: Happy Path ---")
    print("\n--- Running Test Case 1: Happy Path ---")
    task_type = "story_analyst"

    story_input = "In a kingdom powered by enchanted crystals, the knight Anya is hired by the shadowy Lord Valerius to steal the Queen's clockwork heart. Anya must navigate castle corridors and disable magical traps."

    # This simulates a perfect output from the agent's LLM call
    generated_output = json.dumps({
        "artistic_style": "Steampunk Fantasy",
        "mood": "Suspenseful, Adventurous",
        "character_descriptions": [
            {"name": "Anya", "description": "A skilled and agile knight, clad in practical armor integrated with glowing crystals. She is determined but wary."},
            {"name": "Lord Valerius", "description": "An enigmatic and manipulative noble who operates from the shadows, often cloaked and speaking in whispers."}
        ]
    }, indent=4)

    try:
        evaluation = judge.judge_task(
            task_type=task_type,
            input_prompt=story_input,
            generated_output=generated_output
        )
        log_run(f"Score: {evaluation.score}/10 | Feedback: {evaluation.feedback}")
        print(f"Score: {evaluation.score}/10")
        print(f"Feedback:\n{evaluation.feedback}")
    except Exception as e:
        log_run(f"An error occurred during LLM evaluation: {e}")
        print(f"An error occurred during LLM evaluation: {e}")

def run_character_fallback_test(judge: LLMJudgeAgent):
    """
    Test Case 2: Character Extraction Fallback.
    We simulate the LLM failing to find characters. The agent's fallback logic should then kick in.
    The 'generated_output' here represents the agent's *final* output after applying its heuristic.
    """
    log_run("--- Running Test Case 2: Character Fallback Logic ---")
    print("\n--- Running Test Case 2: Character Fallback Logic ---")
    task_type = "story_analyst"

    story_input = "The wizard Elara and the warrior Borin entered the Whispering Caves. Elara held her glowing staff high, while Borin drew his sword."

    # Simulate that the agent's LLM returned an empty character list,
    # so the agent's code applied its 'extract_fallback_character_descriptions' function.
    # This is the FINAL output from the agent that we are judging.
    generated_output = json.dumps({
        "artistic_style": "High Fantasy",
        "mood": "Mysterious, Tense",
        "character_descriptions": [
            {"name": "Elara", "description": "Elara is a key character in the story. Their appearance and personality are important to the plot."},
            {"name": "Borin", "description": "Borin is a key character in the story. Their appearance and personality are important to the plot."}
        ]
    }, indent=4)

    try:
        evaluation = judge.judge_task(
            task_type=task_type,
            input_prompt=story_input,
            generated_output=generated_output
        )
        log_run(f"Score: {evaluation.score}/10 | Feedback: {evaluation.feedback}")
        print(f"Score: {evaluation.score}/10")
        print(f"Feedback:\n{evaluation.feedback}")
        print("\nNOTE: A good score here confirms the fallback worked, but feedback might note the generic descriptions.")
    except Exception as e:
        log_run(f"An error occurred during LLM evaluation: {e}")
        print(f"An error occurred during LLM evaluation: {e}")

def run_user_override_test(judge: LLMJudgeAgent):
    """
    Test Case 3: User Preset Override.
    The LLM suggests one style, but the agent should have prioritized a user-provided style.
    We are judging the agent's final decision.
    """
    log_run("--- Running Test Case 3: User Preset Override Logic ---")
    print("\n--- Running Test Case 3: User Preset Override Logic ---")
    task_type = "story_analyst"

    story_input = "A lone starship captain drifts through a nebula. The ship's AI is their only companion."

    # Imagine the user chose 'Anime' as a style preset.
    # The agent's LLM might have suggested 'Photorealistic Sci-Fi', but the agent's logic
    # correctly chose the user's preset. This is the FINAL output we are judging.
    generated_output = json.dumps({
        "artistic_style": "Anime", # Correctly prioritized user preset
        "mood": "Lonely, Contemplative",
        "character_descriptions": [
            {"name": "Captain Eva", "description": "A young captain with determined eyes and short-cropped hair, often seen gazing out the cockpit window."},
            {"name": "The Ship's AI", "description": "Represented by a holographic blue light, its personality is calm and logical."}
        ]
    }, indent=4)

    try:
        evaluation = judge.judge_task(
            task_type=task_type,
            input_prompt=story_input,
            generated_output=generated_output
        )
        log_run(f"Score: {evaluation.score}/10 | Feedback: {evaluation.feedback}")
        print(f"Score: {evaluation.score}/10")
        print(f"Feedback:\n{evaluation.feedback}")
    except Exception as e:
        log_run(f"An error occurred during LLM evaluation: {e}")
        print(f"An error occurred during LLM evaluation: {e}")

if __name__ == '__main__':
    log_run("="*50)
    log_run("Running Judge Evaluation for: Story Analyst")
    log_run("="*50)
    # Make sure API keys are loaded if necessary for the judge agent
    try:
        judge_agent = LLMJudgeAgent()
        run_happy_path_test(judge_agent)
        run_character_fallback_test(judge_agent)
        run_user_override_test(judge_agent)
    except Exception as e:
        log_run(f"Could not initialize judge agent. Error: {e}")
        print(f"Could not initialize judge agent. Error: {e}")