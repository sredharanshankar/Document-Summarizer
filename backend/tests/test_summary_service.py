from app.config.settings import Settings
from app.models.schemas import SummaryLength
from app.services.ai.fallback_provider import FallbackProvider
from app.services.ai.groq_provider import GroqProvider
from app.services.summary_service import (
    CHARS_PER_TOKEN_ESTIMATE,
    DIRECT_TOKEN_THRESHOLD,
    SummaryService,
    _split_into_chunks,
    get_ai_provider,
)
from tests.helpers import FakeAIProvider


def test_get_ai_provider_uses_fallback_when_no_api_key() -> None:
    settings = Settings(ai_api_key="", ai_provider="groq")
    assert isinstance(get_ai_provider(settings), FallbackProvider)


def test_get_ai_provider_uses_groq_when_key_present() -> None:
    settings = Settings(ai_api_key="test-key", ai_provider="groq")
    assert isinstance(get_ai_provider(settings), GroqProvider)


def test_get_ai_provider_respects_explicit_fallback_choice() -> None:
    settings = Settings(ai_api_key="test-key", ai_provider="fallback")
    assert isinstance(get_ai_provider(settings), FallbackProvider)


def test_short_document_is_summarized_directly_without_chunking() -> None:
    fake = FakeAIProvider()
    service = SummaryService(fake)

    service.generate_analysis("Short document text.", SummaryLength.MEDIUM)

    assert len(fake.analysis_calls) == 1
    assert fake.summary_calls == []  # no chunk summaries needed
    assert fake.analysis_calls[0] == "Short document text."


def test_long_document_is_chunked_before_analysis() -> None:
    fake = FakeAIProvider()
    service = SummaryService(fake)

    # Build a document comfortably over DIRECT_TOKEN_THRESHOLD tokens.
    paragraph = "This paragraph discusses renewable energy policy in some detail. " * 20
    long_text = "\n\n".join([paragraph] * 20)
    assert len(long_text) // CHARS_PER_TOKEN_ESTIMATE > DIRECT_TOKEN_THRESHOLD

    service.generate_analysis(long_text, SummaryLength.LONG)

    assert len(fake.summary_calls) > 1  # multiple chunks were summarized
    assert len(fake.analysis_calls) == 1  # exactly one final pass over the condensed text
    # The condensed text handed to the final analysis call should be much
    # shorter than the original document.
    assert len(fake.analysis_calls[0]) < len(long_text)


def test_regenerate_summary_short_document_calls_provider_directly() -> None:
    fake = FakeAIProvider()
    service = SummaryService(fake)

    summary = service.regenerate_summary("Some text.", SummaryLength.SHORT)

    assert summary == "fake chunk summary of 10 chars"
    assert fake.summary_calls == ["Some text."]


def test_answer_question_short_document_calls_provider_directly() -> None:
    fake = FakeAIProvider()
    service = SummaryService(fake)

    answer = service.answer_question("Some text.", "What does it say?")

    assert answer == "fake answer to: What does it say?"
    assert fake.question_calls == [("Some text.", "What does it say?", None)]


def test_answer_question_condenses_long_documents_first() -> None:
    fake = FakeAIProvider()
    service = SummaryService(fake)

    paragraph = "This paragraph discusses renewable energy policy in some detail. " * 20
    long_text = "\n\n".join([paragraph] * 20)
    assert len(long_text) // CHARS_PER_TOKEN_ESTIMATE > DIRECT_TOKEN_THRESHOLD

    service.answer_question(long_text, "What does it say about policy?")

    assert len(fake.summary_calls) > 1  # chunked first, same as generate_analysis
    condensed_text, question, history = fake.question_calls[0]
    assert question == "What does it say about policy?"
    assert len(condensed_text) < len(long_text)
    assert history is None


def test_answer_question_passes_history_through_to_the_provider() -> None:
    fake = FakeAIProvider()
    service = SummaryService(fake)
    history = [("First question?", "First answer.")]

    service.answer_question("Some text.", "Follow-up question?", history)

    assert fake.question_calls == [("Some text.", "Follow-up question?", history)]


def test_compare_documents_condenses_each_document_and_delegates() -> None:
    fake = FakeAIProvider()
    service = SummaryService(fake)

    result = service.compare_documents([("a.pdf", "Short text a."), ("b.pdf", "Short text b.")])

    assert len(fake.comparison_calls) == 1
    names = [name for name, _ in fake.comparison_calls[0]]
    assert names == ["a.pdf", "b.pdf"]
    assert result.comparison_summary == "fake comparison of: a.pdf, b.pdf"


def test_compare_documents_condenses_a_long_document_before_comparing() -> None:
    fake = FakeAIProvider()
    service = SummaryService(fake)

    paragraph = "This paragraph discusses renewable energy policy in some detail. " * 20
    long_text = "\n\n".join([paragraph] * 20)
    assert len(long_text) // CHARS_PER_TOKEN_ESTIMATE > DIRECT_TOKEN_THRESHOLD

    service.compare_documents([("long.pdf", long_text), ("short.pdf", "Short text.")])

    assert len(fake.summary_calls) > 1  # the long document was chunked first
    compared = fake.comparison_calls[0]
    long_doc_text = next(text for name, text in compared if name == "long.pdf")
    assert len(long_doc_text) < len(long_text)


def test_split_into_chunks_respects_budget_and_keeps_paragraphs_intact() -> None:
    paragraphs = [f"Paragraph number {i} with some filler words in it." for i in range(30)]
    text = "\n\n".join(paragraphs)

    chunks = _split_into_chunks(text, token_budget=50)  # small budget forces multiple chunks

    assert len(chunks) > 1
    # Every original paragraph should appear intact in exactly one chunk.
    rejoined = "\n\n".join(chunks)
    for paragraph in paragraphs:
        assert paragraph in rejoined


def test_split_into_chunks_single_chunk_when_under_budget() -> None:
    text = "One paragraph.\n\nAnother paragraph."
    chunks = _split_into_chunks(text, token_budget=1000)
    assert chunks == [text]
