import base64
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from models.evaluation_result import EvaluationResult # Import from your new model file

def image_to_base64(image_path: str) -> str:
    """Converts an image file to a Base64 encoded string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise IOError(f"Error reading or encoding image at {image_path}: {e}")

class MultimodalJudgeAgent:
    """An agent that uses a multimodal LLM to judge a generated image against a prompt."""

    def __init__(self, llm_provider: Any = None):
        """
        Initializes the judge agent.
        Args:
            llm_provider: A LangChain-compatible LLM instance. Defaults to ChatOpenAI with gpt-4o.
        """
        if llm_provider:
            self.llm = llm_provider
        else:
            # IMPORTANT: We must use a vision-capable model like gpt-4o
            self.llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1024)

        self.output_parser = JsonOutputParser(pydantic_object=EvaluationResult)
        self._load_rubrics()

    def _load_rubrics(self):
        """Loads task-specific rubrics. Can be refactored to load from configs/."""
        self.rubrics = {
            "image_generation": """
                You are evaluating a generated comic panel image against the detailed prompt used to create it.
                Your judgment MUST be based SOLELY on the visual evidence in the image.

                1.  **Prompt-Image Correspondence (50%):** How well does the image visually represent the core elements of the 'Scene' and 'featuring' parts of the prompt? Are the correct characters, objects, and actions depicted?
                2.  **Style & Mood Adherence (30%):** Does the visual aesthetic of the image (colors, lighting, line work, character design) match the requested 'Art Style' and 'Mood' from the prompt?
                3.  **Technical Execution & Negative Prompt (20%):** Is the image high quality and visually coherent? Crucially, is it free of the elements mentioned in the negative prompt (e.g., text, words, signatures, borders)?
            """
        }

    def _create_multimodal_prompt(self, rubric: str, input_prompt: str, image_base64: str) -> List[HumanMessage]:
        """Creates the multimodal prompt payload for the judge."""
        format_instructions = self.output_parser.get_format_instructions()
        system_message_content = [
            {
                "type": "text",
                "text": f"""You are an expert, impartial, and meticulous AI Quality Judge with a keen eye for visual detail.
                Your task is to evaluate the provided image based on how well it adheres to the original text prompt, using the detailed rubric.
                Your feedback must reference specific visual elements in the image.

                You MUST format your response as a JSON object.
                {format_instructions}
                """
            },
            {
                "type": "text",
                "text": f"""
                **Evaluation Rubric:**
                ---
                {rubric}
                ---
                **Original Text Prompt (what the AI was asked to generate):**
                ---
                {input_prompt}
                ---
                Now, please evaluate the following image based on this prompt and rubric.
                """
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            }
        ]
        return [HumanMessage(content=system_message_content)]


    def judge_task(self, task_type: str, input_prompt: str, generated_image_path: str) -> EvaluationResult:
        """
        Judges a generated image against its source prompt.
        """
        print(f"--- Judging Image Task: {generated_image_path} ---")

        rubric = self.rubrics[task_type]
        image_b64 = image_to_base64(generated_image_path)
        judge_prompt = self._create_multimodal_prompt(rubric, input_prompt, image_b64)
        chain = self.llm | self.output_parser

        response_dict = chain.invoke(judge_prompt)
        return EvaluationResult(**response_dict)