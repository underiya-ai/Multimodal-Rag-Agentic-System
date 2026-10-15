from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app settings, read from the .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Agentic Multimodal RAG"

    # API keys (must be set in .env)
    groq_api_key: str
    pinecone_api_key: str
    api_key: str  # secret key that clients send to call our API

    # AI models
    text_model: str = "openai/gpt-oss-20b"
    vision_model: str = "qwen/qwen3.8-27b"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384  # vector size of the MiniLM model

    # Pinecone (vector database)
    pinecone_index_name: str = "novacore-multimodal-rag"
    pinecone_namespace: str = "fy2026-demo"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    # RAG settings
    top_k: int = 5                   # how many chunks to retrieve per question
    max_query_rewrites: int = 2      # maximum number of times the query can be rewritten
    max_images_per_answer: int = 3   # maximum images sent to the vision model per answer

    # Folders
    upload_dir: str = "data/uploads"
    image_dir: str = "data/images"

    # Upload limit and allowed frontend URLs
    max_upload_mb: int = 20
    allowed_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Loads settings only once. The .env file is not read again on every call."""
    return Settings()