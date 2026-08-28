import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

DATA_DIR.mkdir(exist_ok=True, parents=True)
DB_DIR.mkdir(exist_ok=True, parents=True)
VECTORSTORE_DIR.mkdir(exist_ok=True, parents=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Lab Manual AI Assistant API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Directory Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    DB_DIR: Path = DB_DIR
    VECTORSTORE_DIR: Path = VECTORSTORE_DIR

    # Database
    DATABASE_URL: str = f"sqlite:///{DB_DIR / 'lab_manuals.db'}"

    # LLM Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto")

    # Vector Store & Embedding Settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 4

    # File Upload Limits
    MAX_FILE_SIZE_MB: int = 50

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
