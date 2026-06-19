"""
Command request schemas for the CDF classroom assistant.

Defines the input models that the frontend sends to the orchestrator.

Security note: user_api_key is accepted per-request and is NEVER logged,
stored in the database, or included in error reports.
"""

from pydantic import BaseModel, Field
from typing import Optional


class CommandRequest(BaseModel):
    """
    Main request model for the /api/command/text endpoint.
    
    The orchestrator uses this to detect intent, language mode,
    and route to the appropriate service (explain, quiz, etc.).
    """
    session_id: str = Field(
        ...,
        description="Session identifier to track conversation state"
    )
    text: str = Field(
        ...,
        description="User's spoken/typed command (the raw query)"
    )
    mode_hint: Optional[str] = Field(
        default=None,
        description="Optional hint for intent: 'explain', 'quiz', 'followup', etc."
    )
    source_mode: Optional[bool] = Field(
        default=False,
        description="Whether to use source-grounded answers (future layer)"
    )
    user_api_key: Optional[str] = Field(
        default=None,
        description="User-supplied API key. Used for this request only, never persisted."
    )
    user_provider: Optional[str] = Field(
        default=None,
        description="Provider to use with user_api_key: 'groq' | 'openai' | 'anthropic'"
    )
    user_model: Optional[str] = Field(
        default=None,
        description="Model override when user_api_key is provided."
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "session_id": "sess_12345",
                    "text": "What is photosynthesis?",
                    "mode_hint": None,
                    "source_mode": False
                },
                {
                    "session_id": "sess_12345",
                    "text": "Quiz me on photosynthesis",
                    "mode_hint": "quiz",
                    "source_mode": False
                },
                {
                    "session_id": "sess_12345",
                    "text": "Explain in English",
                    "mode_hint": "explain",
                    "source_mode": False
                }
            ]
        }

