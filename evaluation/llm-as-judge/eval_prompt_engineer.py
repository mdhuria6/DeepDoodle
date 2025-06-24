import os
import sys
import json
import datetime

# Go up two directories to the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.llm_judge import LLMJudgeAgent

# For these tests, we assume a simplified STYLE_CONFIGS exists in the agent's environment.
# We will test both a style that exists ('Modern Comic Style') and one that doesn't.

RUN_LOG_DIR = os.path.join(os.path.dirname(__file__), 'run-log')
LOG_FILE = os.path.join(RUN_LOG_DIR, 'eval_prompt_engineer_run.log')
os.makedirs(RUN_LOG_DIR, exist_ok=True)

def log_run(message: str):
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def run_happy_path_test(judge: LLMJudgeAgent):
    log_run("--- Running Test Case 1: Happy Path ---")
    """
    Test Case 1: The "Happy Path".
    Tests standard operation with a known style and characters identified via captions.
    """
    print("\n--- Running Test Case 1: Happy Path ---")
    task_type = "prompt_engineer"

    # This dictionary simulates the relevant parts of the ComicGenerationState
    input_state = {
        "artistic_style": "Modern Comic Style",
        "mood": "Action-packed",
        "character_descriptions": [
            {"name": "Bolt", "description": "A hero with electric powers, wearing a blue and yellow suit."},
            {"name": "Dr. Hex", "description": "A villain with a metallic mask and a green cloak."}
        ],
        "current_scene": {
            "description": "Bolt confronts Dr. Hex on a rooftop overlooking the city at night.",
            "captions": [{"speaker": "Bolt", "text": "Your time is up, Hex!"}]
        }
    }

    # This is the expected output from the agent given the state above and assuming
    # 'Modern Comic Style' has specific keywords in the agent's config.
    generated_prompt_output = "Comic panel featuring: Bolt. Characters: Bolt: A hero with electric powers, wearing a blue and yellow suit.. Scene: Bolt confronts Dr. Hex on a rooftop overlooking the city at night.. Captions: Bolt: Your time is up, Hex!. Art Style: bold lines, vibrant colors, dynamic shading, high contrast, cinematic, dramatic lighting, detailed background. Mood: Action-packed. --ar 3:2 --v 6.0"

    try:
        evaluation = judge.judge_task(
            task_type=task_type,
            input_prompt=json.dumps(input_state),
            generated_output=generated_prompt_output
        )
        log_run(f"Score: {evaluation.score}/10 | Feedback: {evaluation.feedback}")
        print(f"Score: {evaluation.score}/10")
        print(f"Feedback: {evaluation.feedback}")
    except Exception as e:
        log_run(f"An error occurred during LLM evaluation: {e}")
        print(f"An error occurred during LLM evaluation: {e}")

def run_style_fallback_test(judge: LLMJudgeAgent):
    """
    Test Case 2: Style Fallback Logic.
    Tests the agent's behavior when given a style that does NOT exist in its STYLE_CONFIGS.
    """
    print("\n--- Running Test Case 2: Style Fallback Logic ---")
    task_type = "prompt_engineer"

    input_state = {
        "artistic_style": "Unheard-of Fantasy Style", # This style is assumed to be missing
        "mood": "Mystical",
        "character_descriptions": [{"name": "Elara", "description": "An elf with silver hair."}],
        "current_scene": {
            "description": "Elara stands in an ancient, glowing forest.",
            "captions": []
        }
    }

    # Expected output should use the default keywords and the style name itself.
    generated_prompt_output = "Comic panel featuring: Elara. Characters: Elara: An elf with silver hair.. Scene: Elara stands in an ancient, glowing forest.. Captions: . Art Style: in the style of Unheard-of Fantasy Style, , cinematic, dramatic lighting, detailed background. Mood: Mystical. --ar 3:2 --v 6.0"

    try:
        evaluation = judge.judge_task(
            task_type=task_type,
            input_prompt=json.dumps(input_state, indent=2),
            generated_output=generated_prompt_output
        )
        print(f"Score: {evaluation.score}/10")
        print(f"Feedback:\n{evaluation.feedback}")
    except Exception as e:
        print(f"An error occurred: {e}")

def run_character_fallback_test(judge: LLMJudgeAgent):
    """
    Test Case 3: Character Identification Fallback.
    Tests the agent's behavior when no character is mentioned in captions or the description.
    It should fall back to including ALL main characters.
    """
    print("\n--- Running Test Case 3: Character Identification Fallback ---")
    task_type = "prompt_engineer"

    input_state = {
        "artistic_style": "Modern Comic Style",
        "mood": "Tense",
        "character_descriptions": [
            {"name": "Bolt", "description": "A hero with electric powers."},
            {"name": "Dr. Hex", "description": "A villain with a metallic mask."}
        ],
        "current_scene": {
            "description": "A view of the city skyline from an empty rooftop at night.", # No characters mentioned
            "captions": [{"speaker": "Narrator", "text": "The city was quiet... too quiet."}] # Narrator doesn't count
        }
    }

    # Expected output should feature BOTH characters because the specific presence check failed.
    generated_prompt_output = "Comic panel featuring: Bolt, Dr. Hex. Characters: Bolt: A hero with electric powers. | Dr. Hex: A villain with a metallic mask.. Scene: A view of the city skyline from an empty rooftop at night.. Captions: Narrator: The city was quiet... too quiet.. Art Style: bold lines, vibrant colors, dynamic shading, high contrast, cinematic, dramatic lighting, detailed background. Mood: Tense. --ar 3:2 --v 6.0"

    try:
        evaluation = judge.judge_task(
            task_type=task_type,
            input_prompt=json.dumps(input_state, indent=2),
            generated_output=generated_prompt_output
        )
        print(f"Score: {evaluation.score}/10")
        print(f"Feedback:\n{evaluation.feedback}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    log_run("="*50)
    log_run("Running Judge Evaluation for: Prompt Engineer")
    log_run("="*50)

    try:
        judge_agent = LLMJudgeAgent()
        run_happy_path_test(judge_agent)
        run_style_fallback_test(judge_agent)
        run_character_fallback_test(judge_agent)
    except Exception as e:
        log_run(f"Could not initialize judge agent. Error: {e}")
        print(f"Could not initialize judge agent. Error: {e}")