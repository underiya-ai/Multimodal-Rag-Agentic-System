import time
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone,ServerlessSpec
from multimodel_rag.config import get_settings


@lru_cache
def get_embeddings() -> HuggingFaceEmbeddings:
    """Model turn text into Number [list of number] """
    settings=get_settings()
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        encode_kwargs={"normalize_embeddings":True}
    )



@lru_cache
def get_vectorstore() -> PineconeVectorStore:
    """Vector store connected to Pinecone. Creates the index on first use."""
    settings = get_settings()
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)

    if not pc.has_index(settings.pinecone_index_name):
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.embedding_dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.pinecone_cloud,
                region=settings.pinecone_region,
            ),
        )
        # Wait until Pinecone says the index is ready
        while not pc.describe_index(settings.pinecone_index_name).status["ready"]:
            time.sleep(2)

    return PineconeVectorStore(
        index=pc.Index(settings.pinecone_index_name),
        embedding=get_embeddings(),
        namespace=settings.pinecone_namespace,
    )