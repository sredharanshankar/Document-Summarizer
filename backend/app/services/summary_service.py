"""SummaryService: the single entry point the rest of the app uses for AI
analysis. It owns provider selection (Groq vs the no-API-key fallback) and
chunking for long documents, so callers never talk to an AIProvider or
worry about document length directly.

    AI Provider (Groq / Fallback)
        v
    SummaryService  <-- chunking lives here
        v
    Application (pipeline.py)
"""

from __future__ import annotations

from app.config.settings import Settings
from app.models.schemas import SummaryLength
from app.services.ai.base import AIProvider, QAHistory, StructuredAnalysis, StructuredComparison
from app.services.ai.fallback_provider import FallbackProvider
from app.services.ai.groq_provider import GroqProvider

# Rough estimate (English averages ~4 chars/token) - deliberately simple
# rather than a model-specific tokenizer, since it only needs to be good
# enough to decide "does this need chunking", not exact.
CHARS_PER_TOKEN_ESTIMATE = 4
# Documents under this estimated token count are summarized directly.
DIRECT_TOKEN_THRESHOLD = 6000
# Per-chunk input budget when a document does need chunking.
CHUNK_TOKEN_BUDGET = 4000


def get_ai_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "groq" and settings.ai_api_key:
        return GroqProvider(
            api_key=settings.ai_api_key,
            model=settings.ai_model,
            timeout_seconds=settings.ai_request_timeout_seconds,
        )
    return FallbackProvider()


class SummaryService:
    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    def generate_analysis(self, text: str, summary_length: SummaryLength) -> StructuredAnalysis:
        source = self._condense_if_needed(text)
        return self.provider.generate_analysis(source, summary_length)

    def regenerate_summary(self, text: str, summary_length: SummaryLength) -> str:
        source = self._condense_if_needed(text)
        return self.provider.generate_summary(source, summary_length)

    def answer_question(self, text: str, question: str, history: QAHistory | None = None) -> str:
        # Same condensing as summarization: keeps very long documents within
        # the model's context. A known trade-off - an answer that hinges on
        # a detail lost during chunk-summarization could be missed. See the
        # README's Limitations section.
        source = self._condense_if_needed(text)
        return self.provider.answer_question(source, question, history)

    def compare_documents(self, documents: list[tuple[str, str]]) -> StructuredComparison:
        condensed = [(name, self._condense_if_needed(text)) for name, text in documents]
        return self.provider.compare_documents(condensed)

    def _condense_if_needed(self, text: str) -> str:
        if _estimate_tokens(text) <= DIRECT_TOKEN_THRESHOLD:
            return text

        chunks = _split_into_chunks(text, CHUNK_TOKEN_BUDGET)
        chunk_summaries = [
            self.provider.generate_summary(chunk, SummaryLength.MEDIUM) for chunk in chunks
        ]
        return "\n\n".join(chunk_summaries)


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN_ESTIMATE)


def _split_into_chunks(text: str, token_budget: int) -> list[str]:
    char_budget = token_budget * CHARS_PER_TOKEN_ESTIMATE
    paragraphs = text.split("\n\n")

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for paragraph in paragraphs:
        if current and current_len + len(paragraph) > char_budget:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(paragraph)
        current_len += len(paragraph)

    if current:
        chunks.append("\n\n".join(current))

    return chunks
