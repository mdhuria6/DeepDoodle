import os
import sys
import json
from PIL import Image
import datetime

# Go up two directories to the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.multimodal_judge import MultimodalJudgeAgent

RUN_LOG_DIR = os.path.join(os.path.dirname(__file__), 'run-log')
LOG_FILE = os.path.join(RUN_LOG_DIR, 'eval_image_generator_run.log')

# Ensure the run-log directory exists
os.makedirs(RUN_LOG_DIR, exist_ok=True)

def log_run(message: str):
    """Append a message to the evaluation run log file with a timestamp."""
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def create_dummy_image(path: str, width: int, height: int, text: str):
    """Creates a placeholder image with specific dimensions and text for testing."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        from PIL import ImageDraw
        img = Image.new('RGB', (width, height), color='darkgray')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f"Dummy Image\n{width}x{height}\n{text}", fill='white')
        img.save(path)
        return True
    except ImportError:
        print("Pillow is not fully installed. Cannot create dummy image.")
        return False
    except Exception as e:
        print(f"Could not create dummy image: {e}")
        return False

def run_happy_path_test(judge: MultimodalJudgeAgent):
    """
    Test Case 1: The "Happy Path".
    The generated image matches the required dimensions and reasonably reflects the prompt.
    """
    print("\n--- Running Test Case 1: Happy Path ---")
    log_run("--- Running Test Case 1: Happy Path ---")
    task_type = "image_generation"
    image_path = "data/samples/panel_256x320.png"

    # This dictionary simulates the relevant parts of the ComicGenerationState
    input_state = {
        "panel_layout_details": [{
            "panel_index": 1,
            "target_generation_width": 256,
            "target_generation_height": 320
        }],
        "panel_prompts": [
            "Comic panel featuring: Elara. Characters: Elara: A veteran astronomer with hair streaked with grey, indicating years of experience and wisdom. She has a contemplative demeanor, reflecting a life spent in solitude and deep thought. Her eyes are sharp and observant, accustomed to scanning the vastness of space. Elara has a medium build and stands at an average height. Her skin tone is fair, showing signs of aging with fine lines. She typically wears practical, comfortable clothing suitable for long hours in a deep space observatory, often seen in a lab coat or casual attire. Elara is introspective and resilient, with a deep-seated loneliness that is slowly replaced by a sense of belonging and purpose. She carries a device displaying a green sine wave, a distinctive prop symbolizing her connection to the mysterious message.. Scene: Wide shot of a deep space observatory filled with screens displaying cosmic static. Elara, with her contemplative demeanor, sits alone at a console, surrounded by the dim glow of monitors.. Captions: Narrator: In the silent hum of the deep space observatory, Elara felt a familiar loneliness.. Art Style: in the style of Default Comic Style, , cinematic lighting, high detail. Mood: neutral."
        ]
    }
    target_w = input_state["panel_layout_details"][0]["target_generation_width"]
    target_h = input_state["panel_layout_details"][0]["target_generation_height"]
    prompt = input_state["panel_prompts"][0]

    # 1. Create a dummy image that meets the criteria only if the image does not exist
    if not os.path.exists(image_path):
        if not create_dummy_image(image_path, target_w, target_h, "Knight & Castle"):
            log_run("Skipping test due to image creation failure.")
            print("Skipping test due to image creation failure.")
            return
    # 2. Programmatic Check: Verify dimensions
    print(f"   > Programmatically checking dimensions for {image_path}...")
    with Image.open(image_path) as img:
        if img.width == target_w and img.height == target_h:
            log_run(f"PASS: Image dimensions ({img.width}x{img.height}) are correct.")
            print(f"   ✅ PASS: Image dimensions ({img.width}x{img.height}) are correct.")
        else:
            log_run(f"FAIL: Image dimensions ({img.width}x{img.height}) are INCORRECT. Expected ({target_w}x{target_h}).")
            print(f"   ❌ FAIL: Image dimensions ({img.width}x{img.height}) are INCORRECT. Expected ({target_w}x{target_h}).")
            return # Stop test if dimensions are wrong

    # 3. LLM Judge Check: Evaluate visual content
    try:
        evaluation = judge.judge_task(
            task_type=task_type,
            input_prompt=prompt,
            generated_image_path=image_path
        )
        log_run(f"LLM Judge Evaluation: Score: {evaluation.score}/10 | Feedback: {evaluation.feedback}")
        print(f"   > LLM Judge Evaluation:")
        print(f"     Score: {evaluation.score}/10")
        print(f"     Feedback: {evaluation.feedback}")
    except Exception as e:
        log_run(f"An error occurred during LLM evaluation: {e}")
        print(f"   > An error occurred during LLM evaluation: {e}")

def run_dimension_mismatch_test():
    """
    Test Case 2: Dimension Mismatch Failure.
    The agent is simulated to have produced an image with incorrect dimensions.
    This test should fail at the programmatic check, without needing the LLM judge.
    """
    print("\n--- Running Test Case 2: Dimension Mismatch Failure ---")
    log_run("--- Running Test Case 2: Dimension Mismatch Failure ---")
    image_path = "data/samples/panel_512x512.png"

    input_state = {
        "panel_layout_details": [{
            "panel_index": 1,
            "target_generation_width": 256,
            "target_generation_height": 512
        }]
    }
    target_w = input_state["panel_layout_details"][0]["target_generation_width"]
    target_h = input_state["panel_layout_details"][0]["target_generation_height"]

    # Create a dummy image with the WRONG dimensions only if the image does not exist
    if not os.path.exists(image_path):
        if not create_dummy_image(image_path, 512, 512, "Wrong Size"):
            log_run("Skipping test due to image creation failure.")
            print("Skipping test due to image creation failure.")
            return

    # Programmatic Check: This should fail
    print(f"   > Programmatically checking dimensions for {image_path}...")
    with Image.open(image_path) as img:
        if img.width == target_w and img.height == target_h:
            log_run("TEST FAILED: Image dimensions were unexpectedly correct.")
            print(f"   ❌ TEST FAILED: Image dimensions were unexpectedly correct.")
        else:
            log_run(f"TEST PASSED: Correctly identified dimension mismatch. Actual: ({img.width}x{img.height}), Expected: ({target_w}x{target_h})")
            print(f"   ✅ TEST PASSED: Correctly identified dimension mismatch.")
            print(f"      -FAIL: Image dimensions are ({img.width}x{img.height}).")
            print(f"      -EXPECTED: ({target_w}x{target_h}).")

if __name__ == '__main__':
    log_run("="*50)
    log_run("Running Judge Evaluation for: Image Generator")
    log_run("="*50)

    # Make sure API keys are loaded if necessary for the judge agent
    try:
        judge_agent = MultimodalJudgeAgent()
        run_happy_path_test(judge_agent)
        run_dimension_mismatch_test()
    except Exception as e:
        log_run(f"Could not initialize judge agent. Please check API keys. Error: {e}")
        print(f"\nCould not initialize judge agent. Please check API keys. Error: {e}")