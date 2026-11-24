import os
import tempfile

# Must be set BEFORE the app and settings are imported
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("PINECONE_API_KEY", "test-pinecone-key")
os.environ.setdefault("API_KEY", "test-api-key")
os.environ.setdefault("UPLOAD_DIR", tempfile.mkdtemp())

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from multimodel_rag.main import create_app  # noqa: E402


@pytest.fixture
def client():
    # Not used with 'with', so the lifespan (Pinecone connection) does not run in tests
    return TestClient(create_app())


@pytest.fixture
def auth_headers():
    return {"X-API-Key": os.environ["API_KEY"]}