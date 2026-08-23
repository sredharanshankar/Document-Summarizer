"""Shared test doubles, imported explicitly by the test modules that need them."""

import fitz
from PIL import Image

from app.models.schemas import SummaryLength
from app.services.ai.base import AIProvider, QAHistory, StructuredAnalysis, StructuredComparison
from app.services.ocr.base import OCRProvider


class FakeOCRProvider(OCRProvider):
    def __init__(self, text: str = "ocr extracted text") -> None:
        self.text = text
        self.call_count = 0

    def extract_text(self, image: Image.Image) -> str:
        self.call_count += 1
        return self.text


class FakeAIProvider(AIProvider):
    name = "fake"

    def __init__(self) -> None:
        self.analysis_calls: list[str] = []
        self.summary_calls: list[str] = []
        self.question_calls: list[tuple[str, str, QAHistory | None]] = []
        self.comparison_calls: list[list[tuple[str, str]]] = []

    def generate_analysis(self, text: str, summary_length: SummaryLength) -> StructuredAnalysis:
        self.analysis_calls.append(text)
        return StructuredAnalysis(
            summary=f"fake summary ({summary_length.value})",
            key_points=["fake key point"],
            main_ideas=["fake main idea"],
            improvement_suggestions=[],
        )

    def generate_summary(self, text: str, summary_length: SummaryLength) -> str:
        self.summary_calls.append(text)
        return f"fake chunk summary of {len(text)} chars"

    def answer_question(self, text: str, question: str, history: QAHistory | None = None) -> str:
        self.question_calls.append((text, question, history))
        return f"fake answer to: {question}"

    def compare_documents(self, documents: list[tuple[str, str]]) -> StructuredComparison:
        self.comparison_calls.append(documents)
        names = ", ".join(name for name, _ in documents)
        return StructuredComparison(
            comparison_summary=f"fake comparison of: {names}",
            similarities=["fake similarity"],
            differences=["fake difference"],
        )


def blank_pdf_bytes(page_count: int = 1) -> bytes:
    doc = fitz.open()
    for _ in range(page_count):
        doc.new_page()
    data = doc.tobytes()
    doc.close()
    return data
