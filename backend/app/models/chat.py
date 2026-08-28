from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SourceCitation(BaseModel):
    manual_id: str
    experiment_number: Optional[int] = None
    experiment_title: Optional[str] = None
    section_name: Optional[str] = None
    excerpt: str
    score: float


class ChatRequest(BaseModel):
    manual_id: str
    experiment_id: Optional[str] = None
    query: str
    mode: Optional[str] = "standard"  # standard, simple_explanation, troubleshooting, equipment, safety


class ChatResponse(BaseModel):
    query: str
    answer: str
    mode: str
    grounded: bool
    manual_id: str
    experiment_id: Optional[str] = None
    citations: List[SourceCitation] = []
    timestamp: datetime = datetime.utcnow()
