"""
Response schemas for the CDF classroom assistant.

Defines the structured response models that the frontend can render deterministically.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SourceRef(BaseModel):
    """Reference to a source document or material."""
    title: str
    snippet: str
    page_number: Optional[int] = None
    section_label: Optional[str] = None
    source_id: Optional[str] = None
    url: Optional[str] = None


class VisualRef(BaseModel):
    """Reference to a visual asset."""
    type: str = Field(..., description="image, diagram, chart, etc.")
    url: str
    description: Optional[str] = None
    visual_id: Optional[str] = None


class VideoRef(BaseModel):
    """Reference to a video."""
    title: str
    youtube_id: str
    duration: Optional[int] = None
    video_id: Optional[str] = None
    url: Optional[str] = None

class QuizQuestion(BaseModel):
    """A single quiz question."""
    question: str
    options: List[str]
    correct_index: int
    explanation: str


class QuizPayload(BaseModel):
    """Quiz mode payload."""
    title: str
    topic: str
    questions: List[QuizQuestion]
    current_index: int = 0
    total_questions: int


class AssistantResponse(BaseModel):
    """
    Unified response object from the orchestrator.
    
    All fields are set consistently to ensure deterministic frontend rendering.
    The response adapts based on mode:
    - explain: returns answer_text with explanation
    - quiz: returns quiz payload
    - unclear: returns requires_clarification=True with fallback answer_text
    - stop/followup: returns appropriate next_actions
    """
    session_id: str = Field(..., description="Session identifier")
    mode: str = Field(
        ...,
        description="Mode: explain, quiz, followup, stop, or unclear"
    )
    language_mode: str = Field(
        default="hinglish",
        description="Language: hinglish, english, or hindi"
    )
    transcript_text: Optional[str] = Field(
        default=None,
        description="The original user command (for debugging/audit)"
    )
    answer_text: Optional[str] = Field(
        default=None,
        description="Main response text (explanation, fallback, etc.)"
    )
    quiz: Optional[QuizPayload] = Field(
        default=None,
        description="Quiz payload if mode is 'quiz'"
    )
    next_actions: List[str] = Field(
        default_factory=list,
        description="Suggested next steps for the frontend"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for intent/language detection (0.0-1.0)"
    )
    requires_clarification: bool = Field(
        default=False,
        description="True if the assistant needs clarification"
    )
    avatar_state: str = Field(
        default="idle",
        description="Avatar state: idle, speaking, listening, thinking"
    )
    source_refs: List[SourceRef] = Field(
        default_factory=list,
        description="References to source materials (future layer)"
    )
    visuals: List[VisualRef] = Field(
        default_factory=list,
        description="References to visual assets (future layer)"
    )
    videos: List[VideoRef] = Field(
        default_factory=list,
        description="References to videos (future layer)"
    )
    
    # Backwards compatibility: explain card attributes
    title: Optional[str] = Field(
        default=None,
        description="Card title (backwards compatibility)"
    )
    grade_level: Optional[int] = Field(
        default=None,
        description="Grade/class level (backwards compatibility)"
    )
    bullets: List[str] = Field(
        default_factory=list,
        description="Bullet points for smart board display (backwards compatibility)"
    )
    example: Optional[str] = Field(
        default=None,
        description="Example text (backwards compatibility)"
    )
    recap: Optional[str] = Field(
        default=None,
        description="Recap/summary text (backwards compatibility)"
    )
    
    # Backwards compatibility: quiz card attributes
    questions: List[QuizQuestion] = Field(
        default_factory=list,
        description="Questions list (backwards compatibility, use quiz.questions)"
    )
    audio_base64: Optional[str] = Field(
        default=None,
        description="Audio base64 (future layer)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_12345",
                "mode": "explain",
                "language_mode": "hinglish",
                "transcript_text": "What is photosynthesis?",
                "answer_text": "Photosynthesis ek process hai...",
                "quiz": None,
                "next_actions": ["Should I give an example?"],
                "confidence": 0.95,
                "requires_clarification": False,
                "avatar_state": "speaking",
                "source_refs": [],
                "visuals": [],
                "videos": [],
                "title": "Photosynthesis",
                "bullets": ["Plants make food using sunlight", "Water and CO2 are needed"],
                "example": "Green leaves use sunlight..."
            }
        }

