from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Multi-Agent AI Orchestration Platform"
    app_env: str = "dev"
    openai_api_key: str | None = None
    llm_provider: str = "mock"  # mock or openai
    db_path: str = "runs.db"
    cors_allow_origins: str = "*"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
