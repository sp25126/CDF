"""
LLM Router — single entry point for all LLM calls.

Routing policy:
  Groq    → primary (fast, cheap, strong)
  OpenRouter → fallback (broader model access)
  Ollama  → local emergency fallback

The frontend NEVER knows which provider was used.
The response contract is identical regardless of provider.
"""
import logging
from typing import Optional

from app.providers.groq_provider import GroqProvider
from app.providers.openrouter_provider import OpenRouterProvider
from app.providers.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)

# Instantiate once at module load
_groq = GroqProvider()
_openrouter = OpenRouterProvider()
_ollama = OllamaProvider()

# Provider chain: ordered by preference
PROVIDER_CHAIN = [_groq, _openrouter, _ollama]


async def route_chat(
    messages: list,
    task_type: str = "default",
    response_format: Optional[dict] = None,
) -> dict:
    """
    Try providers in order: Groq → OpenRouter → Ollama.
    Returns parsed dict on success.
    Raises a descriptive RuntimeError if all providers fail.

    Logs:
        - provider attempted
        - fallback reason
        - final provider that succeeded
        - error type if all fail
    """
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
