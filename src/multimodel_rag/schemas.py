from typing import Literal

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """The question sent by the client."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        examples=["Which region had the highest revenue growth?"],
    )


class SourceItem(BaseModel):
    """Where a piece of the answer came from."""

    page: int
    type: str       # text, table, or visual
    preview: str    # short part of the content


class AskResponse(BaseModel):
    """The answer sent back to the client."""

    answer: str
    used_vision: bool      # was the image model used?
    query_rewrites: int    # how many times the question was rewritten
    sources: list[SourceItem]


class JobResponse(BaseModel):
    """Status of a PDF processing job."""

    job_id: str
    filename: str
    status: Literal["queued", "running", "completed", "failed"]
    chunks_stored: int = 0
    error: str | None = None
