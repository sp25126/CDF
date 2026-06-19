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
    ModelsRequest, ModelsResponse,
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
    "groq": "llama-3.1-8b-instant",
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
                    "messages": [{"role": "user", "content": "hi"}],
                    "max_tokens": 5,
                },
            )
            if resp.status_code == 200:
                return True, None
            # 400 = model issue or bad request — but the KEY is valid (Groq would return 401 for bad keys)
            if resp.status_code == 400:
                # Try once more with a different model to confirm the key works
                resp2 = await client.post(
                    PROVIDER_CHAT_URLS["groq"],
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": "hi"}],
                        "max_tokens": 5,
                    },
                )
                if resp2.status_code == 200:
                    return True, None
                if resp2.status_code in (401, 403):
                    return False, _safe_error(f"{resp2.status_code}")
                # Any 2xx or model-related 4xx still means the key is accepted
                if resp2.status_code != 401 and resp2.status_code != 403:
                    return True, None
            if resp.status_code in (401, 403):
                return False, _safe_error(f"{resp.status_code} {resp.text[:100]}")
            if resp.status_code == 429:
                # Rate limited but key IS valid
                return True, None
            return False, _safe_error(f"{resp.status_code} {resp.text[:100]}")
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


# ─── Model list fetchers ──────────────────────────────────────────────────────

# Models to surface from Groq (filter from their /models list)
GROQ_PREFERRED_PREFIXES = (
    "llama", "gemma", "mixtral", "qwen", "deepseek", "mistral",
)

# Chat models known to be available on OpenAI — fallback if API call fails
OPENAI_FALLBACK_MODELS = [
    {"id": "gpt-4o", "label": "GPT-4o"},
    {"id": "gpt-4o-mini", "label": "GPT-4o Mini"},
    {"id": "gpt-4-turbo", "label": "GPT-4 Turbo"},
    {"id": "gpt-3.5-turbo", "label": "GPT-3.5 Turbo"},
]

ANTHROPIC_FALLBACK_MODELS = [
    {"id": "claude-opus-4-5", "label": "Claude Opus 4.5"},
    {"id": "claude-sonnet-4-5", "label": "Claude Sonnet 4.5"},
    {"id": "claude-haiku-4-5", "label": "Claude Haiku 4.5"},
    {"id": "claude-3-5-sonnet-20241022", "label": "Claude 3.5 Sonnet"},
    {"id": "claude-3-5-haiku-20241022", "label": "Claude 3.5 Haiku"},
]


async def _fetch_groq_models(api_key: str) -> list[dict]:
    """Fetch live model list from Groq /models endpoint."""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if resp.status_code != 200:
                return []
            data = resp.json().get("data", [])
            # Keep only chat-capable models with known prefixes, sort by id
            models = [
                {"id": m["id"], "label": _groq_label(m["id"])}
                for m in data
                if any(m["id"].lower().startswith(p) for p in GROQ_PREFERRED_PREFIXES)
            ]
            models.sort(key=lambda m: m["id"])
            return models
    except Exception as e:
        logger.warning(f"[Settings] Groq model fetch failed: {e}")
        return []


def _groq_label(model_id: str) -> str:
    """Human-readable label from Groq model ID."""
    # e.g. llama-3.3-70b-versatile → LLaMA 3.3 70B Versatile
    name = model_id.replace("-", " ").replace("_", " ")
    parts = name.split()
    pretty = []
    for p in parts:
        if p.lower() == "llama":
            pretty.append("LLaMA")
        elif p.lower() == "gemma":
            pretty.append("Gemma")
        elif p.lower() == "mixtral":
            pretty.append("Mixtral")
        elif p.lower() == "qwen":
            pretty.append("Qwen")
        elif p.lower() == "deepseek":
            pretty.append("DeepSeek")
        elif p.lower() in ("instant", "versatile", "preview", "speculative"):
            pretty.append(f"({p.capitalize()})")
        else:
            pretty.append(p.upper() if len(p) <= 3 else p.capitalize())
    return " ".join(pretty)


async def _fetch_openai_models(api_key: str) -> list[dict]:
    """Fetch live model list from OpenAI — filter to GPT chat models."""
    CHAT_PREFIXES = ("gpt-4", "gpt-3.5", "o1", "o3", "o4")
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if resp.status_code != 200:
                return OPENAI_FALLBACK_MODELS
            data = resp.json().get("data", [])
            models = [
                {"id": m["id"], "label": m["id"]}
                for m in data
                if any(m["id"].lower().startswith(p) for p in CHAT_PREFIXES)
                and "instruct" not in m["id"]   # exclude instruct variants
                and "realtime" not in m["id"]
                and "audio" not in m["id"]
                and "tts" not in m["id"]
                and "embedding" not in m["id"]
                and "whisper" not in m["id"]
            ]
            models.sort(key=lambda m: m["id"], reverse=True)
            return models if models else OPENAI_FALLBACK_MODELS
    except Exception as e:
        logger.warning(f"[Settings] OpenAI model fetch failed: {e}")
        return OPENAI_FALLBACK_MODELS


async def _fetch_anthropic_models(api_key: str) -> list[dict]:
    """Anthropic has a /models endpoint (beta). Return curated fallback on error."""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
            )
            if resp.status_code != 200:
                return ANTHROPIC_FALLBACK_MODELS
            data = resp.json().get("data", [])
            models = [
                {"id": m["id"], "label": m.get("display_name", m["id"])}
                for m in data
                if "claude" in m["id"].lower()
            ]
            return models if models else ANTHROPIC_FALLBACK_MODELS
    except Exception as e:
        logger.warning(f"[Settings] Anthropic model fetch failed: {e}")
        return ANTHROPIC_FALLBACK_MODELS


@router.post("/models", response_model=ModelsResponse)
async def get_models(req: ModelsRequest):
    """
    Fetch the live list of available models for a provider using the user's key.
    Falls back to a curated static list if the API call fails.
    Never logs the key.
    """
    provider = req.provider.lower()
    logger.info(f"[Settings] Fetching models for provider={provider} (key redacted)")

    if provider == "groq":
        models = await _fetch_groq_models(req.api_key)
    elif provider == "openai":
        models = await _fetch_openai_models(req.api_key)
    elif provider == "anthropic":
        models = await _fetch_anthropic_models(req.api_key)
    else:
        return ModelsResponse(status="error", models=[], error="Unsupported provider.")

    return ModelsResponse(status="success", models=models)
