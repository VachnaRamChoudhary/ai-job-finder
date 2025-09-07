from typing import Optional, List

from pydantic import BaseModel, Field


# Define the state schema
class JobState(BaseModel):
    file_bytes: bytes
    raw_text: Optional[str] = None
    # The skills can be a string from the LLM or a list after parsing
    skills: Optional[List[str]] = None
    raw_jobs: Optional[dict] = None
    job_ids: Optional[List[str]] = None
    jobs: List[dict] = Field(default_factory=list)
    response: str = ""
    start: int = 0
    posted_hours: int = 12
    job_count: int = 10
