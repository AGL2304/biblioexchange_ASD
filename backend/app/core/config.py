from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret: str = "dev-secret-change-me"
    jwt_expires_minutes: int = 60
    database_url: str = "postgresql+psycopg2://biblioexchange:change-me@db:5432/biblioexchange"

    class Config:
        env_file = ".env"


settings = Settings()
