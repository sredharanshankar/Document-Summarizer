from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SummaryLength(StrEnum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class JobStage(StrEnum):
    QUEUED = "queued"
    VALIDATING = "validating"
    EXTRACTING = "extracting"
    OCR = "ocr"
    CLEANING = "cleaning"
    SUMMARIZING = "summarizing"
    DONE = "done"


class JobStatus(StrEnum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    page_count: int | None = None
    word_count: int
    used_ocr: bool
    processing_duration_ms: int


class AnalyzeResult(BaseModel):
    metadata: DocumentMetadata
    summary: str
    summary_length: SummaryLength
    key_points: list[str]
    main_ideas: list[str]
    improvement_suggestions: list[str]
    ai_provider: str


class ErrorPayload(BaseModel):
    error: str
    message: str


class AnalyzeAcceptedResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    stage: JobStage
    filename: str
    created_at: datetime
    result: AnalyzeResult | None = None
    error: ErrorPayload | None = None


class SummarizeRequest(BaseModel):
    job_id: str
    summary_length: SummaryLength = Field(default=SummaryLength.MEDIUM)


class SummarizeResponse(BaseModel):
    summary: str
    summary_length: SummaryLength


class AskQuestionRequest(BaseModel):
    job_id: str
    question: str


class AskQuestionResponse(BaseModel):
    answer: str
    ai_provider: str


class CompareRequest(BaseModel):
    job_ids: list[str]


class CompareResponse(BaseModel):
    documents: list[str]
    comparison_summary: str
    similarities: list[str]
    differences: list[str]
    ai_provider: str


class CompareAskRequest(BaseModel):
    job_ids: list[str]
    question: str
