from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    skills: List[str]


class ChatResponse(BaseModel):
    message: str


class JobSearchRequest(BaseModel):
    """
    Defines the request model for a direct job search.
    """
    skills: List[str] = Field(..., description="A list of skills to search for.")
    experience: Optional[str] = Field(None, description="The desired years of experience (e.g., '3 years exp'). Currently not used in filtering.")
    page: int = Field(1, description="The page number for pagination.", gt=0)
    size: int = Field(10, description="The number of results per page.", gt=0)
    posted_hours: int = Field(12, description="The time window in hours to filter job postings by.", gt=0)