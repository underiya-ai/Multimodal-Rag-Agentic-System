import uvicorn


def main() -> None:
    """Starts the API server."""
    uvicorn.run(
        "multimodel_rag.main:app",
        host="127.0.0.1",
        port=8000,
    )