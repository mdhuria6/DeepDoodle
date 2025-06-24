from pydantic import BaseModel, Field

class EvaluationResult(BaseModel):
    """
    A structured data model for the output of a judge agent.
    """
    score: int = Field(description="The final score from 1 to 10.")
    feedback: str = Field(description="Detailed, constructive feedback explaining the score based on the rubric.")
    positive_points: str = Field(description="A summary of what was done well.")
    areas_for_improvement: str = Field(description="Specific, actionable areas that could be improved.")
