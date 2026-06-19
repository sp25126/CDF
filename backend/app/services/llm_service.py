"""
LLM Service — thin wrapper over the multi-provider LLM router.

All actual provider logic lives in app/providers/*.
This module preserves the existing public API so no other service needs to change.
"""
import json
import logging
from typing import Optional

from app.services.llm_router import route_chat
from app.services.validation import validate_response

logger = logging.getLogger(__name__)


class LLMService:
    """
    Public interface for all LLM interactions.
    Delegates to the router which handles: Groq → OpenRouter → Ollama fallback.
    """

    async def get_chat_completion(
        self,
        messages: list,
        response_format: Optional[dict] = None,
        task_type: str = "default",
        user_api_key: Optional[str] = None,
        user_provider: Optional[str] = None,
        model_override: Optional[str] = None,
    ) -> dict:
        """
        Run a chat completion via the provider router.
        If user_api_key + user_provider are set, routes to that provider directly.
        Validates the output schema; if validation fails, logs a warning but
        still returns the result (the caller decides what to do with it).
        """
        result = await route_chat(
            messages=messages,
            task_type=task_type,
            response_format=response_format,
            user_api_key=user_api_key,
            user_provider=user_provider,
            model_override=model_override,
        )

        if not validate_response(result, task_type):
            logger.warning(
                f"[LLMService] Output schema validation failed for task='{task_type}'. "
                f"Returning result anyway: {str(result)[:200]}"
            )

        return result

    async def generate_response(
        self, prompt: str, task_type: str = "default", response_format: Optional[dict] = None
    ) -> str:
        """Single-turn prompt convenience wrapper."""
        messages = [{"role": "user", "content": prompt}]
        response = await self.get_chat_completion(messages, task_type=task_type, response_format=response_format)
        return json.dumps(response) if isinstance(response, dict) else str(response)


# Singleton used throughout the codebase
llm_service = LLMService()
