from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from multimodel_rag.agent import nodes
from multimodel_rag.agent.state import RAGState
from multimodel_rag.config import get_settings


def route_after_grading(state: RAGState) -> str:
    """Decides the next step after grading."""
    if state["is_relevant"]:
        return "generate_with_vision" if state["image_paths"] else "generate_text"

    if state["rewrite_count"] < get_settings().max_query_rewrites:
        return "rewrite_query"

    # No retries left: answer with what we have
    return "generate_text"


@lru_cache
def get_graph():
    """Builds the graph once and reuses it for every request."""
    builder = StateGraph(RAGState)

    builder.add_node("retrieve", nodes.retrieve)
    builder.add_node("grade_documents", nodes.grade_documents)
    builder.add_node("rewrite_query", nodes.rewrite_query)
    builder.add_node("generate_text", nodes.generate_text)
    builder.add_node("generate_with_vision", nodes.generate_with_vision)

    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "grade_documents")
    builder.add_conditional_edges(
        "grade_documents",
        route_after_grading,
        {
            "generate_with_vision": "generate_with_vision",
            "generate_text": "generate_text",
            "rewrite_query": "rewrite_query",
        },
    )
    builder.add_edge("rewrite_query", "retrieve")
    builder.add_edge("generate_text", END)
    builder.add_edge("generate_with_vision", END)

    return builder.compile()

