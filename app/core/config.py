from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    ai_service_base_url: str
    ai_service_mock_mode: bool = True
    cors_origins: str = "http://localhost:5173"
    rag_base_url: str = "http://localhost:8001"
    exim_api_key: str = "QItPgQVXjSZk2EZCk3mCorpPeyUrEUTD"
    ecos_api_key: str = "3HEMWZ961Q61X8D1LFAH"

    class Config:
        env_file = ".env"

settings = Settings()