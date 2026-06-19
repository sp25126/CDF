"""
Groq provider — primary fast classroom answer engine.

Uses OpenAI-compatible chat completions at https://api.groq.com/openai/v1
Compliant with Groq's supported fields (no logprobs, logit_bias, top_logprobs, n>1).
"""
import httpx
import json
import logging
import asyncio
import time
import json_repair
from typing import Optional

from app.providers.base import BaseProvider
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_CHAT_URL = f"{GROQ_BASE_URL}/chat/completions"

# Model selection per task type
GROQ_MODEL_MAP = {
    "explain": settings.GROQ_MODEL_STRONG,   # llama3-70b-8192
    "quiz":    settings.GROQ_MODEL_STRONG,
    "default": settings.GROQ_MODEL_STRONG,
    "classify": settings.GROQ_MODEL_FAST,    # llama3-8b-8192
    "intent":   settings.GROQ_MODEL_FAST,
    "clarify":  settings.GROQ_MODEL_FAST,
}

def _strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()


class GroqProvider(BaseProvider):
    """
    Primary provider: Groq fast inference.
    Routes explain/quiz to llama3-70b-8192, lightweight tasks to llama3-8b-8192.
    """

    @property
    def provider_name(self) -> str:
        return "groq"

    def _get_model(self, task_type: str) -> str:
        return GROQ_MODEL_MAP.get(task_type, settings.GROQ_MODEL_STRONG)

    async def chat_completion(
        self,
        messages: list,
        task_type: str = "default",
        response_format: Optional[dict] = None,
        api_key: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> dict:
        # Use user-supplied key if provided, otherwise fall back to server key
        effective_key = api_key or settings.GROQ_API_KEY
        if not effective_key:
            raise RuntimeError("[Groq] GROQ_API_KEY not configured.")

        model = model_override or self._get_model(task_type)

        # Build Groq-compatible payload — no unsupported fields
        payload: dict = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
        }
        # Groq supports response_format for JSON mode on some models
        if response_format and response_format.get("type") == "json_object":
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {effective_key}",
            "Content-Type": "application/json",
        }

        start = time.monotonic()
        backoff = 1.0

        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(3):
                try:
                    resp = await client.post(GROQ_CHAT_URL, headers=headers, json=payload)

                    if resp.status_code == 429:
                        logger.warning(
                            f"[Groq] Rate limit 429 on attempt {attempt + 1}."
                        )
                        if attempt < 2:
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            continue
                        raise httpx.HTTPStatusError(
                            "Groq 429 Too Many Requests",
                            request=resp.request,
                            response=resp,
                        )

                    resp.raise_for_status()

                    latency_ms = int((time.monotonic() - start) * 1000)
                    content = resp.json()["choices"][0]["message"]["content"]
                    usage = resp.json().get("usage", {})
                    logger.info(
                        f"[Groq] ✓ provider=groq model={model} task={task_type} "
                        f"latency={latency_ms}ms tokens={usage.get('total_tokens', '?')}"
                    )
                    return json_repair.loads(_strip_fences(content))

                except httpx.HTTPStatusError:
                    raise
                except Exception as e:
                    logger.warning(f"[Groq] Attempt {attempt + 1} error: {e}")
                    if attempt < 2:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    raise

    async def health_check(self) -> bool:
        if not settings.GROQ_API_KEY:
            return False
        try:
            # Ping with a minimal completion
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    GROQ_CHAT_URL,
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.GROQ_MODEL_FAST,
                        "messages": [{"role": "user", "content": "ping"}],
                        "max_tokens": 1,
                    },
                )
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"[Groq] Health check failed: {e}")
            return False
