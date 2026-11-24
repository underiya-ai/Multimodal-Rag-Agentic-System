from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Response, UploadFile

from multimodel_rag.agent.graph import get_graph
from multimodel_rag.config import get_settings
from multimodel_rag.core.security import verify_api_key
from multimodel_rag.schemas import AskRequest, AskResponse, JobResponse, SourceItem, VoiceAskResponse
from multimodel_rag.services.jobs import job_store, run_ingestion
from multimodel_rag.services.voice import audio_to_data_uri, synthesize_speech, transcribe_audio

# Public routes: no API key needed
public_router = APIRouter()

# Protected routes: every request needs the X-API-Key header
router = APIRouter(dependencies=[Depends(verify_api_key)])

CHUNK_SIZE = 1024 * 1024  # read the upload 1 MB at a time


def save_upload(file: UploadFile, destination: Path, max_bytes: int) -> None:
    """Saves the upload in pieces. Stops and deletes the file if it is too big."""
    written = 0
    try:
        with destination.open("wb") as out_file:
            while chunk := file.file.read(CHUNK_SIZE):
                written += len(chunk)
                if written > max_bytes:
                    raise HTTPException(status_code=413, detail="File too large.")
                out_file.write(chunk)
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise


@public_router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/ingest", response_model=JobResponse, status_code=202)
def ingest_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Uploads a PDF. Processing runs in the background and a job_id is returned."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save under a random ID, not the user's filename (prevents path tricks)
    job_id = uuid4().hex
    saved_path = upload_dir / f"{job_id}.pdf"
    save_upload(file, saved_path, max_bytes=settings.max_upload_mb * 1024 * 1024)

    job = job_store.create(job_id, filename=file.filename)
    background_tasks.add_task(run_ingestion, job_id, saved_path)
    return job


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_status(job_id: str):
    """Returns the current status of an ingestion job."""
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.post("/ask", response_model=AskResponse)
def ask_question(body: AskRequest):
    """Runs the agent on the question and returns the answer."""
    start_state = {
        "question": body.question,
        "search_query": body.question,
        "rewrite_count": 0,
        "documents": [],
        "image_paths": [],
        "is_relevant": False,
        "used_vision": False,
        "answer": "",
    }

    try:
        result = get_graph().invoke(start_state)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate an answer.")

    sources = [
        SourceItem(
            page=int(doc.metadata.get("page", 0)),
            type=doc.metadata.get("type", "unknown"),
            preview=doc.page_content[:150].replace("\n", " "),
        )
        for doc in result["documents"]
    ]

    return AskResponse(
        answer=result["answer"],
        used_vision=result["used_vision"],
        query_rewrites=result["rewrite_count"],
        sources=sources,
    )


ALLOWED_AUDIO_EXTENSIONS = {
    ".flac", ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".ogg", ".opus", ".wav", ".webm"
}


@router.post("/voice/ask", response_model=VoiceAskResponse)
async def ask_with_voice(file: UploadFile = File(...)):
    """Receives user spoken query as audio, runs RAG on PDF, and returns voice answer."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Audio file must have a filename.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported audio format '{suffix}'. "
                f"Please upload an audio recording ({', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))})."
            ),
        )

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file provided.")

    try:
        question_text = transcribe_audio(audio_bytes, filename=file.filename)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Speech transcription failed: {exc}")

    if not question_text:
        raise HTTPException(status_code=400, detail="No speech could be recognized in the audio.")

    start_state = {
        "question": question_text,
        "search_query": question_text,
        "rewrite_count": 0,
        "documents": [],
        "image_paths": [],
        "is_relevant": False,
        "used_vision": False,
        "answer": "",
    }

    try:
        result = get_graph().invoke(start_state)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate an answer.")

    answer_text = result["answer"]

    # Synthesize the answer into speech
    try:
        audio_mp3 = await synthesize_speech(answer_text)
        audio_uri = audio_to_data_uri(audio_mp3)
    except Exception:
        audio_uri = ""

    sources = [
        SourceItem(
            page=int(doc.metadata.get("page", 0)),
            type=doc.metadata.get("type", "unknown"),
            preview=doc.page_content[:150].replace("\n", " "),
        )
        for doc in result["documents"]
    ]

    return VoiceAskResponse(
        transcribed_question=question_text,
        answer=answer_text,
        audio_base64=audio_uri,
        used_vision=result["used_vision"],
        query_rewrites=result["rewrite_count"],
        sources=sources,
    )


@router.post("/voice/speak")
async def speak_text(body: AskRequest):
    """Answers a text question and returns raw MP3 audio directly for streaming playback."""
    start_state = {
        "question": body.question,
        "search_query": body.question,
        "rewrite_count": 0,
        "documents": [],
        "image_paths": [],
        "is_relevant": False,
        "used_vision": False,
        "answer": "",
    }

    try:
        result = get_graph().invoke(start_state)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate an answer.")

    audio_bytes = await synthesize_speech(result["answer"])
    return Response(content=audio_bytes, media_type="audio/mpeg")