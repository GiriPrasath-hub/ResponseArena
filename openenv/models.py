from pydantic import BaseModel
from typing import Optional, Dict, Any

class Observation(BaseModel):
    task: str
    task_name: str
    difficulty: str
    query: str

class Action(BaseModel):
    type: str = "respond"
    content: Optional[str] = ""

class Reward(BaseModel):
    score: float
    breakdown: Optional[Dict[str, float]] = None
    feedback: Optional[Dict[str, Any]] = None