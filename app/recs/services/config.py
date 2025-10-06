"""
Configuration service for recommendations.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """Configuration for recommendations service."""

    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_org_id: Optional[str] = os.getenv("OPENAI_ORG_ID")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    rerank_model: str = os.getenv("RERANK_MODEL", "gpt-4o-mini")

    # Data Configuration
    rec_source_json: str = os.getenv("REC_SOURCE_JSON", "/app/data/source.jsonl")
    rec_embed_batch: int = int(os.getenv("REC_EMBED_BATCH", "512"))

    # Admin Configuration
    admin_token: Optional[str] = os.getenv("ADMIN_TOKEN")

    # Index Configuration
    index_path: str = "/app/index"
    embedding_dimension: int = 1536  # text-embedding-3-small dimension

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global config instance
config = Config()
