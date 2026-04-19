from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Cybercrime Complaint Guide — India (MVP)"
    database_url: str = "sqlite:///./ailegal.db"
    ai_provider: str = "firebase"
    enable_seed_data: bool = False
    enable_heuristic_fallback: bool = False
    firebase_project_id: Optional[str] = None
    firebase_location: str = "us-central1"
    firebase_model: str = "gemini-2.5-flash"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    assistant_model_version: str = "v1"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    # e.g. https://.*\\.vercel\\.app — use when frontend is on Vercel previews
    cors_origin_regex: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
