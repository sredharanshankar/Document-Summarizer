import pytest

from app.config.settings import Settings
from app.models.schemas import JobStatus, SummaryLength
from app.services.ai.base import AIProvider, StructuredAnalysis
from app.services.job_store import JobStore
from app.services.pipeline import run_analysis_pipeline
from app.services.summary_service import SummaryService
from app.utils.errors import AIProviderError
from tests.helpers import FakeAIProvider, FakeOCRProvider, blank_pdf_bytes


@pytest.fixture
def settings() -> Settings:
    return Settings(ai_api_key="", ocr_enabled=True)


def test_pipeline_completes_job_with_full_result(
    settings: Settings, sample_pdf_bytes: bytes
) -> None:
    store = JobStore()
    job = store.create(filename="report.pdf")
    fake_ai = FakeAIProvider()

    run_analysis_pipeline(
        job.id,
        sample_pdf_bytes,
        ".pdf",
        summary_length=SummaryLength.MEDIUM,
        settings=settings,
        ocr_provider=FakeOCRProvider(),
        summary_service=SummaryService(fake_ai),
        store=store,
    )

    updated = store.get(job.id)
    assert updated is not None
    assert updated.status == JobStatus.COMPLETED
    assert updated.result is not None
    assert updated.result.summary == "fake summary (medium)"
    assert updated.result.key_points == ["fake key point"]
    assert updated.result.metadata.filename == "report.pdf"
    assert updated.result.metadata.used_ocr is False
    assert updated.result.ai_provider == "fake"
    assert fake_ai.analysis_calls  # the cleaned document text reached the AI provider


def test_pipeline_fails_job_on_empty_extracted_text(settings: Settings) -> None:
    store = JobStore()
    job = store.create(filename="blank.pdf")
    fake_ai = FakeAIProvider()

    run_analysis_pipeline(
        job.id,
        blank_pdf_bytes(1),
        ".pdf",
        summary_length=SummaryLength.MEDIUM,
        settings=settings,
        ocr_provider=FakeOCRProvider(text="   "),
        summary_service=SummaryService(fake_ai),
        store=store,
    )

    updated = store.get(job.id)
    assert updated is not None
    assert updated.status == JobStatus.FAILED
    assert updated.error is not None
    assert updated.error.error == "empty_text"
    assert not fake_ai.analysis_calls  # never reached summarization


def test_pipeline_fails_job_cleanly_when_ai_provider_raises(
    settings: Settings, sample_pdf_bytes: bytes
) -> None:
    class BrokenAIProvider(AIProvider):
        name = "broken"

        def generate_analysis(self, text: str, summary_length: SummaryLength) -> StructuredAnalysis:
            raise AIProviderError("The AI service could not process this document right now.")

        def generate_summary(self, text: str, summary_length: SummaryLength) -> str:
            raise AIProviderError("boom")

        def answer_question(self, text: str, question: str, history=None) -> str:
            raise AIProviderError("boom")

        def compare_documents(self, documents):
            raise AIProviderError("boom")

    store = JobStore()
    job = store.create(filename="report.pdf")

    run_analysis_pipeline(
        job.id,
        sample_pdf_bytes,
        ".pdf",
        summary_length=SummaryLength.MEDIUM,
        settings=settings,
        ocr_provider=FakeOCRProvider(),
        summary_service=SummaryService(BrokenAIProvider()),
        store=store,
    )

    updated = store.get(job.id)
    assert updated is not None
    assert updated.status == JobStatus.FAILED
    assert updated.error is not None
    assert updated.error.error == "ai_provider_error"
    # Extraction result should still have been recorded before the AI step failed.
    assert updated.cleaned_text is not None
