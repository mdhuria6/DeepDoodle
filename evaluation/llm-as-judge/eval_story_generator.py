# DeepDoodle/evaluation/llm-as-judge/eval_story_generator.py

import os
import sys
import datetime

# Go up two directories to the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.llm_judge import LLMJudgeAgent

RUN_LOG_DIR = os.path.join(os.path.dirname(__file__), 'run-log')
LOG_FILE = os.path.join(RUN_LOG_DIR, 'eval_story_generator_run.log')
os.makedirs(RUN_LOG_DIR, exist_ok=True)

def log_run(message: str):
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def run_creative_expansion_test(judge: LLMJudgeAgent):
    """
    Test Case 1: Standard Creative Expansion.
    Checks if the agent can creatively expand a simple idea into a cohesive short story.
    """
    log_run("--- Running Test Case 1: Creative Expansion ---")
    task_type = "story_generator"

    # The initial inputs fed into the agent
    initial_prompt = "A clockmaker in a Victorian city discovers a gear that runs backwards."
    mood_input = "Steampunk Mystery"
    style_input = "Intricate and mechanical, with brass and copper tones"
    
    # This simulates a high-quality, sanitized output from the story_generator agent
    generated_story_output = """
    In the fog-shrouded heart of London, Alistair Finch, a man whose life was measured in the steady tick-tock of his creations, found an anomaly. It was a small brass gear, no larger than a shilling, but its teeth moved with an impossible, counter-clockwise spin. He placed it within his latest automaton, a silver songbird, expecting a malfunction. Instead, the bird sang a melody from the future, a tune yet to be composed. The gear did not just run backwards; it rewound time itself for whatever machine it inhabited. Realizing the terrible power he held, Alistair saw a shadowy figure watching his shop from across the cobbled street, a man whose own pocket watch seemed eerily familiar. The mystery of the gear had just begun, and it was clear he was no longer the only one who knew of its existence.
    """

    # For the judge, we combine the inputs to reflect the agent's full context
    full_input_context = f"Original Prompt: {initial_prompt}\nRequested Mood: {mood_input}\nRequested Style: {style_input}"

    try:
        evaluation = judge.judge_task(
            task_type=task_type,
            input_prompt=full_input_context,
            generated_output=generated_story_output
        )
        log_run(f"Score: {evaluation.score}/10 | Feedback: {evaluation.feedback}")
        print(f"Score: {evaluation.score}/10")
        print(f"Feedback:\n{evaluation.feedback}")
    except Exception as e:
        log_run(f"An error occurred during LLM evaluation: {e}")
        print(f"An error occurred during LLM evaluation: {e}")

def run_thematic_adherence_test(judge: LLMJudgeAgent):
    """
    Test Case 2: Strong Thematic Adherence.
    This test uses a very specific theme to check if the generated story's language and content align with it.
    """
    print("\n--- Running Test Case 2: Strong Thematic Adherence ---")
    task_type = "story_generator"

    initial_prompt = "A lone astronaut finds a strange, alien plant on a desolate moon."
    mood_input = "Cosmic Horror"
    style_input = "Organic, Giger-esque, bio-mechanical"

    # This simulates a high-quality output that strongly adheres to the 'Cosmic Horror' theme
    generated_story_output = """
    The crimson dust of Kepler-186f was sterile, dead. Yet, there it was. A plant, pulsating with a faint, nauseating violet light. It was a lattice of bone-white chitin and translucent, vein-like tubes. As Astronaut Eva knelt, the plant unfurled, revealing a pattern that was not just a pattern, but a star-chart of an impossible galaxy, a map that hurt her mind to behold. The silence of the moon was broken by a whisper, not in her ears, but directly in her thoughts—a soft, wet, sibilant sound that promised infinite knowledge at the low cost of her sanity. She felt an overwhelming urge to touch it, to let its alien geometry rewrite her human mind. The true desolation wasn't the moon around her, but the vast, terrifying emptiness it had just shown her within herself.
    """

    full_input_context = f"Original Prompt: {initial_prompt}\nRequested Mood: {mood_input}\nRequested Style: {style_input}"

    try:
        evaluation = judge.judge_task(
            task_type=task_type,
            input_prompt=full_input_context,
            generated_output=generated_story_output
        )
        print(f"Score: {evaluation.score}/10")
        print(f"Feedback:\n{evaluation.feedback}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    log_run("="*50)
    log_run("Running Judge Evaluation for: Story Generator")
    log_run("="*50)

    # Make sure API keys are loaded if necessary for the judge agent
    try:
        judge_agent = LLMJudgeAgent()
        run_creative_expansion_test(judge_agent)
    except Exception as e:
        log_run(f"Could not initialize judge agent. Error: {e}")
        print(f"Could not initialize judge agent. Error: {e}")