from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models.evaluation_result import EvaluationResult  # Import from your new model file

class LLMJudgeAgent:
    """An agent that uses a powerful LLM to judge the output of text-based generative tasks."""

    def __init__(self, llm_provider: Any = None):
        """
        Initializes the judge agent.
        Args:
            llm_provider: A LangChain-compatible LLM instance. Defaults to ChatOpenAI with gpt-4o.
        """
        if llm_provider:
            self.llm = llm_provider
        else:
            self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

        self.output_parser = JsonOutputParser(pydantic_object=EvaluationResult)
        self._load_rubrics()

    def _load_rubrics(self):
        """Loads task-specific rubrics. Can be refactored to load from configs/."""
        self.rubrics = {
            "story_generator": """
                1.  **Narrative Expansion & Creativity (40%):** How effectively does the generated text expand upon the original prompt? Does it add meaningful plot details, character depth, and descriptive world-building, or is it merely repetitive?
                2.  **Thematic Adherence (30%):** Does the expanded story strongly reflect the requested 'mood' (genre) and 'artistic_style'? For example, if the mood is 'Noir', does the text use classic noir language and themes?
                3.  **Coherence and Structure (20%):** Is the story logically consistent from beginning to end? Does it maintain a clear narrative structure without contradicting the original prompt?
                4.  **Output Quality & Sanitization (10%):** Is the final text clean, well-formatted prose, free of conversational artifacts (e.g., "Here is your story...") or incomplete sentences?
            """,
            "story_analyst": """
                1.  **JSON Format and Key Adherence (40%):** Did the output strictly adhere to a valid JSON format? Does it contain the required top-level keys: 'artistic_style', 'mood', and 'character_descriptions'? The 'character_descriptions' must be a list of objects, each with 'name' and 'description' keys.
                2.  **Thematic Analysis Quality (30%):** How accurately and relevantly did the analysis capture the story's essence? Is the 'artistic_style' appropriate for the genre? Is the 'mood' a fitting descriptor for the story's tone?
                3.  **Character Description Quality (30%):** Are the character descriptions insightful and useful for an illustrator? Do they capture the essence of the characters from the text? If the primary method failed, did a reasonable fallback get triggered?
            """,
            "scene_decomposer": """
                1.  **Structural & Count Adherence (50%):** This is the most critical criterion. Is the output a valid JSON list? Does the number of scenes in the list EXACTLY match the requested 'panel_count' from the input? Any mismatch is a major failure.
                2.  **Scene Content Quality (30%):** Is each element in the list a valid JSON object? Does each object contain a clear, visually descriptive 'description' key? If 'captions' are present, are they a list of objects with 'speaker' and 'text'? The content should be high quality.
                3.  **Narrative Cohesion & Completeness (20%):** Does the sequence of scenes logically and accurately represent the original story? Are any key plot points or events missing from the decomposition?
            """,
            "prompt_engineer": """
                1.  **Structural Integrity (40%):** Does the generated prompt strictly follow the required structure? It must contain distinct, well-formed sections for 'featuring' (characters), 'Scene', 'Captions', 'Art Style', and 'Mood'.
                2.  **Correct Information Collation (40%):** Is the information within each section accurate based on the input? Does the 'Scene' match the scene description? Are the correct characters identified and listed? Are all captions included?
                3.  **Style & Keyword Application (20%):** Does the 'Art Style' section correctly apply the keywords associated with the requested style preset? If a style preset was not found, does it correctly use the fallback styling logic?
            """
        }

    def get_judge_prompt_template(self) -> ChatPromptTemplate:
        """Creates the prompt template for the judge."""
        return ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert, impartial, and meticulous AI Quality Judge. Your task is to evaluate the output of a generative AI task based on a provided prompt and a detailed rubric.
                Analyze the output critically and provide a score from 1 to 10, along with detailed, constructive feedback.
                Use a chain-of-thought process: first, analyze the output against each criterion in the rubric, then synthesize these observations to determine your final score and feedback.

                You MUST format your response as a JSON object with the keys: 'score', 'feedback', 'positive_points', 'areas_for_improvement'.
                {format_instructions}
                """
            ),
            (
                "human",
                """Please evaluate the following AI task.

                **Task Type:**
                {task_type}

                **Evaluation Rubric:**
                {rubric}

                ---
                **Input Prompt (what the AI was asked to do):**
                {input_prompt}
                ---
                **Generated Output (what the AI produced):**
                {generated_output}
                ---

                **Your Internal Reasoning (step-by-step analysis based on rubric):**
                """
            )
        ])

    def judge_task(self, task_type: str, input_prompt: str, generated_output: str) -> EvaluationResult:
        """
        Judges a given text-based task.
        """
        if task_type not in self.rubrics:
            raise ValueError(f"Unknown task type: {task_type}. No rubric found.")

        rubric = self.rubrics[task_type]
        prompt_template = self.get_judge_prompt_template()
        chain = prompt_template | self.llm | self.output_parser

        print(f"--- Judging Text Task: {task_type} ---")
        response_dict = chain.invoke({
            "task_type": task_type,
            "rubric": rubric,
            "input_prompt": input_prompt,
            "generated_output": generated_output,
            "format_instructions": self.output_parser.get_format_instructions(),
        })
        return EvaluationResult(**response_dict)