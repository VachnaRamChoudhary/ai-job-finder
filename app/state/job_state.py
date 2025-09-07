from typing import Optional, List

from pydantic import BaseModel, Field


# Define the state schema
class JobState(BaseModel):
    file_bytes: Optional[bytes] = None
    raw_text: Optional[str] = None
    # The skills can be a string from the LLM or a list after parsing
    skills: Optional[List[str]] = None
    raw_jobs: Optional[dict] = None
    job_ids: Optional[List[str]] = None
    jobs: List[dict] = Field(default_factory=list)
    response: str = ""
    summary: Optional[str] = None
    thought_process: Optional[str] = None
    start: int = 0
    posted_hours: int = 24
    job_count: int = 10
