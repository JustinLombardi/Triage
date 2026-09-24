from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://triage:triage@postgres:5432/triage"
    redis_url: str = "redis://redis:6379/0"
    github_token: str = ""
    github_webhook_secret: str = ""
    cors_origin: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
