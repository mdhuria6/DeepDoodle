# DeepDoodle/evaluation/llm-as-judge/eval_scene_decomposer.py

import os
import sys
import json
import datetime

# Go up two directories to the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.llm_judge import LLMJudgeAgent

RUN_LOG_DIR = os.path.join(os.path.dirname(__file__), 'run-log')
LOG_FILE = os.path.join(RUN_LOG_DIR, 'eval_scene_decomposer_run.log')
os.makedirs(RUN_LOG_DIR, exist_ok=True)

def log_run(message: str):
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def run_elara_story_test(judge: LLMJudgeAgent):
    """
    Test Case: Evaluates the specific output for the "Elara the Astronomer" story.
    """
    log_run("--- Running Test Case: Elara Story Decomposition ---")
    task_type = "scene_decomposer"

    # This dictionary simulates the relevant parts of the ComicGenerationState fed to the agent,
    # using the exact data you provided.
    input_state_context = {
        "story_text": """In the silent hum of the deep space observatory, veteran astronomer Elara felt a familiar loneliness.
            For years, her screens showed nothing but cosmic static.
            Tonight was different. A single, pure sine wave, glowing an emerald green, cut through the noise.
            It was a signal. Before she could process it, alarms blared.
            A nearby red giant, catalogued for centuries, had gone supernova, decades ahead of schedule.
            The energy readings were impossible. As the shockwave data streamed in, she saw it: the supernova's energy was being shaped, focused.
            The sine wave wasn't from the star; it was riding the wave, a message in a bottle on a stellar tsunami.
            It was an invitation. Years later, her hair now streaked with grey, Elara steps out onto a world bathed in the light of twin suns.
            The air is sweet, the ground soft. A bustling, elegant city rises in the distance, a testament to her arrival.
            She looks at a device in her hand, which displays that same, beautiful green sine wave.
            She wasn't the discoverer of a message; she was its recipient.
            And she was finally home.
        """,
        "panel_count": 4, # The number of panels in your output
        "character_descriptions": [
            {
                "name": "Elara",
                "description": "A veteran astronomer with hair streaked with grey, indicating years of experience and wisdom. She has a contemplative demeanor, reflecting a life spent in solitude and deep thought. Her eyes are sharp and observant, accustomed to scanning the vastness of space. Elara has a medium build and stands at an average height. Her skin tone is fair, showing signs of aging with fine lines. She typically wears practical, comfortable clothing suitable for long hours in a deep space observatory, often seen in a lab coat or casual attire. Elara is introspective and resilient, with a deep-seated loneliness that is slowly replaced by a sense of belonging and purpose. She carries a device displaying a green sine wave, a distinctive prop symbolizing her connection to the mysterious message."
            }
        ]
    }

    # The exact JSON output your agent produced.
    generated_output = json.dumps([
        {
            "panel": 1,
            "description": "Wide shot of a deep space observatory filled with screens displaying cosmic static. Elara, with her contemplative demeanor, sits alone at a console, surrounded by the dim glow of monitors.",
            "captions": [
                {
                    "order": 1,
                    "speaker": "Narrator",
                    "text": "In the silent hum of the deep space observatory, Elara felt a familiar loneliness.",
                    "type": "narration",
                    "location": "left"
                }
            ]
        },
        {
            "panel": 2,
            "description": "Close-up on Elara's wide, shocked eyes, illuminated by the green glow of the monitor displaying a pure sine wave. Her expression shifts from loneliness to awe.",
            "captions": [
                {
                    "order": 1,
                    "speaker": "Elara",
                    "text": "What is this... a signal?",
                    "type": "dialogue",
                    "location": "right"
                },
                {
                    "order": 2,
                    "speaker": "Narrator",
                    "text": "Tonight was different. A sine wave cut through the noise.",
                    "type": "narration",
                    "location": "left"
                }
            ]
        },
        {
            "panel": 3,
            "description": "Medium shot of Elara at her console, alarms blaring around her. The screen shows data of a supernova with impossible energy readings. Her face is a mix of shock and realization.",
            "captions": [
                {
                    "order": 1,
                    "speaker": "Narrator",
                    "text": "A nearby red giant had gone supernova, decades ahead of schedule.",
                    "type": "narration",
                    "location": "left"
                },
                {
                    "order": 2,
                    "speaker": "Elara",
                    "text": "The energy... it's being shaped. This isn't just a star's death.",
                    "type": "dialogue",
                    "location": "right"
                }
            ]
        },
        {
            "panel": 4,
            "description": "Wide shot of Elara, now older with grey-streaked hair, stepping onto a vibrant alien world under twin suns. She holds a device displaying the green sine wave, looking towards a distant, bustling city.",
            "captions": [
                {
                    "order": 1,
                    "speaker": "Narrator",
                    "text": "Years later, Elara steps onto a world bathed in light, finally home.",
                    "type": "narration",
                    "location": "left"
                },
                {
                    "order": 2,
                    "speaker": "Elara",
                    "text": "I wasn't the discoverer of a message; I was its recipient.",
                    "type": "dialogue",
                    "location": "center"
                }
            ]
        }
    ], indent=2)

    try:
        evaluation = judge.judge_task(
            task_type=task_type,
            input_prompt=json.dumps(input_state_context, indent=2),
            generated_output=generated_output
        )
        log_run(f"Score: {evaluation.score}/10 | Feedback: {evaluation.feedback}")
        log_run(f"Positive Points: {getattr(evaluation, 'positive_points', '')}")
        log_run(f"Areas for Improvement: {getattr(evaluation, 'areas_for_improvement', '')}")
        print(f"Score: {evaluation.score}/10")
        print(f"Feedback:\n{evaluation.feedback}")
        print(f"\nPositive Points:\n{evaluation.positive_points}")
        print(f"\nAreas for Improvement:\n{evaluation.areas_for_improvement}")
    except Exception as e:
        log_run(f"An error occurred during LLM evaluation: {e}")
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    log_run("="*50)
    log_run("Running Judge Evaluation for: Scene Decomposer")
    log_run("="*50)

    # Make sure API keys are loaded if necessary for the judge agent
    try:
        judge_agent = LLMJudgeAgent()
        run_elara_story_test(judge_agent)
    except Exception as e:
        log_run(f"Could not initialize judge agent. Please check API keys. Error: {e}")
        print(f"\nCould not initialize judge agent. Please check API keys. Error: {e}")