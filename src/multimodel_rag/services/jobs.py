"""Purpose: Runs PDF processing in the background and tracks each job’s status. The uploaded file is deleted after processing, so the disk does not fill up."""

import threading
from pathlib import Path

from multimodel_rag.schemas import JobResponse
from multimodel_rag.services.pdf_processor import ingest_pdf


class JobStore:
    """Thread-safe storage for job status."""

    def __init__(self) -> None:
        self._jobs: dict[str, JobResponse] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str, filename: str) -> JobResponse:
        job = JobResponse(job_id=job_id, filename=filename, status="queued")
        with self._lock:
            self._jobs[job_id] = job
        return job

    def update(self, job_id: str, **changes) -> None:
        with self._lock:
            self._jobs[job_id] = self._jobs[job_id].model_copy(update=changes)

    def get(self, job_id: str) -> JobResponse | None:
        with self._lock:
            return self._jobs.get(job_id)


# One shared store for the whole app
job_store = JobStore()


def run_ingestion(job_id: str, pdf_path: Path) -> None:
    """Background task: processes the PDF and updates the job status."""
    job_store.update(job_id, status="running")
    try:
        chunks = ingest_pdf(pdf_path)
        job_store.update(job_id, status="completed", chunks_stored=chunks)
    except Exception as error:
        # Only the error type is shown to the client, not internal details
        job_store.update(
            job_id,
            status="failed",
            error=f"Processing failed ({type(error).__name__}).",
        )
    finally:
        pdf_path.unlink(missing_ok=True)  # clean up the uploaded file