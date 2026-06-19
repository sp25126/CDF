"""
OpenAI provider — user-key-based calls to OpenAI's chat completions API.

This provider is ONLY used when the user supplies their own key.
It is not in the default server chain.
"""
import httpx
import json
import logging
import json_repair
from typing import Optional

from app.providers.base import BaseProvider

logger = logging.getLogger(__name__)

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

OPENAI_MODEL_MAP = {
    "explain": "gpt-4o-mini",
    "quiz": "gpt-4o-mini",
    "default": "gpt-4o-mini",
    "classify": "gpt-3.5-turbo",
    "intent": "gpt-3.5-turbo",
    "clarify": "gpt-3.5-turbo",
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


class OpenAIProvider(BaseProvider):
    """
    OpenAI chat completions provider.
    Accepts an optional api_key override for user-supplied keys.
    """

    @property
    def provider_name(self) -> str:
        return "openai"

    def _get_model(self, task_type: str, model_override: Optional[str] = None) -> str:
        if model_override:
            return model_override
        return OPENAI_MODEL_MAP.get(task_type, "gpt-4o-mini")

    async def chat_completion(
        self,
        messages: list,
        task_type: str = "default",
        response_format: Optional[dict] = None,
        api_key: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> dict:
        if not api_key:
            raise RuntimeError("[OpenAI] No API key provided. OpenAI requires a user-supplied key.")

        model = self._get_model(task_type, model_override)

        payload: dict = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
        }
        if response_format and response_format.get("type") == "json_object":
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(OPENAI_CHAT_URL, headers=headers, json=payload)

                if resp.status_code == 401:
                    raise RuntimeError("[OpenAI] Invalid API key.")
                if resp.status_code == 429:
                    raise RuntimeError("[OpenAI] Rate limited or quota exceeded.")
                if resp.status_code == 402:
                    raise RuntimeError("[OpenAI] Quota exhausted.")

                resp.raise_for_status()

                content = resp.json()["choices"][0]["message"]["content"]
                usage = resp.json().get("usage", {})
                logger.info(
                    f"[OpenAI] ✓ model={model} task={task_type} "
                    f"tokens={usage.get('total_tokens', '?')}"
                )
                return json_repair.loads(_strip_fences(content))

            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"[OpenAI] HTTP {e.response.status_code}") from e

    async def health_check(self) -> bool:
        return True  # No server key configured; health is per-user-key
