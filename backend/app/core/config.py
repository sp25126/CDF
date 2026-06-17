from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Shiksha Sahayak"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # LLM Provider
    LLM_API_KEY: str = "sk-placeholder"
    LLM_MODEL: str = "gpt-4-turbo-preview"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
