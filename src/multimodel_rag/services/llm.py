from  functools import lru_cache
from langchain_groq import ChatGroq
from multimodel_rag.config import get_settings


@lru_cache
def get_text_llm() -> ChatGroq:
    """Model for text tasks: grading, rewriting, and text answers."""

    settings =get_settings()

    return ChatGroq(
        model=settings.text_model,
        api_key=settings.groq_api_key,
        temperature=0
    )

@lru_cache
def get_vision_llm() -> ChatGroq:
    """Model that can read Image (charts and diagram)"""
    settings=get_settings()
    return ChatGroq(
        model=settings.vision_model,
        api_key=settings.vision_model,
        temperature=0
    )