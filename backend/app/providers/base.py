"""
Abstract base provider for all LLM backends.
All providers must implement this interface.
"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseProvider(ABC):
    """
    Abstract contract for all LLM providers.
    The router calls these methods; the frontend never knows which provider ran.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier, e.g. 'groq', 'openrouter', 'ollama'."""
        ...

    @abstractmethod
    async def chat_completion(
        self,
        messages: list,
        task_type: str = "default",
        response_format: Optional[dict] = None,
    ) -> dict:
        """
        Run a chat completion and return a parsed dict.
        Must raise on unrecoverable failures so the router can try the next provider.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable and accepting requests."""
        ...
