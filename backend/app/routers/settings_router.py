"""
Settings router — validate user-supplied API keys and fetch quota information.

Security guarantees:
  - Keys are accepted only in request body (never query params / headers logged by default).
  - Keys are never stored in any database, log, or server-side variable.
  - Keys are stripped from all error traces before returning to the client.
  - A minimal 1-token ping is used for validation (cheapest possible call).
"""
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.settings import (
    ValidateKeyRequest, ValidateKeyResponse,
    UsageRequest, UsageInfo, UsageResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ─── Provider endpoints ───────────────────────────────────────────────────────

PROVIDER_CHAT_URLS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages",
}

PROVIDER_PING_MODELS = {
    "groq": "llama3-8b-8192",
    "openai": "gpt-3.5-turbo",
    "anthropic": "claude-3-5-haiku-20241022",
}


def _safe_error(msg: str) -> str:
    """Return a user-friendly error without exposing raw provider messages."""
    msg_lower = msg.lower()
    if "401" in msg or "unauthorized" in msg_lower or "invalid api key" in msg_lower:
        return "That key doesn't seem to be valid. Please check it and try again."
    if "403" in msg or "forbidden" in msg_lower:
        return "Access denied. Make sure the key has the right permissions."
    if "429" in msg or "rate limit" in msg_lower or "too many" in msg_lower:
        return "Too many requests. Your key is valid but currently rate-limited."
    if "402" in msg or "quota" in msg_lower or "insufficient" in msg_lower:
        return "Your quota appears to be exhausted. Please check your account."
    if "timeout" in msg_lower or "connect" in msg_lower:
        return "Could not reach the provider. Check your connection and try again."
    return "Something went wrong. Please check the key and try again."


async def _ping_groq(api_key: str, model: str) -> tuple[bool, Optional[str]]:
    """Minimal Groq ping. Returns (success, error_message)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                PROVIDER_CHAT_URLS["groq"],
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1,
                },
            )
            if resp.status_code == 200:
                return True, None
            return False, _safe_error(f"{resp.status_code} {resp.text}")
    except Exception as e:
        return False, _safe_error(str(e))


async def _ping_openai(api_key: str, model: str) -> tuple[bool, Optional[str]]:
    """Minimal OpenAI ping."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                PROVIDER_CHAT_URLS["openai"],
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1,
                },
            )
            if resp.status_code == 200:
                return True, None
            return False, _safe_error(f"{resp.status_code} {resp.text}")
    except Exception as e:
        return False, _safe_error(str(e))


async def _ping_anthropic(api_key: str, model: str) -> tuple[bool, Optional[str]]:
    """Minimal Anthropic ping."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                PROVIDER_CHAT_URLS["anthropic"],
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "ping"}],
                },
            )
            if resp.status_code == 200:
                return True, None
            return False, _safe_error(f"{resp.status_code} {resp.text}")
    except Exception as e:
        return False, _safe_error(str(e))


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/validate", response_model=ValidateKeyResponse)
async def validate_key(req: ValidateKeyRequest):
    """
    Test whether a user-supplied API key is accepted by the provider.
    Uses a minimal 1-token ping. Never logs the key.
    """
    provider = req.provider.lower()
    model = req.model or PROVIDER_PING_MODELS.get(provider, "")

    if provider not in PROVIDER_PING_MODELS:
        return ValidateKeyResponse(
            valid=False,
            provider=provider,
            error="Unsupported provider. Choose groq, openai, or anthropic.",
        )

    logger.info(f"[Settings] Validating key for provider={provider} (key redacted)")

    if provider == "groq":
        ok, err = await _ping_groq(req.api_key, model)
    elif provider == "openai":
        ok, err = await _ping_openai(req.api_key, model)
    elif provider == "anthropic":
        ok, err = await _ping_anthropic(req.api_key, model)
    else:
        ok, err = False, "Unknown provider."

    return ValidateKeyResponse(valid=ok, provider=provider, model_used=model if ok else None, error=err)


@router.post("/usage", response_model=UsageResponse)
async def get_usage(req: UsageRequest):
    """
    Attempt to fetch quota/rate-limit info for a user-supplied key.
    Returns null values gracefully if the provider does not expose quota data.
    """
    provider = req.provider.lower()
    now = datetime.now(timezone.utc).isoformat()

    logger.info(f"[Settings] Usage check for provider={provider} (key redacted)")

    # None of the three providers expose a simple free quota endpoint.
    # Groq, OpenAI, and Anthropic usage is available only via billing dashboards.
    # We return a structured unavailable response — no error, just no data.
    usage = UsageInfo(
        provider=provider,
        used=None,
        remaining=None,
        limit=None,
        reset_at=None,
        last_checked=now,
        available=False,
    )

    return UsageResponse(status="success", data=usage)
