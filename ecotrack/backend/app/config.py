from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "db"
    db_port: int = 3306
    db_name: str = "ecotrack_db"
    db_user: str = "ecotrack_user"
    db_password: str = "ecotrack_password"

    secret_key: str = "change-me-in-production-at-least-32-characters"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    openai_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
