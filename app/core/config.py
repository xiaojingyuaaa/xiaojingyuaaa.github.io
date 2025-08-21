import os
from pathlib import Path
from pydantic import BaseSettings

# 正确地确定项目根目录
# __file__ -> app/core/config.py
# .parent -> app/core
# .parent -> app
# .parent -> 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    应用配置类，从环境变量或.env文件中加载配置。
    """
    # --- RAG核心配置 ---
    EMBEDDING_MODEL_NAME: str # 使用的嵌入模型名称
    DOCS_PATH: str            # 知识库源文件路径
    VECTOR_STORE_PATH: str    # FAISS向量数据库存储路径

    # --- vLLM配置 ---
    LLM_MODEL_NAME: str       # vLLM加载的大语言模型名称
    VLLM_API_BASE: str        # vLLM提供的OpenAI兼容API的基础URL
    VLLM_API_KEY: str         # vLLM API的密钥（本地部署通常为"EMPTY"）

    # --- 数据库配置 ---
    DATABASE_URL: str         # SQLAlchemy数据库连接URL

    class Config:
        # Pydantic V1直接使用 `env_file`。
        # Pydantic V2推荐使用 `pydantic-settings` 和 `SettingsConfigDict`。
        # 此处为保持兼容性，使用基础方式。
        case_sensitive = True
        env_file = BASE_DIR / ".env"
        env_file_encoding = 'utf-8'


# 创建一个可复用的全局配置实例
settings = Settings()
