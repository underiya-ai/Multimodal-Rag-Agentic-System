from unittest.mock import MagicMock, patch


def test_health_is_public(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_voice_ui_is_public(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "NovaCore" in response.text or "Multimodal" in response.text

    voice_response = client.get("/voice")
    assert voice_response.status_code == 200


def test_ask_requires_api_key(client):
    response = client.post("/api/v1/ask", json={"question": "What is the revenue?"})
    assert response.status_code == 401


def test_ask_returns_answer(client, auth_headers):
    fake_graph = MagicMock()
    fake_graph.invoke.return_value = {
        "answer": "Europe",
        "used_vision": False,
        "rewrite_count": 0,
        "documents": [],
    }

    with patch("multimodel_rag.api.routes.get_graph", return_value=fake_graph):
        response = client.post(
            "/api/v1/ask",
            json={"question": "Which region grew fastest?"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json()["answer"] == "Europe"


def test_ingest_rejects_non_pdf(client, auth_headers):
    response = client.post(
        "/api/v1/ingest",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_ingest_returns_job_with_queued_status(client, auth_headers):
    with patch("multimodel_rag.api.routes.run_ingestion"):
        response = client.post(
            "/api/v1/ingest",
            files={"file": ("report.pdf", b"%PDF-1.4 test", "application/pdf")},
            headers=auth_headers,
        )
        assert response.status_code == 202
        job_id = response.json()["job_id"]

        status_response = client.get(f"/api/v1/jobs/{job_id}", headers=auth_headers)

    assert status_response.status_code == 200
    assert status_response.json()["status"] == "queued"


def test_unknown_job_returns_404(client, auth_headers):
    response = client.get("/api/v1/jobs/does-not-exist", headers=auth_headers)
    assert response.status_code == 404


def test_voice_ask_rejects_non_audio_file(client, auth_headers):
    response = client.post(
        "/api/v1/voice/ask",
        files={"file": ("document.pdf", b"%PDF-1.4", "application/pdf")},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "Unsupported audio format" in response.json()["detail"]


def test_voice_ask_endpoint(client, auth_headers):
    fake_graph = MagicMock()
    fake_graph.invoke.return_value = {
        "answer": "Net profit was 10 million dollars.",
        "used_vision": False,
        "rewrite_count": 0,
        "documents": [],
    }

    with (
        patch("multimodel_rag.api.routes.transcribe_audio", return_value="What was the profit?"),
        patch("multimodel_rag.api.routes.get_graph", return_value=fake_graph),
        patch("multimodel_rag.api.routes.synthesize_speech", return_value=b"fake-mp3-bytes"),
    ):
        response = client.post(
            "/api/v1/voice/ask",
            files={"file": ("speech.wav", b"riffwavdata", "audio/wav")},
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["transcribed_question"] == "What was the profit?"
    assert data["answer"] == "Net profit was 10 million dollars."
    assert data["audio_base64"].startswith("data:audio/mp3;base64,")


def test_voice_speak_endpoint(client, auth_headers):
    fake_graph = MagicMock()
    fake_graph.invoke.return_value = {
        "answer": "The quick brown fox.",
        "used_vision": False,
        "rewrite_count": 0,
        "documents": [],
    }

    with (
        patch("multimodel_rag.api.routes.get_graph", return_value=fake_graph),
        patch("multimodel_rag.api.routes.synthesize_speech", return_value=b"fake-mp3-bytes"),
    ):
        response = client.post(
            "/api/v1/voice/speak",
            json={"question": "Tell me something"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"fake-mp3-bytes"
