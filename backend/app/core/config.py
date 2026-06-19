from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Shiksha Sahayak"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ── CORS ──────────────────────────────────────────────────────────────────
    # In development: Next.js dev proxy rewrites /api/* → localhost:8000/api/*
    # so the browser never sees a cross-origin request.
    # In production: set ALLOWED_ORIGINS to your actual domain(s).
    # Never use ["*"] in production with credentials enabled.
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",   # Next.js dev server
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://localhost:3001",   # Alternate port if needed
    ]

    # ── LLM Providers ─────────────────────────────────────────────────────────
    # OpenRouter (fallback)
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "google/gemma-4-31b-it:free"

    # Groq (primary)
    GROQ_API_KEY: str = ""
    GROQ_MODEL_STRONG: str = "llama-3.3-70b-versatile"
    GROQ_MODEL_FAST: str = "llama-3.1-8b-instant"

    # Ollama (local fallback)
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    class Config:
        env_file = ".env"
        # ALLOWED_ORIGINS env var overrides CORS_ORIGINS if set as comma list
        # e.g. ALLOWED_ORIGINS=https://myapp.com,https://api.myapp.com


@lru_cache()
def get_settings():
    return Settings()
