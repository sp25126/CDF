"""
LLM Router — single entry point for all LLM calls.

Routing policy (no user key):
  Groq    → primary (fast, cheap, strong)
  OpenRouter → fallback (broader model access)
  Ollama  → local emergency fallback

Routing policy (user key provided):
  Use the user's chosen provider directly with their key.
  If that fails, return a structured error — do NOT fall back to the server key.

Security: user_api_key is passed through but NEVER logged in full.
"""
import logging
from typing import Optional

from app.providers.groq_provider import GroqProvider
from app.providers.openrouter_provider import OpenRouterProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider

logger = logging.getLogger(__name__)

# Instantiate once at module load
_groq = GroqProvider()
_openrouter = OpenRouterProvider()
_ollama = OllamaProvider()
_openai = OpenAIProvider()
_anthropic = AnthropicProvider()

# Default server-key chain: ordered by preference
PROVIDER_CHAIN = [_groq, _openrouter, _ollama]

# Map provider name → provider instance (for user-key routing)
USER_PROVIDER_MAP = {
    "groq": _groq,
    "openai": _openai,
    "anthropic": _anthropic,
}


async def route_chat(
    messages: list,
    task_type: str = "default",
    response_format: Optional[dict] = None,
    user_api_key: Optional[str] = None,
    user_provider: Optional[str] = None,
    model_override: Optional[str] = None,
) -> dict:
    """
    Route an LLM call.

    If user_api_key + user_provider are supplied, route directly to that
    provider with the user's key. On failure, return a structured error
    (do NOT silently fall back to the server key — user expects their key).

    Otherwise try the default server chain: Groq → OpenRouter → Ollama.
    """
    # ── User-supplied key path ────────────────────────────────────────────────
    if user_api_key and user_provider:
        provider_name = user_provider.lower()
        provider = USER_PROVIDER_MAP.get(provider_name)
        if not provider:
            logger.warning(f"[LLMRouter] Unknown user provider: {provider_name}")
            return _build_graceful_error(task_type, "Unsupported provider.")

        logger.info(f"[LLMRouter] Using user key for provider={provider_name} task={task_type} (key redacted)")
        try:
            result = await provider.chat_completion(
                messages=messages,
                task_type=task_type,
                response_format=response_format,
                api_key=user_api_key,
                model_override=model_override,
            )
            logger.info(f"[LLMRouter] ✓ User-key success provider={provider_name}")
            return result
        except Exception as e:
            err_str = str(e)
            logger.warning(f"[LLMRouter] ✗ User-key provider={provider_name} failed: {type(e).__name__}")
            return _build_graceful_error(task_type, err_str)

    # ── Default server-key chain ──────────────────────────────────────────────
    last_error = None
    attempted = []

    for provider in PROVIDER_CHAIN:
        name = provider.provider_name
        try:
            logger.info(f"[LLMRouter] Attempting provider={name} task={task_type}")
            result = await provider.chat_completion(
                messages=messages,
                task_type=task_type,
                response_format=response_format,
            )
            logger.info(f"[LLMRouter] ✓ Success provider={name}")
            return result

        except Exception as e:
            err_str = str(e)
            logger.warning(
                f"[LLMRouter] ✗ Provider={name} failed. "
                f"Reason: {type(e).__name__}: {err_str[:120]}. "
                f"Trying next provider."
            )
            last_error = e
            attempted.append(f"{name}({type(e).__name__})")
            continue

    # All providers exhausted
    chain_log = " → ".join(attempted)
    err_msg = str(last_error) if last_error else "Unknown error"

    logger.error(
        f"[LLMRouter] All providers exhausted for task={task_type}. "
        f"Chain: {chain_log}. Last error: {err_msg}"
    )

    # Return structured graceful error — never crash the request
    return _build_graceful_error(task_type, err_msg)


def _build_graceful_error(task_type: str, err_msg: str) -> dict:
    """Build a graceful response when all providers fail."""
    is_rate_limit = "429" in err_msg or "too many requests" in err_msg.lower()
    is_timeout = "timeout" in err_msg.lower() or "timed out" in err_msg.lower()

    if is_rate_limit:
        title = "Service Busy"
        user_msg = (
            "All AI providers are currently rate-limited. "
            "Please wait a moment and try again."
        )
    elif is_timeout:
        title = "Request Timeout"
        user_msg = (
            "The AI service took too long to respond. "
            "Please check your connection and try again."
        )
    else:
        title = "Service Unavailable"
        user_msg = (
            "The AI service is currently unavailable. "
            "Please try again in a moment."
        )

    if task_type in ("explain", "default"):
        return {
            "title": title,
            "answer_text": user_msg,
            "next_actions": ["Try again"],
        }
    elif task_type == "quiz":
        return {
            "title": title,
            "response_text": user_msg,
            "questions": [],
        }
    elif task_type == "classify":
        return {
            "needs_visual": False,
            "visual_reason": "Service unavailable.",
            "needs_video": False,
            "video_reason": "Service unavailable.",
        }
    elif task_type == "intent":
        return {"intent": "unclear", "topic": "unknown"}
    elif task_type == "clarify":
        return {"is_clear": False, "confidence": 0.0, "topic": "unknown"}
    else:
        return {"title": title, "answer_text": user_msg, "next_actions": []}
