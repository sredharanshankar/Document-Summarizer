"""In-memory store for document-processing jobs.

This is a single-process, in-memory store by design: the app has no
database, and a demo/assessment deployment runs one backend instance.
Jobs are never persisted and do not survive a restart. See the README's
"Limitations" section — a multi-instance production deployment would need
to move this to Redis or a database.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.models.schemas import AnalyzeResult, ErrorPayload, JobStage, JobStatus

# Number of most-recent Q&A exchanges kept and passed as conversation
# context for follow-up questions. Bounds both memory use and how much
# gets resent to the AI provider on every question.
MAX_QA_HISTORY = 6


@dataclass
class Job:
    id: str
    filename: str
    status: JobStatus = JobStatus.PROCESSING
    stage: JobStage = JobStage.QUEUED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result: AnalyzeResult | None = None
    error: ErrorPayload | None = None
    # Populated once extraction/OCR/cleaning finish, ahead of summarization.
    # Cached so /documents/summarize can regenerate just the summary for a
    # new length without re-running extraction/OCR.
    cleaned_text: str | None = None
    file_type: str | None = None
    page_count: int | None = None
    word_count: int | None = None
    used_ocr: bool = False
    # (question, answer) pairs from /documents/ask, oldest first - capped at
    # MAX_QA_HISTORY so a long Q&A session doesn't grow a job's memory
    # footprint or the context sent to the AI provider without bound.
    qa_history: list[tuple[str, str]] = field(default_factory=list)


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, filename: str) -> Job:
        job = Job(id=uuid.uuid4().hex, filename=filename)
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def set_stage(self, job_id: str, stage: JobStage) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                job.stage = stage

    def set_extraction_result(
        self,
        job_id: str,
        *,
        cleaned_text: str,
        file_type: str,
        page_count: int | None,
        word_count: int,
        used_ocr: bool,
    ) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                job.cleaned_text = cleaned_text
                job.file_type = file_type
                job.page_count = page_count
                job.word_count = word_count
                job.used_ocr = used_ocr
                job.stage = JobStage.CLEANING

    def complete(self, job_id: str, result: AnalyzeResult, cleaned_text: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                job.status = JobStatus.COMPLETED
                job.stage = JobStage.DONE
                job.result = result
                job.cleaned_text = cleaned_text

    def append_qa_exchange(self, job_id: str, question: str, answer: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                job.qa_history.append((question, answer))
                if len(job.qa_history) > MAX_QA_HISTORY:
                    job.qa_history = job.qa_history[-MAX_QA_HISTORY:]

    def fail(self, job_id: str, error: ErrorPayload) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                job.status = JobStatus.FAILED
                job.error = error


job_store = JobStore()
