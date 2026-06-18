import httpx
import json
import logging
import asyncio
import json_repair
from app.core.config import get_settings
from app.services.validation import validate_response

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Ollama settings ────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434"

# Task-based Tier Priorities
TIER_STRONG = ["qwen2.5:3b", "gemma2:2b", "qwen2:0.5b", "gemma4:e2b"]
TIER_MID = ["qwen2.5:3b", "gemma2:2b", "qwen2:0.5b", "gemma4:e2b"]
TIER_SMALL = ["qwen2:0.5b", "qwen2.5:3b", "gemma2:2b", "gemma4:e2b"]

def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers that some models add."""
    s = text.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()


class LLMService:
    def __init__(self):
        self.openrouter_key   = settings.LLM_API_KEY
        self.openrouter_model = settings.LLM_MODEL
        self.openrouter_url   = "https://openrouter.ai/api/v1/chat/completions"

    # ── Ollama model detection ─────────────────────────────────────────────────

    async def _get_available_ollama_models(self, tier_list: list) -> list:
        """Return all available Ollama models from the tier list that are pulled, in priority order."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                resp.raise_for_status()
                models_info = resp.json().get("models", [])
                pulled = {m["name"].split(":")[0] for m in models_info}
                pulled_full = {m["name"] for m in models_info}
                
                available = []
                for candidate in tier_list:
                    base = candidate.split(":")[0]
                    if candidate in pulled_full or base in pulled:
                        available.append(candidate)
                return available
        except Exception as e:
            logger.warning(f"[LLM] Could not reach Ollama to list models: {e}")
        return []

    # ── Ollama Call ────────────────────────────────────────────────────────────

    async def _call_ollama(self, messages: list, response_format: dict = None, model: str = None) -> dict:
        if not model:
            raise RuntimeError("No Ollama model specified")

        payload: dict = {"model": model, "messages": messages, "stream": False}
        if response_format:
            payload["format"] = "json"

        logger.info(f"[LLM] → Ollama ({model})")
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
            resp.raise_for_status()
            content = resp.json()["message"]["content"]
            return json_repair.loads(_strip_markdown_fences(content))

    # ── OpenRouter Call ────────────────────────────────────────────────────────

    async def _call_openrouter(self, messages: list, response_format: dict = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type":  "application/json",
            "HTTP-Referer":  "http://localhost:3000",
            "X-Title":       "Shiksha Sahayak",
        }
        payload: dict = {"model": self.openrouter_model, "messages": messages}
        if response_format:
            payload["response_format"] = response_format

        logger.info(f"[LLM] → OpenRouter ({self.openrouter_model})")
        async with httpx.AsyncClient(timeout=30.0) as client:
            backoff = 1.0
            for attempt in range(3):
                try:
                    resp = await client.post(self.openrouter_url, headers=headers, json=payload)
                    if resp.status_code == 429:
                        logger.warning(f"[LLM] OpenRouter rate limit (429) received (Attempt {attempt+1})")
                        if attempt < 2:
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            continue
                        raise httpx.HTTPStatusError("OpenRouter 429 Too Many Requests", request=resp.request, response=resp)
                    resp.raise_for_status()
                    content = resp.json()["choices"][0]["message"]["content"]
                    return json_repair.loads(_strip_markdown_fences(content))
                except Exception as e:
                    if attempt < 2 and not (isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 401):
                        logger.warning(f"[LLM] OpenRouter attempt {attempt+1} error: {e}. Retrying...")
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    raise e

    # ── Public API ─────────────────────────────────────────────────────────────

    async def get_chat_completion(self, messages: list, response_format: dict = None, task_type: str = "default") -> dict:
        """
        Public entry point. Determines routing tier list and attempts completion,
        validating output schema and retrying with fallbacks on failure.
        """
        # Determine tier
        if task_type in ("explain", "quiz"):
            tier_list = TIER_STRONG
            use_openrouter_first = True
        elif task_type == "classify":
            tier_list = TIER_MID
            use_openrouter_first = False
        elif task_type in ("intent", "clarify"):
            tier_list = TIER_SMALL
            use_openrouter_first = False
        else:
            tier_list = TIER_STRONG
            use_openrouter_first = True

        # Set provider attempt order
        if use_openrouter_first:
            providers = ["openrouter", "ollama"]
        else:
            providers = ["ollama", "openrouter"]

        last_exception = None

        for provider in providers:
            if provider == "openrouter":
                if not self.openrouter_key:
                    logger.info("[LLM] OpenRouter key missing, skipping provider")
                    continue
                try:
                    res = await self._call_openrouter(messages, response_format)
                    if validate_response(res, task_type):
                        return res
                    logger.warning(f"[LLM] OpenRouter output failed validation for task '{task_type}'")
                    
                    # Output validation failed: retry once with same or fallback local model
                    logger.info(f"[LLM] Validation retry: Trying local Ollama fallback for task '{task_type}'")
                except Exception as e:
                    logger.error(f"[LLM] OpenRouter error details: {type(e).__name__} - {e}")
                    last_exception = e

            elif provider == "ollama":
                # Find all available models in tier list
                models = await self._get_available_ollama_models(tier_list)
                if not models:
                    logger.warning(f"[LLM] No available Ollama models found for tier: {tier_list}")
                    continue
                for model in models:
                    try:
                        res = await self._call_ollama(messages, response_format, model=model)
                        if validate_response(res, task_type):
                            return res
                        logger.warning(f"[LLM] Ollama ({model}) output failed validation for task '{task_type}'")
                    except Exception as e:
                        logger.error(f"[LLM] Ollama ({model}) error details: {type(e).__name__} - {e}")
                        last_exception = e

        # Analyze the final error to see if it is a rate limit or timeout
        is_rate_limit = False
        is_timeout = False
        err_msg = str(last_exception) if last_exception else "Unknown error"
        
        if last_exception:
            if "429" in err_msg or "too many requests" in err_msg.lower():
                is_rate_limit = True
            elif "timeout" in err_msg.lower() or "timed out" in err_msg.lower():
                is_timeout = True

        # Last resort fallback if everything failed
        logger.error(f"[LLM] All providers and models failed for task '{task_type}': {err_msg}")
        
        if is_rate_limit:
            return {
                "title": "Rate Limit Exceeded",
                "answer_text": f"The AI service is currently busy (Rate Limit Exceeded). Error detail: {err_msg}. Please try again in a moment.",
                "next_actions": ["Try again"]
            }
        elif is_timeout:
            return {
                "title": "Request Timeout",
                "answer_text": f"The request to the AI service timed out. Error detail: {err_msg}. Please check your connection and try again.",
                "next_actions": ["Try again"]
            }

        # Otherwise generic fallback
        if task_type == "explain":
            return {
                "title": "Explanation",
                "answer_text": f"I'm having trouble retrieving a complete answer right now. Error details: {err_msg}.",
                "next_actions": ["Try again"]
            }
        elif task_type == "quiz":
            return {
                "title": "Quiz",
                "response_text": f"I was unable to load the quiz questions. Error details: {err_msg}.",
                "questions": []
            }
        
        raise RuntimeError(f"All LLM providers and fallbacks exhausted: {last_exception}")

    async def generate_response(self, prompt: str, task_type: str = "default") -> str:
        messages = [{"role": "user", "content": prompt}]
        response = await self.get_chat_completion(messages, task_type=task_type)
        return json.dumps(response) if isinstance(response, dict) else str(response)


llm_service = LLMService()
