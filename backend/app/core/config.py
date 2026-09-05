import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "StudyGen AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # LLM
    MODEL_NAME: str = "Qwen3-14B"
    MAX_TOKENS: int = 2048
    QWEN_API_URL: str

    # API Keys
    GOOGLE_API_KEY: str | None = None

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
        extra="ignore",
    )


    # LLM - Hugging Face
    # LLM
    HF_API_URL: str
    HF_TOKEN: str
    HF_MODEL: str
    MAX_TOKENS: int = 2048


settings = Settings()