from multimodel_rag.agent.graph import route_after_grading
from multimodel_rag.config import get_settings


def make_state(**changes) -> dict:
    """Builds a fake agent state. Pass only the fields you want to change."""
    state = {
        "question": "test question",
        "search_query": "test question",
        "rewrite_count": 0,
        "documents": [],
        "image_paths": [],
        "is_relevant": False,
        "used_vision": False,
        "answer": "",
    }
    state.update(changes)
    return state


def test_relevant_text_goes_to_text_answer():
    state = make_state(is_relevant=True, image_paths=[])
    assert route_after_grading(state) == "generate_text"


def test_relevant_with_image_goes_to_vision():
    state = make_state(is_relevant=True, image_paths=["chart.png"])
    assert route_after_grading(state) == "generate_with_vision"


def test_irrelevant_rewrites_when_retries_left():
    state = make_state(is_relevant=False, rewrite_count=0)
    assert route_after_grading(state) == "rewrite_query"


def test_irrelevant_answers_after_max_rewrites():
    max_rewrites = get_settings().max_query_rewrites
    state = make_state(is_relevant=False, rewrite_count=max_rewrites)
    assert route_after_grading(state) == "generate_text"