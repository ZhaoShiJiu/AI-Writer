from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://novel_writer:novel_write_2024@localhost:5432/novel_write"
    redis_url: str = "redis://:redis_write_2024@localhost:6379"
    llm_gateway_url: str = "http://localhost:8001"

    context_max_chars: int = 4000
    continuation_target_chars: int = 400

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
