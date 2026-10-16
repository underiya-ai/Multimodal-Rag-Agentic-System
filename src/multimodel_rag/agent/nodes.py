from pathlib import Path

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage

from multimodel_rag.agent.state import RAGState
from multimodel_rag.config import get_settings
from multimodel_rag.services.images import image_to_data_uri
from multimodel_rag.services.llm import get_text_llm, get_vision_llm
from multimodel_rag.services.vector_store import get_vectorstore

NOT_FOUND_MESSAGE = "I could not find that information in the report."


def format_context(documents: list[Document]) -> str:
    """Joins chunks into one text block, with a page and type label on each."""
    parts = []
    for doc in documents:
        label = f"[Page {doc.metadata.get('page')} | {doc.metadata.get('type')}]"
        parts.append(f"{label}\n{doc.page_content}")
    return "\n\n".join(parts)


def retrieve(state: RAGState) -> dict:
    """Step 1: search Pinecone for the most relevant chunks."""
    settings = get_settings()
    documents = get_vectorstore().similarity_search(
        state["search_query"],
        k=settings.top_k,
    )

    image_paths = []
    for doc in documents:
        if doc.metadata.get("type") != "visual":
            continue
        image_path = doc.metadata.get("image_path")
        if image_path and Path(image_path).exists():
            image_paths.append(image_path)

    return {
        "documents": documents,
        "image_paths": image_paths[: settings.max_images_per_answer],
    }


def grade_documents(state: RAGState) -> dict:
    """Step 2: ask the LLM whether the context helps answer the question."""
    prompt = (
        "You are grading retrieved context.\n"
        f"Question: {state['question']}\n\n"
        f"Context:\n{format_context(state['documents'])}\n\n"
        "Does the context contain information that helps answer the question? "
        "Reply with only 'yes' or 'no'."
    )
    reply = get_text_llm().invoke(prompt).content.strip().lower()
    return {"is_relevant": reply.startswith("yes")}



def rewrite_query(state: RAGState) -> dict:
    """Step 3: rephrase the question so the next search works better."""
    prompt = (
        "Rewrite this question so it is better for searching a company report. "
        "Keep the same meaning. Return only the new question.\n"
        f"Question: {state['question']}"
    )
    new_query = get_text_llm().invoke(prompt).content.strip()
    return {
        "search_query": new_query,
        "rewrite_count": state["rewrite_count"] + 1,
    }


def generate_text(state: RAGState) -> dict:
    """Step 4a: answer using text context only."""
    prompt = (
        "You answer questions about a company report. Use ONLY the context below.\n"
        "Mention page numbers. If the answer is not in the context, say exactly:\n"
        f'"{NOT_FOUND_MESSAGE}"\n\n'
        f"CONTEXT:\n{format_context(state['documents'])}\n\n"
        f"QUESTION: {state['question']}\n\nANSWER:"
    )
    answer = get_text_llm().invoke(prompt).content.strip()
    return {"answer": answer, "used_vision": False}


def generate_with_vision(state: RAGState) -> dict:
    """Step 4b: answer using text context and the relevant images."""
    prompt = (
        "You answer questions about a company report. "
        "Use ONLY the context and the attached images.\n"
        "Mention page numbers. If the answer is not in the context, say exactly:\n"
        f'"{NOT_FOUND_MESSAGE}"\n\n'
        f"CONTEXT:\n{format_context(state['documents'])}\n\n"
        f"QUESTION: {state['question']}"
    )

    content = [{"type": "text", "text": prompt}]
    for image_path in state["image_paths"]:
        content.append({
            "type": "image_url",
            "image_url": {"url": image_to_data_uri(image_path)},
        })

    answer = get_vision_llm().invoke([HumanMessage(content=content)]).content.strip()
    return {"answer": answer, "used_vision": True}