"""Full per-job pipeline: validate (already done at the API layer) -> extract
-> [OCR] -> clean -> summarize -> done. Runs synchronously in a thread pool
(see app/api/routes/documents.py) since PDF parsing, OCR, and the AI call
are all blocking. Every stage transition is written to the job store so
the frontend's progress UI reflects real, not simulated, progress.
"""

from __future__ import annotations

import logging
import time

from app.config.settings import Settings
from app.models.schemas import AnalyzeResult, DocumentMetadata, ErrorPayload, JobStage, SummaryLength
from app.services.document_processor import extract_document_text, get_default_ocr_provider
from app.services.job_store import JobStore
from app.services.job_store import job_store as default_job_store
from app.services.ocr.base import OCRProvider
from app.services.summary_service import SummaryService, get_ai_provider
from app.services.text_cleaner import clean_pages
from app.utils.errors import AppError, EmptyTextError

logger = logging.getLogger("document_summary_assistant")


def run_analysis_pipeline(
    job_id: str,
    content: bytes,
    extension: str,
    summary_length: SummaryLength,
    settings: Settings,
    ocr_provider: OCRProvider | None = None,
    summary_service: SummaryService | None = None,
    store: JobStore | None = None,
) -> None:
    store = store or default_job_store
    ocr_provider = ocr_provider or get_default_ocr_provider(settings)
    summary_service = summary_service or SummaryService(get_ai_provider(settings))
    started_at = time.monotonic()

    try:
        store.set_stage(job_id, JobStage.VALIDATING)
        store.set_stage(job_id, JobStage.EXTRACTING)

        page_texts, used_ocr = extract_document_text(
            content,
            extension,
            ocr_provider,
            settings,
            on_stage=lambda stage: store.set_stage(job_id, stage),
        )

        store.set_stage(job_id, JobStage.CLEANING)
        cleaned_text = clean_pages(page_texts)

        if not cleaned_text.strip():
            raise EmptyTextError(
                "We couldn't extract readable text from this document. "
                "Please try a clearer image or a higher-quality scanned PDF."
            )

        store.set_extraction_result(
            job_id,
            cleaned_text=cleaned_text,
            file_type=extension.lstrip("."),
            page_count=len(page_texts) if extension == ".pdf" else None,
            word_count=len(cleaned_text.split()),
            used_ocr=used_ocr,
        )

        store.set_stage(job_id, JobStage.SUMMARIZING)
        analysis = summary_service.generate_analysis(cleaned_text, summary_length)

        job = store.get(job_id)
        filename = job.filename if job else "document"
        word_count = job.word_count if job else len(cleaned_text.split())
        page_count = job.page_count if job else None

        result = AnalyzeResult(
            metadata=DocumentMetadata(
                filename=filename,
                file_type=extension.lstrip("."),
                page_count=page_count,
                word_count=word_count or 0,
                used_ocr=used_ocr,
                processing_duration_ms=int((time.monotonic() - started_at) * 1000),
            ),
            summary=analysis.summary,
            summary_length=summary_length,
            key_points=analysis.key_points,
            main_ideas=analysis.main_ideas,
            improvement_suggestions=analysis.improvement_suggestions,
            ai_provider=summary_service.provider.name,
        )
        store.complete(job_id, result, cleaned_text)
    except AppError as exc:
        logger.warning("Document processing failed for job %s: %s", job_id, exc.message)
        store.fail(job_id, ErrorPayload(error=exc.error, message=exc.message))
    except Exception:
        logger.exception("Unexpected error processing job %s", job_id)
        store.fail(
            job_id,
            ErrorPayload(
                error="internal_error",
                message="Something went wrong while processing your document. Please try again.",
            ),
        )
