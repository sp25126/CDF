"""
Settings schemas — user-supplied API key validation and usage metadata.

These models travel only for the duration of a single request.
The raw key is never logged or persisted server-side.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ValidateKeyRequest(BaseModel):
    """Minimal ping to verify a user-supplied key works."""
    provider: str = Field(..., description="'groq' | 'openai' | 'anthropic'")
    api_key: str = Field(..., min_length=10, description="User-supplied API key")
    model: Optional[str] = Field(default=None, description="Model to test against")


class ValidateKeyResponse(BaseModel):
    valid: bool
    provider: str
    model_used: Optional[str] = None
    error: Optional[str] = None


class UsageRequest(BaseModel):
    provider: str = Field(..., description="'groq' | 'openai' | 'anthropic'")
    api_key: str = Field(..., min_length=10)


class UsageInfo(BaseModel):
    provider: str
    used: Optional[int] = None          # tokens used (if known)
    remaining: Optional[int] = None     # tokens/requests remaining
    limit: Optional[int] = None         # total quota limit
    reset_at: Optional[str] = None      # ISO timestamp of next reset
    last_checked: Optional[str] = None  # ISO timestamp when we checked
    available: bool = False             # True only if provider returned real data


class UsageResponse(BaseModel):
    status: str = "success"
    data: Optional[UsageInfo] = None
    error: Optional[str] = None


class ModelsRequest(BaseModel):
    provider: str = Field(..., description="'groq' | 'openai' | 'anthropic'")
    api_key: str = Field(..., min_length=10)


class ModelInfo(BaseModel):
    id: str
    label: str


class ModelsResponse(BaseModel):
    status: str = "success"
    models: list[ModelInfo] = []
    error: Optional[str] = None
