"""
OpenRouter provider — fallback with model-level routing.

Supports ordered fallback model lists per task type.
Tracks which model actually answered via response headers.
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

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Ordered fallback model lists per task type
OPENROUTER_MODEL_GROUPS = {
    "explain": [
        "google/gemma-4-31b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free",
    ],
    "quiz": [
        "google/gemma-4-31b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free",
    ],
    "classify": [
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free",
    ],
    "intent": [
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free",
    ],
    "clarify": [
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free",
    ],
    "default": [
        "google/gemma-4-31b-it:free",
        "meta-llama/llama-3.2-3b-instruct:free",
    ],
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


class OpenRouterProvider(BaseProvider):
    """
    Fallback provider: OpenRouter with ordered model groups.
    Tries each model in the group list before failing.
    """

    @property
    def provider_name(self) -> str:
        return "openrouter"

    def _get_models(self, task_type: str) -> list:
        return OPENROUTER_MODEL_GROUPS.get(task_type, OPENROUTER_MODEL_GROUPS["default"])

    async def chat_completion(
        self,
        messages: list,
        task_type: str = "default",
        response_format: Optional[dict] = None,
    ) -> dict:
        if not settings.LLM_API_KEY:
            raise RuntimeError("[OpenRouter] LLM_API_KEY not configured.")

        models = self._get_models(task_type)
        headers = {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Shiksha Sahayak",
        }

        last_error = None

        for model in models:
            payload: dict = {"model": model, "messages": messages}
            if response_format:
                payload["response_format"] = response_format

            start = time.monotonic()
            backoff = 1.0

            async with httpx.AsyncClient(timeout=30.0) as client:
                for attempt in range(2):
                    try:
                        resp = await client.post(OPENROUTER_URL, headers=headers, json=payload)

                        if resp.status_code == 429:
                            logger.warning(
                                f"[OpenRouter] Rate limit on model={model} attempt={attempt + 1}"
                            )
                            if attempt < 1:
                                await asyncio.sleep(backoff)
                                backoff *= 2
                                continue
                            # Move to next model
                            break

                        resp.raise_for_status()

                        latency_ms = int((time.monotonic() - start) * 1000)
                        # Track which model actually answered
                        actual_model = resp.headers.get("x-model-used", model)
                        content = resp.json()["choices"][0]["message"]["content"]
                        logger.info(
                            f"[OpenRouter] ✓ provider=openrouter model={actual_model} "
                            f"task={task_type} latency={latency_ms}ms"
                        )
                        return json_repair.loads(_strip_fences(content))

                    except httpx.HTTPStatusError as e:
                        logger.warning(
                            f"[OpenRouter] HTTP error model={model} attempt={attempt+1}: {e}"
                        )
                        last_error = e
                        if attempt < 1:
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            continue
                        break
                    except Exception as e:
                        logger.warning(
                            f"[OpenRouter] Error model={model} attempt={attempt+1}: {e}"
                        )
                        last_error = e
                        if attempt < 1:
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            continue
                        break

            logger.warning(f"[OpenRouter] Model {model} exhausted, trying next.")

        raise RuntimeError(
            f"[OpenRouter] All models exhausted for task={task_type}. Last error: {last_error}"
        )

    async def health_check(self) -> bool:
        if not settings.LLM_API_KEY:
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                )
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"[OpenRouter] Health check failed: {e}")
            return False
