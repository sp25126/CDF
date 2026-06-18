import httpx
import json
import logging
import re
import asyncio
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
        if response_format:
            payload["response_format"] = response_format

        logger.info(f"Sending LLM Request to {self.base_url} with model {self.model}...")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            retries = 3
            backoff = 1.0
            for attempt in range(retries):
                try:
                    response = await client.post(self.base_url, headers=headers, json=payload)
                    if response.status_code == 429:
                        if attempt < retries - 1:
                            logger.warning(f"OpenRouter returned 429 (Too Many Requests). Retrying in {backoff}s...")
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            continue
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
                    if attempt < retries - 1:
                        # If it's a httpx status error with 429, we retry
                        if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                            logger.warning(f"OpenRouter 429 exception. Retrying in {backoff}s...")
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            continue
                    logger.warning(f"OpenRouter LLM call failed: {e}. Falling back to Ollama.")
                    return await self._fallback_to_ollama(messages, response_format)

    async def _fallback_to_ollama(self, messages: list, response_format: dict = None) -> dict:
        ollama_url = "http://localhost:11434/api/chat"
        payload = {
            "model": "gemma2:2b",
            "messages": messages,
            "stream": False
        }
        if response_format:
            payload["format"] = "json"
            
        logger.info(f"Sending LLM Request to Ollama with model {payload['model']}...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(ollama_url, json=payload)
                response.raise_for_status()
                data = response.json()
                content = data["message"]["content"]
                
                content_clean = content.strip()
                if content_clean.startswith("```json"):
                    content_clean = content_clean[7:]
                elif content_clean.startswith("```"):
                    content_clean = content_clean[3:]
                if content_clean.endswith("```"):
                    content_clean = content_clean[:-3]
                content_clean = content_clean.strip()
                
                logger.info("Successfully received response from Ollama.")
                return json.loads(content_clean)
            except Exception as e:
                logger.error(f"Ollama fallback failed: {e}")
                raise e

    async def generate_response(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = await self.get_chat_completion(messages)
        return json.dumps(response) if isinstance(response, dict) else str(response)

llm_service = LLMService()
