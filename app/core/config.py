import os
from pathlib import Path
from pydantic import BaseSettings

# Correctly determine the project root directory
# __file__ -> app/core/config.py
# .parent -> app/core
# .parent -> app
# .parent -> project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables or a .env file.
    """
    # --- RAG Core Settings ---
    EMBEDDING_MODEL_NAME: str
    DOCS_PATH: str
    VECTOR_STORE_PATH: str

    # --- vLLM Settings ---
    LLM_MODEL_NAME: str
    VLLM_API_BASE: str
    VLLM_API_KEY: str

    # --- Database Settings ---
    DATABASE_URL: str

    class Config:
        # Pydantic V1 used `env_file` directly.
        # Pydantic V2 recommends using `pydantic-settings` and `SettingsConfigDict`.
        # We stick to the basic way for broader compatibility.
        case_sensitive = True
        env_file = BASE_DIR / ".env"
        env_file_encoding = 'utf-8'


# Create a single, reusable instance of the settings
settings = Settings()
