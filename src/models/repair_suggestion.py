from pydantic import BaseModel


class RepairSuggestion(BaseModel):
    file_path: str
    line_number: int
    problem: str
    suggested_fix: str
    confidence: float
    reasoning: list[str]