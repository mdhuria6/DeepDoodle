from agents.story_generator import story_generator
from evaluation.visualize_metrics import plot_text_generation_metrics
from models.comic_generation_state import ComicGenerationState
from evaluation.test_cases import test_cases
from evaluation.agent_text_validator import run_text_generation_evaluation
import nltk
import os
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')
base_path = "output/story_generator"
csv_name = "story_generator_results.csv"
backslash = "/"
csv_path = base_path + backslash + csv_name
plot_output_dir = os.path.dirname(base_path + backslash + csv_path)

def call_story_generator(input_dict):
    state = ComicGenerationState(input_dict)
    return story_generator(state)

df = run_text_generation_evaluation(
    agent_func=call_story_generator,
    test_cases=test_cases,
    output_key="story_text",
    input_keys=["story_text", "style_preset", "genre_preset", "layout_style", "character_description"],
    save_path=csv_path
)

plot_text_generation_metrics(csv_path,output_dir=plot_output_dir)
