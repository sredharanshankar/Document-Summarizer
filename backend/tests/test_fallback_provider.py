from app.models.schemas import SummaryLength
from app.services.ai.fallback_provider import FallbackProvider

SHORT_DOC = "This document is very short."

WELL_FORMED_DOC = "\n\n".join(
    [
        "Renewable energy adoption has accelerated across the globe over the past decade. "
        "Solar and wind capacity have both grown at double-digit rates annually, driven by "
        "falling equipment costs and supportive government policy.",
        "Grid integration remains a significant technical challenge. Utilities must manage "
        "variable generation while maintaining reliability, which has driven investment in "
        "battery storage and demand-response programs across many regions.",
        "Financing structures have also evolved considerably. Power purchase agreements now "
        "allow developers to secure long-term revenue certainty, which has unlocked "
        "institutional capital that was previously unavailable to the sector.",
        "In conclusion, renewable energy has moved from a niche technology to a mainstream "
        "part of the global energy mix, though grid and financing challenges remain active "
        "areas of development.",
    ]
)

REPETITIVE_DOC = "\n\n".join(
    [
        "The quarterly results exceeded expectations across every business unit this year. "
        "The quarterly results exceeded expectations across every business unit this year.",
        "Revenue growth was particularly strong in the enterprise segment during the quarter.",
    ]
)


def test_generate_summary_short_is_shorter_than_long() -> None:
    provider = FallbackProvider()
    short = provider.generate_summary(WELL_FORMED_DOC, SummaryLength.SHORT)
    long = provider.generate_summary(WELL_FORMED_DOC, SummaryLength.LONG)

    assert len(short) < len(long)
    assert short != ""


def test_generate_summary_empty_text_returns_empty_string() -> None:
    provider = FallbackProvider()
    assert provider.generate_summary("", SummaryLength.MEDIUM) == ""


def test_generate_analysis_returns_grounded_content() -> None:
    provider = FallbackProvider()
    result = provider.generate_analysis(WELL_FORMED_DOC, SummaryLength.MEDIUM)

    assert result.summary
    assert len(result.key_points) > 0
    assert len(result.main_ideas) > 0
    # Every key point / main idea is a literal sentence lifted from the source
    # document - the core "no fake functionality" guarantee for this fallback
    # path (nothing here is generated text, only extracted text).
    for sentence in [*result.key_points, *result.main_ideas]:
        assert sentence.strip() in WELL_FORMED_DOC


def test_short_document_triggers_length_suggestion() -> None:
    provider = FallbackProvider()
    result = provider.generate_analysis(SHORT_DOC, SummaryLength.SHORT)

    assert any("short" in s.lower() for s in result.improvement_suggestions)


def test_well_formed_document_with_conclusion_does_not_flag_missing_conclusion() -> None:
    provider = FallbackProvider()
    result = provider.generate_analysis(WELL_FORMED_DOC, SummaryLength.MEDIUM)

    assert not any("conclu" in s.lower() for s in result.improvement_suggestions)


def test_repeated_sentences_trigger_repetition_suggestion() -> None:
    provider = FallbackProvider()
    result = provider.generate_analysis(REPETITIVE_DOC, SummaryLength.SHORT)

    assert any("repeat" in s.lower() for s in result.improvement_suggestions)


def test_empty_text_returns_empty_analysis_without_crashing() -> None:
    provider = FallbackProvider()
    result = provider.generate_analysis("", SummaryLength.MEDIUM)

    assert result.summary == ""
    assert result.key_points == []
    assert result.main_ideas == []
    assert result.improvement_suggestions == []


def test_answer_question_returns_grounded_sentence_for_relevant_question() -> None:
    provider = FallbackProvider()
    answer = provider.answer_question(WELL_FORMED_DOC, "What is happening with financing?")

    assert "financing" in answer.lower() or "capital" in answer.lower()
    # Extractive, not generative - the answer must be lifted verbatim.
    assert any(sentence.strip() in WELL_FORMED_DOC for sentence in answer.split(". "))


def test_answer_question_is_honest_when_nothing_matches() -> None:
    provider = FallbackProvider()
    # Deliberately zero keyword overlap with WELL_FORMED_DOC's vocabulary -
    # the fallback provider matches on literal keyword overlap, so a
    # semantically-unrelated-but-word-overlapping question (e.g. one using
    # "capital" when the document says "institutional capital") isn't a
    # reliable way to test the "no match" path.
    answer = provider.answer_question(WELL_FORMED_DOC, "What is your favorite pizza topping?")

    assert "doesn't seem to mention" in answer.lower() or "doesn't mention" in answer.lower()


def test_answer_question_on_empty_document_does_not_crash() -> None:
    provider = FallbackProvider()
    answer = provider.answer_question("", "Anything?")
    assert answer


def test_answer_question_uses_previous_question_for_a_sparse_followup() -> None:
    provider = FallbackProvider()
    # "What about that?" carries no real keywords of its own ("what",
    # "about", "that" are all stopwords) - on its own it can't match
    # anything. With the previous question in history, it should be able to
    # find the financing-related sentence that a bare-keyword match couldn't.
    history = [("What is happening with financing?", "(some prior answer)")]

    answer = provider.answer_question(WELL_FORMED_DOC, "What about that?", history)

    assert "doesn't seem to mention" not in answer.lower()
    assert "financ" in answer.lower() or "capital" in answer.lower()


def test_answer_question_sparse_followup_without_history_is_still_honest() -> None:
    provider = FallbackProvider()
    answer = provider.answer_question(WELL_FORMED_DOC, "What about that?")
    assert "doesn't seem to mention" in answer.lower()


COMPARISON_DOC_A = (
    "Investment discussions dominated this quarter. Renewable renewable renewable "
    "energy energy projects continue to expand. Investment planning requires "
    "careful investment analysis of the investment portfolio."
)

COMPARISON_DOC_B = (
    "Investment committee approved the office relocation relocation relocation "
    "budget. Investment terms for the new lease office office were finalized "
    "after months of negotiation."
)


def test_compare_documents_finds_a_shared_keyword() -> None:
    provider = FallbackProvider()
    result = provider.compare_documents(
        [("doc_a.pdf", COMPARISON_DOC_A), ("doc_b.pdf", COMPARISON_DOC_B)]
    )

    assert any("investment" in s.lower() for s in result.similarities)


def test_compare_documents_finds_unique_terms_per_document() -> None:
    provider = FallbackProvider()
    result = provider.compare_documents(
        [("doc_a.pdf", COMPARISON_DOC_A), ("doc_b.pdf", COMPARISON_DOC_B)]
    )

    doc_a_diff = next((d for d in result.differences if "doc_a.pdf" in d), None)
    doc_b_diff = next((d for d in result.differences if "doc_b.pdf" in d), None)
    assert doc_a_diff is not None
    assert doc_b_diff is not None
    assert "renewable" in doc_a_diff.lower() or "portfolio" in doc_a_diff.lower()
    assert "relocation" in doc_b_diff.lower() or "office" in doc_b_diff.lower()


def test_compare_documents_summary_names_both_documents() -> None:
    provider = FallbackProvider()
    result = provider.compare_documents(
        [("doc_a.pdf", COMPARISON_DOC_A), ("doc_b.pdf", COMPARISON_DOC_B)]
    )

    assert "doc_a.pdf" in result.comparison_summary
    assert "doc_b.pdf" in result.comparison_summary


def test_compare_documents_uses_index_not_name_for_duplicate_filenames() -> None:
    provider = FallbackProvider()
    # Two uploads can share a filename - this must not crash or silently
    # merge the two documents' keyword sets together.
    result = provider.compare_documents(
        [("report.pdf", COMPARISON_DOC_A), ("report.pdf", COMPARISON_DOC_B)]
    )

    assert len(result.differences) <= 2
    assert result.comparison_summary
