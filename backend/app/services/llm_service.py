import httpx
import json
import logging
import re
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class LLMService:
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        # Determine if it's OpenRouter or OpenAI
        if "sk-or-" in self.api_key:
            self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        else:
            self.base_url = "https://api.openai.com/v1/chat/completions"

    async def get_chat_completion(self, messages: list, response_format: dict = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if "openrouter.ai" in self.base_url:
            headers["HTTP-Referer"] = "http://localhost:3000"
            headers["X-Title"] = "Shiksha Sahayak"

        payload = {
            "model": self.model,
            "messages": messages
        }
        # Only use json response_format if it is OpenAI or supported model
        if response_format:
            payload["response_format"] = response_format

        logger.info(f"Sending LLM Request to {self.base_url} with model {self.model}...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Sanitize markdown JSON blocks if present
                content_clean = content.strip()
                if content_clean.startswith("```json"):
                    content_clean = content_clean[7:]
                elif content_clean.startswith("```"):
                    content_clean = content_clean[3:]
                if content_clean.endswith("```"):
                    content_clean = content_clean[:-3]
                content_clean = content_clean.strip()
                
                logger.info("Successfully received and parsed LLM response.")
                return json.loads(content_clean)
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                if 'response' in locals() and response is not None:
                    logger.error(f"Response status: {response.status_code}, content: {response.text}")
                raise e

llm_service = LLMService()
