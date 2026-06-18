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


from app.schemas.visual import VisualRef
from app.schemas.video import VideoRef

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
    hands_free_mode: bool = Field(
        default=False,
        description="True if the hands-free loop is active"
    )
    voice_command_mode: bool = Field(
        default=False,
        description="True if currently expecting a short voice command"
    )
    assistant_state: str = Field(
        default="idle",
        description="Overall assistant state: idle, listening, explaining, quizzing, awaiting_followup"
    )
    avatar_state: str = Field(
        default="idle",
        description="Avatar visual state: idle, speaking, listening, thinking"
    )
    follow_up_prompt: Optional[str] = Field(
        default=None,
        description="Follow-up question asked to the user"
    )
    next_voice_commands: List[str] = Field(
        default_factory=list,
        description="Expected short voice commands to guide the user"
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
    visual_reason: Optional[str] = Field(
        default=None,
        description="Reasoning for attaching visual"
    )
    video_reason: Optional[str] = Field(
        default=None,
        description="Reasoning for attaching video"
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
    response_text: Optional[str] = Field(
        default=None,
        description="Response text (backwards compatibility)"
    )
    
    # Backwards compatibility: quiz card attributes
    questions: List[QuizQuestion] = Field(
        default_factory=list,
        description="Questions list (backwards compatibility, use quiz.questions)"
    )
    message: Optional[str] = Field(
        default=None,
        description="Clarification message (backwards compatibility)"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested actions (backwards compatibility)"
    )
    citations: List[SourceRef] = Field(
        default_factory=list,
        description="Citations list (backwards compatibility, use source_refs)"
    )
    source_mode: bool = Field(
        default=False,
        description="Source mode (backwards compatibility)"
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

