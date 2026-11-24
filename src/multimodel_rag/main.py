from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from multimodel_rag.api.routes import public_router, router
from multimodel_rag.api.ui import ui_router
from multimodel_rag.config import get_settings
from multimodel_rag.middleware import RequestIDMiddleware
from multimodel_rag.services.vector_store import get_vectorstore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs at startup: creates folders and connects to Pinecone early."""
    settings = get_settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.image_dir).mkdir(parents=True, exist_ok=True)

    get_vectorstore()  # first request will not be slow
    yield


def create_app() -> FastAPI:
    """Builds the app. Tests use this too."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    app.include_router(public_router, prefix="/api/v1")
    app.include_router(router, prefix="/api/v1")

    # Serve compiled Perplexity-style React frontend if built
    frontend_dist = Path("frontend/dist")
    if frontend_dist.exists():
        from fastapi.responses import FileResponse
        from fastapi.staticfiles import StaticFiles

        @app.get("/voice")
        def serve_voice_page():
            return FileResponse(frontend_dist / "index.html")

        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    else:
        app.include_router(ui_router)

    return app


app = create_app()