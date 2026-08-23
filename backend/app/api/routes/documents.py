from fastapi import APIRouter, Depends, Form, Request, UploadFile
from starlette.concurrency import run_in_threadpool

from app.config.settings import Settings, get_settings
from app.models.schemas import (
    AnalyzeAcceptedResponse,
    AskQuestionRequest,
    AskQuestionResponse,
    CompareAskRequest,
    CompareRequest,
    CompareResponse,
    JobStatusResponse,
    SummarizeRequest,
    SummarizeResponse,
    SummaryLength,
)
from app.services.job_store import job_store
from app.services.pipeline import run_analysis_pipeline
from app.services.summary_service import SummaryService, get_ai_provider
from app.utils.background_tasks import schedule_background_task
from app.utils.errors import FileTooLargeError, NotFoundError, ProcessingError, ValidationError
from app.utils.filenames import sanitize_display_filename
from app.utils.validation import validate_upload

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_QUESTION_LENGTH = 2000
MIN_COMPARE_DOCUMENTS = 2
MAX_COMPARE_DOCUMENTS = 5


@router.post("/analyze", status_code=202, response_model=AnalyzeAcceptedResponse)
async def analyze_document(
    request: Request,
    file: UploadFile,
    summary_length: SummaryLength = Form(default=SummaryLength.MEDIUM),
    settings: Settings = Depends(get_settings),
) -> AnalyzeAcceptedResponse:
    # Reject oversized uploads via the declared Content-Length before buffering
    # the body into memory. (Multipart overhead means this is an upper bound,
    # not exact - the post-read size check below is the authoritative one.)
    content_length = request.headers.get("content-length")
    if content_length is not None and int(content_length) > settings.max_file_size * 2:
        max_mb = settings.max_file_size / (1024 * 1024)
        raise FileTooLargeError(f"This file is larger than the {max_mb:.0f} MB limit.")

    content = await file.read()
    extension = validate_upload(filename=file.filename or "", content=content, settings=settings)

    display_name = sanitize_display_filename(file.filename or "document")
    job = job_store.create(filename=display_name)

    schedule_background_task(
        run_in_threadpool(
            run_analysis_pipeline, job.id, content, extension, summary_length, settings
        )
    )

    return AnalyzeAcceptedResponse(job_id=job.id, status=job.status)


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    job = job_store.get(job_id)
    if job is None:
        raise NotFoundError("We couldn't find that document analysis job.")

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        stage=job.stage,
        filename=job.filename,
        created_at=job.created_at,
        result=job.result,
        error=job.error,
    )


@router.post("/summarize", response_model=SummarizeResponse)
async def regenerate_summary(
    request: SummarizeRequest,
    settings: Settings = Depends(get_settings),
) -> SummarizeResponse:
    job = job_store.get(request.job_id)
    if job is None:
        raise NotFoundError("We couldn't find that document analysis job.")
    if job.cleaned_text is None:
        raise ProcessingError("This document hasn't finished processing yet.")

    summary_service = SummaryService(get_ai_provider(settings))
    summary = await run_in_threadpool(
        summary_service.regenerate_summary, job.cleaned_text, request.summary_length
    )

    return SummarizeResponse(summary=summary, summary_length=request.summary_length)


@router.post("/ask", response_model=AskQuestionResponse)
async def ask_question(
    request: AskQuestionRequest,
    settings: Settings = Depends(get_settings),
) -> AskQuestionResponse:
    question = request.question.strip()
    if not question:
        raise ValidationError("Please enter a question.")
    if len(question) > MAX_QUESTION_LENGTH:
        raise ValidationError(f"Questions are limited to {MAX_QUESTION_LENGTH} characters.")

    job = job_store.get(request.job_id)
    if job is None:
        raise NotFoundError("We couldn't find that document analysis job.")
    if job.cleaned_text is None:
        raise ProcessingError("This document hasn't finished processing yet.")

    summary_service = SummaryService(get_ai_provider(settings))
    answer = await run_in_threadpool(
        summary_service.answer_question, job.cleaned_text, question, job.qa_history
    )
    job_store.append_qa_exchange(job.id, question, answer)

    return AskQuestionResponse(answer=answer, ai_provider=summary_service.provider.name)


@router.post("/compare", response_model=CompareResponse)
async def compare_documents(
    request: CompareRequest,
    settings: Settings = Depends(get_settings),
) -> CompareResponse:
    if len(request.job_ids) < MIN_COMPARE_DOCUMENTS:
        raise ValidationError("Select at least two documents to compare.")
    if len(request.job_ids) > MAX_COMPARE_DOCUMENTS:
        raise ValidationError(f"You can compare up to {MAX_COMPARE_DOCUMENTS} documents at a time.")

    jobs = []
    for job_id in request.job_ids:
        job = job_store.get(job_id)
        if job is None:
            raise NotFoundError("We couldn't find one of the selected documents.")
        if job.cleaned_text is None:
            raise ProcessingError(f"'{job.filename}' hasn't finished processing yet.")
        jobs.append(job)

    summary_service = SummaryService(get_ai_provider(settings))
    comparison = await run_in_threadpool(
        summary_service.compare_documents,
        [(job.filename, job.cleaned_text) for job in jobs],
    )

    return CompareResponse(
        documents=[job.filename for job in jobs],
        comparison_summary=comparison.comparison_summary,
        similarities=comparison.similarities,
        differences=comparison.differences,
        ai_provider=summary_service.provider.name,
    )


@router.post("/compare/ask", response_model=AskQuestionResponse)
async def ask_compare_question(
    request: CompareAskRequest,
    settings: Settings = Depends(get_settings),
) -> AskQuestionResponse:
    question = request.question.strip()
    if not question:
        raise ValidationError("Please enter a question.")
    if len(question) > MAX_QUESTION_LENGTH:
        raise ValidationError(f"Questions are limited to {MAX_QUESTION_LENGTH} characters.")
    if not request.job_ids or len(request.job_ids) < MIN_COMPARE_DOCUMENTS:
        raise ValidationError("Select at least two documents to ask a question across.")

    jobs = []
    for job_id in request.job_ids:
        job = job_store.get(job_id)
        if job is None:
            raise NotFoundError("We couldn't find one of the selected documents.")
        if job.cleaned_text is None:
            raise ProcessingError(f"'{job.filename}' hasn't finished processing yet.")
        jobs.append(job)

    combined_sections = [
        f"--- Document: {job.filename} ---\n{job.cleaned_text}"
        for job in jobs
    ]
    combined_text = "\n\n".join(combined_sections)

    summary_service = SummaryService(get_ai_provider(settings))
    answer = await run_in_threadpool(
        summary_service.answer_question, combined_text, question, None
    )

    return AskQuestionResponse(answer=answer, ai_provider=summary_service.provider.name)
