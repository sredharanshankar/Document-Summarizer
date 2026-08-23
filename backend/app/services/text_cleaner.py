"""Text cleaning/normalization shared by the PDF and OCR extraction paths.

Handles the artifacts both sources produce: broken/hyphenated lines,
repeated whitespace, unicode inconsistencies, and headers/footers that
repeat across pages. Intentionally conservative - it normalizes noise
within a paragraph while keeping blank lines between paragraphs, so
document structure survives cleaning.
"""

from __future__ import annotations

import re
import unicodedata

_HYPHEN_LINEBREAK = re.compile(r"(\w)-\n(\w)")
_MULTIPLE_SPACES = re.compile(r"[ \t]+")
_PARAGRAPH_BREAK = re.compile(r"\n{2,}")

# A page needs at least this many lines before we bother checking for a
# repeated header/footer - short pages make the heuristic unreliable.
MIN_LINES_FOR_BOUNDARY_CHECK = 2
# Fraction of pages a line must appear on (as first/last line) to be
# considered a repeated header/footer rather than real content.
REPETITION_THRESHOLD = 0.6


def clean_pages(page_texts: list[str]) -> str:
    """Clean a list of per-page raw text and join into one normalized document."""
    stripped_pages = _strip_repeated_boundary_lines(page_texts)
    cleaned_pages = [_clean_single_page(page) for page in stripped_pages]
    return "\n\n".join(page for page in cleaned_pages if page)


def _clean_single_page(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _HYPHEN_LINEBREAK.sub(r"\1\2", text)  # de-hyphenate wrapped words

    paragraphs = []
    for paragraph in _PARAGRAPH_BREAK.split(text):
        # Rejoin lines that were only wrapped mid-paragraph (e.g. PDF line
        # width), collapsing them onto one line without losing word breaks.
        lines = [line.strip() for line in paragraph.split("\n") if line.strip()]
        joined = _MULTIPLE_SPACES.sub(" ", " ".join(lines)).strip()
        if joined:
            paragraphs.append(joined)

    return "\n\n".join(paragraphs)


def _strip_repeated_boundary_lines(page_texts: list[str]) -> list[str]:
    if len(page_texts) < 3:
        return page_texts  # not enough pages to reliably detect repetition

    first_lines: list[str] = []
    last_lines: list[str] = []
    for text in page_texts:
        lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
        if len(lines) < MIN_LINES_FOR_BOUNDARY_CHECK:
            continue
        first_lines.append(lines[0].lower())
        last_lines.append(lines[-1].lower())

    repeated_headers = _find_repeated(first_lines, len(page_texts))
    repeated_footers = _find_repeated(last_lines, len(page_texts))

    if not repeated_headers and not repeated_footers:
        return page_texts

    result = []
    for text in page_texts:
        lines = text.strip().split("\n")
        if lines and lines[0].strip().lower() in repeated_headers:
            lines = lines[1:]
        if lines and lines[-1].strip().lower() in repeated_footers:
            lines = lines[:-1]
        result.append("\n".join(lines))
    return result


def _find_repeated(candidates: list[str], page_count: int) -> set[str]:
    counts: dict[str, int] = {}
    for line in candidates:
        counts[line] = counts.get(line, 0) + 1
    threshold = max(page_count * REPETITION_THRESHOLD, 3)
    return {line for line, count in counts.items() if count >= threshold}
