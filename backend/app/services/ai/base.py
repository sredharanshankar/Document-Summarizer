from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.schemas import SummaryLength

# (question, answer) pairs, oldest first - prior Q&A turns for a job, so a
# follow-up question ("what about the remote policy?") can be answered in
# context instead of independently each time.
QAHistory = list[tuple[str, str]]


@dataclass
class StructuredAnalysis:
    summary: str
    key_points: list[str]
    main_ideas: list[str]
    improvement_suggestions: list[str]


@dataclass
class StructuredComparison:
    comparison_summary: str
    similarities: list[str]
    differences: list[str]


class AIProvider(ABC):
    """Abstraction over a summarization backend.

    SummaryService depends only on this interface, so the app isn't
    tightly coupled to one AI vendor - GroqProvider can be swapped for
    another hosted LLM, and FallbackProvider (no external API at all) lets
    the whole pipeline run without any API key configured.
    """

    name: str

    @abstractmethod
    def generate_analysis(self, text: str, summary_length: SummaryLength) -> StructuredAnalysis:
        """Full analysis: summary, key points, main ideas, improvement suggestions."""

    @abstractmethod
    def generate_summary(self, text: str, summary_length: SummaryLength) -> str:
        """Just the summary, for cheap regeneration at a different length."""

    @abstractmethod
    def answer_question(self, text: str, question: str, history: QAHistory | None = None) -> str:
        """Answer a free-form question grounded in the document text only.

        `history` is prior (question, answer) turns for the same job, oldest
        first, letting a follow-up question be answered in context.
        """

    @abstractmethod
    def compare_documents(self, documents: list[tuple[str, str]]) -> StructuredComparison:
        """Compare 2+ documents, given as (name, text) pairs, in order."""
