"""
Shared configuration settings (shared between backend and worker)
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables

    Usage:
        from llmbattler_shared.config import settings

        db_url = settings.postgres_uri
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database URLs
    postgres_uri: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/llmbattler"

    # CORS settings (backend only)
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    # Model configuration (relative to project root)
    models_config_path: str = "config/models.yaml"

    # Worker settings
    worker_interval_hours: int = 1  # Run worker every N hours
    worker_timezone: str = "UTC"

    # LLM API timeouts (seconds)
    llm_connect_timeout: int = 5
    llm_read_timeout: int = 30
    llm_write_timeout: int = 5
    llm_pool_timeout: int = 5

    # LLM API retry settings
    llm_retry_attempts: int = 3
    llm_retry_backoff_base: float = 1.0  # Base delay in seconds (1s, 2s, 4s)

    # Battle settings
    max_follow_ups: int = 5  # Maximum 5 follow-ups (6 total messages)

    # Leaderboard settings
    min_votes_for_leaderboard: int = 5  # Minimum votes to appear on leaderboard

    # ELO settings
    initial_elo: int = 1500
    k_factor: int = 32

    # PostgreSQL connection pool settings
    postgres_pool_size: int = 5
    postgres_max_overflow: int = 10


# Singleton instance
settings = Settings()
