from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    skills: List[str]

class ChatResponse(BaseModel):
    message: str