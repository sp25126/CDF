from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any, Dict
from datetime import datetime


# ─── Request Schemas ──────────────────────────────────────────────────────────

class CommandRequest(BaseModel):
    """Unified command request accepted by POST /api/command and /api/command/text."""
    text: str = Field(..., min_length=1, description="The teacher's command text")
    session_id: str = Field(..., description="Browser session UUID")
    source_mode: Optional[bool] = Field(False, description="True if answering from ingested sources only")
    mode_hint: Optional[str] = Field(None, description="Optional intent hint: quiz, explain, etc.")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional classroom context metadata")


class UrlSourceRequest(BaseModel):
    url: str

class TextSourceRequest(BaseModel):
    title: str
    text: str


# ─── Citation / Source ────────────────────────────────────────────────────────

class Citation(BaseModel):
    source_title: str
    snippet: str
    page_number: Optional[int] = None
    section_label: Optional[str] = None


# ─── Per-mode Response Shapes (for documentation clarity) ────────────────────

class ExplainResponse(BaseModel):
    mode: str = "explain"
    title: str
    grade_level: int
    bullets: List[str]
    example: str
    recap: str
    response_text: str
    language_mode: Optional[str] = None
    source_mode: Optional[bool] = None
    citations: Optional[List[Citation]] = None


class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer: str


class QuizResponse(BaseModel):
    mode: str = "quiz"
    title: str
    instructions: str
    questions: List[QuizQuestion]
    answer_key: Union[str, List[str]]
    response_text: str
    language_mode: Optional[str] = None
    source_mode: Optional[bool] = None
    citations: Optional[List[Citation]] = None


class ClarifyResponse(BaseModel):
    mode: str = "clarify"
    message: str
    suggestions: List[str]
    response_text: str
    language_mode: Optional[str] = None


# ─── Transcript ───────────────────────────────────────────────────────────────

class TranscriptEntry(BaseModel):
    """A single turn in the classroom conversation transcript."""
    id: str
    timestamp: str
    role: str = Field(..., description="'user' or 'assistant'")
    text: str
    mode: Optional[str] = None
    language_mode: Optional[str] = None


# ─── Session ─────────────────────────────────────────────────────────────────

class SessionState(BaseModel):
    """Live session state returned by GET /api/session/{session_id}."""
    session_id: str
    mode: str = "idle"
    language_mode: str = "hinglish"
    assistant_state: str = "idle"
    hands_free: bool = False
    source_mode: bool = False
    recent_turns_count: int = 0
    last_topic: Optional[str] = None
    last_updated: Optional[str] = None


class SessionUpdateRequest(BaseModel):
    """Body for POST /api/session/{session_id}."""
    language_mode: Optional[str] = None
    hands_free: Optional[bool] = None
    source_mode: Optional[bool] = None


# ─── Reset ───────────────────────────────────────────────────────────────────

class ResetResponse(BaseModel):
    session_id: str
    cleared: bool = True
    message: str = "Session cleared"


# ─── Source Metadata ─────────────────────────────────────────────────────────

class SourceMetadata(BaseModel):
    id: str
    title: str
    type: str
    page_count: Optional[int] = None
    origin_url: Optional[str] = None
    language: str
    created_at: str


# ─── Unified Envelope ────────────────────────────────────────────────────────

class GlobalResponse(BaseModel):
    """
    Single consistent response envelope for all /api/* endpoints.

    Success:  { status: "success", data: <payload> }
    Error:    { status: "error",   error: { code, message } }
    Empty:    { status: "success", data: null }
    """
    status: str = Field("success", description="'success' or 'error'")
    data: Optional[Any] = Field(None, description="Response payload — null for empty states")
    error: Optional[Dict[str, str]] = Field(
        None,
        description="Error details — only present when status='error'. Never exposes stack traces."
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {"status": "success", "data": {"mode": "explain", "title": "Gravity"}},
                {"status": "success", "data": None},
                {"status": "error", "error": {"code": "INVALID_INPUT", "message": "Command cannot be empty"}}
            ]
        }
