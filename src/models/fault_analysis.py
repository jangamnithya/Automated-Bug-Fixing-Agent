from pydantic import BaseModel, Field
from typing import List


class FaultAnalysis(BaseModel):
    """Structured explanation of a suspected bug."""

    file_path: str
    line_number: int
    exception_type: str

    issue: str

    evidence: List[str] = Field(default_factory=list)

    confidence: str = "LOW"