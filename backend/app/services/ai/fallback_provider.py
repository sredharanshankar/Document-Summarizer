"""Rule-based extractive summarizer used when no AI provider is configured
(or the app is asked to demo the pipeline without an API key).

Nothing here is hardcoded output - every field is computed from the
specific document's own text (word-frequency sentence scoring for the
summary/key points/main ideas, and measurable document properties for the
improvement suggestions), so it degrades gracefully rather than faking
results. Quality is naturally lower than an LLM's, which is expected and
documented in the README.
"""

from __future__ import annotations

from collections import Counter

from app.models.schemas import SummaryLength
from app.services.ai.base import AIProvider, QAHistory, StructuredAnalysis, StructuredComparison
from app.services.ai.text_analysis import (
    score_sentences,
    score_sentences_by_query,
    split_paragraphs,
    split_sentences,
    top_keywords,
    word_frequencies,
)

_SUMMARY_SENTENCE_TARGETS = {
    SummaryLength.SHORT: 2,
    SummaryLength.MEDIUM: 5,
    SummaryLength.LONG: 10,
}
_KEY_POINT_COUNT = 5
_MAIN_IDEA_COUNT = 4
_ANSWER_SENTENCE_COUNT = 3
_COMPARISON_TOP_KEYWORDS = 15
_MAX_COMPARISON_ITEMS = 5
_CONCLUSION_MARKERS = (
    "in conclusion",
    "to conclude",
    "to summarize",
    "in summary",
    "overall,",
    "in closing",
)


class FallbackProvider(AIProvider):
    name = "fallback"

    def generate_summary(self, text: str, summary_length: SummaryLength) -> str:
        sentences = split_sentences(text)
        if not sentences:
            return ""
        frequencies = word_frequencies(text)
        scores = score_sentences(sentences, frequencies)
        n = _summary_sentence_count(summary_length, len(sentences))
        top = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)[:n]
        return " ".join(sentences[i] for i in sorted(top))

    def generate_analysis(self, text: str, summary_length: SummaryLength) -> StructuredAnalysis:
        sentences = split_sentences(text)
        paragraphs = split_paragraphs(text)
        frequencies = word_frequencies(text)

        if not sentences:
            return StructuredAnalysis(summary="", key_points=[], main_ideas=[], improvement_suggestions=[])

        scores = score_sentences(sentences, frequencies)
        ranked = sorted(range(len(sentences)), key=lambda i: scores[i], reverse=True)

        summary_n = _summary_sentence_count(summary_length, len(sentences))
        summary_indices = set(ranked[:summary_n])
        summary = " ".join(sentences[i] for i in sorted(summary_indices))

        key_point_indices = [i for i in ranked if i not in summary_indices][:_KEY_POINT_COUNT]
        key_points = [sentences[i] for i in key_point_indices]

        main_ideas = _rank_paragraph_ideas(paragraphs, frequencies)[:_MAIN_IDEA_COUNT]

        return StructuredAnalysis(
            summary=summary,
            key_points=key_points,
            main_ideas=main_ideas,
            improvement_suggestions=_generate_suggestions(text, sentences, paragraphs),
        )

    def answer_question(self, text: str, question: str, history: QAHistory | None = None) -> str:
        sentences = split_sentences(text)
        if not sentences:
            return "There's no document text to search for an answer."

        scores = score_sentences_by_query(sentences, question)

        # A short follow-up ("what about the remote policy?") often carries
        # too few keywords of its own to match anything on pure keyword
        # overlap. This has no real understanding of what "that" refers to -
        # it's a simple, honest broadening: if the question alone matches
        # nothing, retry including the previous question's keywords too,
        # since that's usually what a bare follow-up is continuing from.
        if history and not any(score > 0 for score in scores):
            previous_question = history[-1][0]
            scores = score_sentences_by_query(sentences, f"{question} {previous_question}")

        relevant = sorted(
            (i for i in range(len(sentences)) if scores[i] > 0),
            key=lambda i: scores[i],
            reverse=True,
        )[:_ANSWER_SENTENCE_COUNT]

        if not relevant:
            return "The document doesn't seem to mention that."

        return " ".join(sentences[i] for i in sorted(relevant))

    def compare_documents(self, documents: list[tuple[str, str]]) -> StructuredComparison:
        # Keep these as frequency-ordered lists, not sets: a set forgets
        # which words were most emphasized, so a later `sorted()` would
        # rank purely alphabetically ("across" before "renewable") instead
        # of by how much each document actually emphasizes the term.
        keyword_lists = [top_keywords(word_frequencies(text), _COMPARISON_TOP_KEYWORDS) for _, text in documents]
        keyword_sets = [set(kw) for kw in keyword_lists]
        word_counts = [len(text.split()) for _, text in documents]

        shared = set.intersection(*keyword_sets) if keyword_sets else set()
        ordered_shared = [word for word in keyword_lists[0] if word in shared] if keyword_lists else []
        similarities = [f'All documents reference "{word}".' for word in ordered_shared[:_MAX_COMPARISON_ITEMS]]
        if not similarities:
            similarities = [
                "No strongly shared themes were detected across the documents' most frequent terms."
            ]

        differences = []
        for i, (name, _) in enumerate(documents):
            # Index-based, not name-based: two uploaded files can share a
            # filename, which would silently corrupt a name-keyed comparison.
            others: set[str] = set()
            for j, keywords in enumerate(keyword_sets):
                if j != i:
                    others |= keywords
            unique = [word for word in keyword_lists[i] if word not in others][:_MAX_COMPARISON_ITEMS]
            if unique:
                differences.append(f'"{name}" uniquely emphasizes: {", ".join(unique)}.')
        if not differences:
            differences = ["No strongly distinguishing terms were detected between the documents."]

        word_count_summary = ", ".join(
            f'"{name}" ({count} words)' for (name, _), count in zip(documents, word_counts)
        )
        comparison_summary = f"Compared {len(documents)} documents: {word_count_summary}."

        return StructuredComparison(
            comparison_summary=comparison_summary,
            similarities=similarities,
            differences=differences,
        )


def _summary_sentence_count(length: SummaryLength, total_sentences: int) -> int:
    return max(1, min(_SUMMARY_SENTENCE_TARGETS[length], total_sentences))


def _rank_paragraph_ideas(paragraphs: list[str], frequencies: Counter[str]) -> list[str]:
    ranked: list[tuple[float, str]] = []
    for paragraph in paragraphs:
        sentences = split_sentences(paragraph)
        if not sentences:
            continue
        scores = score_sentences(sentences, frequencies)
        best_index = max(range(len(sentences)), key=lambda i: scores[i])
        ranked.append((sum(scores), sentences[best_index]))

    ranked.sort(key=lambda pair: pair[0], reverse=True)
    return [sentence for _, sentence in ranked]


def _generate_suggestions(text: str, sentences: list[str], paragraphs: list[str]) -> list[str]:
    suggestions: list[str] = []
    word_count = len(text.split())
    lower_text = text.lower()

    if word_count < 120:
        suggestions.append(
            "This document is quite short. Consider adding more supporting detail, "
            "context, or examples to strengthen it."
        )

    if word_count >= 300 and not any(marker in lower_text for marker in _CONCLUSION_MARKERS):
        suggestions.append(
            "No clear concluding section was detected. Consider adding a concise "
            "conclusion that summarizes the key outcomes."
        )

    if len(paragraphs) >= 4:
        single_sentence_paragraphs = sum(1 for p in paragraphs if len(split_sentences(p)) == 1)
        if single_sentence_paragraphs / len(paragraphs) > 0.6:
            suggestions.append(
                "Several sections consist of only a single sentence. Expanding them "
                "with more explanation could improve clarity."
            )

    repeated = Counter(s.lower().strip() for s in sentences if len(s.split()) > 4)
    if any(count > 1 for count in repeated.values()):
        suggestions.append(
            "The document repeats some information more than once. Consolidating "
            "repeated points could improve readability."
        )

    if len(sentences) >= 6:
        average_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if average_sentence_length > 32:
            suggestions.append(
                "Many sentences are quite long and complex. Breaking them into "
                "shorter sentences could make the document easier to read."
            )

    return suggestions
