from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #APP settings
    APP_NAME: str = "StudyGen AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # LLM
    LLM_PROVIDER: str | None = None
    MODEL_NAME: str = "qwen2.5:1.5b"
    MAX_TOKENS: int = 2048
    QWEN_API_URL: str

    # API Keys
    GOOGLE_API_KEY: str | None = None

    # Vector DB & Storage
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Database
    DATABASE_URL: str 

    # Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120



    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM - Hugging Face
    HF_API_URL: str | None = None
    HF_TOKEN: str  | None = None
    HF_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    MAX_TOKENS: int = 2048 

    # Re-ranker (FlashRank for Phase 2)
    RERANKER_ENABLED: bool = True
    RERANKER_MODEL: str = "ms-marco-MiniLM-L-12-v2"
    
settings = Settings()