"""
Ollama provider — local emergency fallback.

Uses Ollama's /api/chat endpoint. Gracefully returns None if Ollama is unreachable
so the router can skip it without crashing.
"""
import httpx
import logging
import time
import json_repair
from typing import Optional

from app.providers.base import BaseProvider
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Task-based model tier preferences for Ollama
OLLAMA_MODEL_TIERS = {
    "explain": ["qwen2.5:3b", "gemma2:2b", "qwen2:0.5b"],
    "quiz":    ["qwen2.5:3b", "gemma2:2b", "qwen2:0.5b"],
    "classify":["qwen2:0.5b", "qwen2.5:3b"],
    "intent":  ["qwen2:0.5b", "qwen2.5:3b"],
    "clarify": ["qwen2:0.5b", "qwen2.5:3b"],
    "default": ["qwen2.5:3b", "qwen2:0.5b"],
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


class OllamaProvider(BaseProvider):
    """
    Local fallback provider using Ollama.
    If Ollama is not running, this provider raises so the router skips it.
    """

    @property
    def provider_name(self) -> str:
        return "ollama"

    def _base_url(self) -> str:
        return settings.OLLAMA_BASE_URL

    async def _get_available_models(self, tier_list: list) -> list:
        """Return pulled models from tier_list in priority order."""
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(f"{self._base_url()}/api/tags")
                resp.raise_for_status()
                models_info = resp.json().get("models", [])
                pulled = {m["name"] for m in models_info}
                pulled_base = {m["name"].split(":")[0] for m in models_info}
                return [
                    m for m in tier_list
                    if m in pulled or m.split(":")[0] in pulled_base
                ]
        except Exception as e:
            logger.warning(f"[Ollama] Cannot list models: {e}")
            return []

    async def chat_completion(
        self,
        messages: list,
        task_type: str = "default",
        response_format: Optional[dict] = None,
    ) -> dict:
        tier_list = OLLAMA_MODEL_TIERS.get(task_type, OLLAMA_MODEL_TIERS["default"])
        available = await self._get_available_models(tier_list)

        if not available:
            raise RuntimeError("[Ollama] No available models found (is Ollama running?)")

        last_error = None
        for model in available:
            payload: dict = {"model": model, "messages": messages, "stream": False}
            if response_format:
                payload["format"] = "json"

            start = time.monotonic()
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    resp = await client.post(
                        f"{self._base_url()}/api/chat", json=payload
                    )
                    resp.raise_for_status()
                    latency_ms = int((time.monotonic() - start) * 1000)
                    content = resp.json()["message"]["content"]
                    logger.info(
                        f"[Ollama] ✓ provider=ollama model={model} "
                        f"task={task_type} latency={latency_ms}ms"
                    )
                    return json_repair.loads(_strip_fences(content))
            except Exception as e:
                logger.warning(f"[Ollama] Model {model} failed: {e}")
                last_error = e
                continue

        raise RuntimeError(
            f"[Ollama] All available models failed for task={task_type}. "
            f"Last error: {last_error}"
        )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(f"{self._base_url()}/api/tags")
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"[Ollama] Health check failed: {e}")
            return False
