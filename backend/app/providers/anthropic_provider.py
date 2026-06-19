"""
Anthropic provider — user-key-based calls to Anthropic's messages API.

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

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

ANTHROPIC_MODEL_MAP = {
    "explain": "claude-3-5-haiku-20241022",
    "quiz": "claude-3-5-haiku-20241022",
    "default": "claude-3-5-haiku-20241022",
    "classify": "claude-3-5-haiku-20241022",
    "intent": "claude-3-5-haiku-20241022",
    "clarify": "claude-3-5-haiku-20241022",
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

def _convert_messages(messages: list) -> tuple[Optional[str], list]:
    """
    Convert OpenAI-style messages to Anthropic format.
    Anthropic: system prompt is separate, messages must alternate user/assistant.
    """
    system = None
    converted = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            system = content
        else:
            converted.append({"role": role, "content": content})
    return system, converted


class AnthropicProvider(BaseProvider):
    """
    Anthropic Claude provider.
    Accepts an optional api_key override for user-supplied keys.
    """

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def _get_model(self, task_type: str, model_override: Optional[str] = None) -> str:
        if model_override:
            return model_override
        return ANTHROPIC_MODEL_MAP.get(task_type, "claude-3-5-haiku-20241022")

    async def chat_completion(
        self,
        messages: list,
        task_type: str = "default",
        response_format: Optional[dict] = None,
        api_key: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> dict:
        if not api_key:
            raise RuntimeError("[Anthropic] No API key provided. Anthropic requires a user-supplied key.")

        model = self._get_model(task_type, model_override)
        system_prompt, converted_messages = _convert_messages(messages)

        payload: dict = {
            "model": model,
            "max_tokens": 4096,
            "messages": converted_messages,
        }
        if system_prompt:
            payload["system"] = system_prompt

        headers = {
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(ANTHROPIC_MESSAGES_URL, headers=headers, json=payload)

                if resp.status_code == 401:
                    raise RuntimeError("[Anthropic] Invalid API key.")
                if resp.status_code == 429:
                    raise RuntimeError("[Anthropic] Rate limited or quota exceeded.")
                if resp.status_code == 402:
                    raise RuntimeError("[Anthropic] Quota exhausted.")

                resp.raise_for_status()

                data = resp.json()
                content = data["content"][0]["text"]
                usage = data.get("usage", {})
                logger.info(
                    f"[Anthropic] ✓ model={model} task={task_type} "
                    f"tokens={usage.get('input_tokens', 0) + usage.get('output_tokens', 0)}"
                )
                return json_repair.loads(_strip_fences(content))

            except httpx.HTTPStatusError as e:
                raise RuntimeError(f"[Anthropic] HTTP {e.response.status_code}") from e

    async def health_check(self) -> bool:
        return True  # Health is per-user-key
