from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class SessionMemory(BaseModel):
    session_id: str
    recent_turns: List[Dict[str, str]] = Field(default_factory=list)
    assistant_state: str = "idle"
    mode: str = "explain"
    language_mode: str = "hinglish"
    source_id: Optional[str] = None
    quiz_index: int = 0
    hands_free: bool = False

class UserMemory(BaseModel):
    user_id: str
    preferred_language: str = "hinglish"
    preferred_class_level: Optional[str] = None
    recurring_topics: List[str] = Field(default_factory=list)
    source_preferences: List[str] = Field(default_factory=list)
    corrections: List[Dict[str, Any]] = Field(default_factory=list)
    failure_patterns: List[str] = Field(default_factory=list)
