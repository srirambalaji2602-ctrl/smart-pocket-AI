from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"

    secret_key: str = "change-this-secret-key"

    database_url: str = "sqlite:///./pocketsmart.db"

    gemini_api_key: str | None = None

    gemini_model: str = "gemini-2.5-flash"

    access_token_expire_minutes: int = 1440

    max_image_mb: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def upload_dir(self) -> Path:
        directory = self.base_dir / "uploads"
        directory.mkdir(parents=True, exist_ok=True)
        return directory


@lru_cache
def get_settings() -> Settings:
    return Settings()