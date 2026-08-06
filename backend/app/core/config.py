import os
from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv


class Settings(BaseSettings):
    APP_NAME: str = "StudyGen AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    MODEL_NAME: str = "gemini-3.6-flash"
    MAX_TOKENS: int = 2048
    

    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

    # Vector DB & Storage
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    EMBEDDING_MODEL: str = "models/embedding-001"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Database
    DATABASE_URL: str = "sqlite:///./studygen.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
