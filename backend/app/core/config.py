from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Shiksha Sahayak"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # OpenRouter (fallback provider)
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "google/gemma-4-31b-it:free"

    # Groq (primary provider)
    GROQ_API_KEY: str = ""
    GROQ_MODEL_STRONG: str = "llama-3.3-70b-versatile"
    GROQ_MODEL_FAST: str = "llama-3.1-8b-instant"

    # Ollama (local fallback)
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
