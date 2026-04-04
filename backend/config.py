from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Backend configuration."""

    model_config = SettingsConfigDict(
        env_prefix="BACKEND_",
        env_file=".env",
        extra="ignore",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database (placeholder for MVP)
    database_url: str = "postgresql+asyncpg://user:pass@localhost/booking"

    # Connection pooling
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False

    # Logging
    log_level: str = "INFO"


settings = Settings()
