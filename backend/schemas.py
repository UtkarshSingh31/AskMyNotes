from pydantic import BaseModel
from typing import List, Dict

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict]
