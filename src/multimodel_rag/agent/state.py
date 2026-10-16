from typing import TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict):
    question: str              # the user's original question
    search_query: str          # text used for the search (may be rewritten)
    rewrite_count: int         # how many times the query was rewritten
    documents: list[Document]  # chunks found in Pinecone
    image_paths: list[str]     # images to send to the vision model
    is_relevant: bool          # did the grader say the context is useful?
    used_vision: bool          # was the vision model used?
    answer: str                # final answer