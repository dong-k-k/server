from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    ai_service_base_url: str
    ai_service_mock_mode: bool = True
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

settings = Settings()
