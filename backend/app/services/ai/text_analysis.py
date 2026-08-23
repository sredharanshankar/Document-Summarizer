"""Pure text-analysis helpers backing the extractive fallback provider.

No external NLP dependency (nltk/spacy) - a small hand-rolled stopword
list and regex sentence splitter are plenty for frequency-based sentence
scoring, and avoid pulling in a large model download for a fallback path
that exists specifically to work with zero external dependencies.
"""

from __future__ import annotations

import re
from collections import Counter

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")
_WORD = re.compile(r"[A-Za-z']+")

STOPWORDS = frozenset(
    """
    a an the and or but if then else when while of to in on at for from by
    with about against between into through during before after above below
    up down out off over under again further once here there all any both
    each few more most other some such no nor not only own same so than too
    very s t can will just don should now is are was were be been being have
    has had having do does did doing would could shall might must this that
    these those i you he she it we they me him her us them my your his its
    our their what which who whom as because until while
    """.split()
)


def split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    for paragraph in text.split("\n\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        for sentence in _SENTENCE_SPLIT.split(paragraph):
            sentence = sentence.strip()
            if sentence:
                sentences.append(sentence)
    return sentences


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def word_frequencies(text: str) -> Counter[str]:
    words = [w.lower() for w in _WORD.findall(text) if w.lower() not in STOPWORDS and len(w) > 1]
    return Counter(words)


def top_keywords(frequencies: Counter[str], n: int = 10) -> list[str]:
    return [word for word, _ in frequencies.most_common(n)]


def extract_keywords(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text) if w.lower() not in STOPWORDS and len(w) > 1}


def score_sentences_by_query(sentences: list[str], query: str) -> list[float]:
    """Score each sentence by keyword overlap with a query (0-1), for extractive Q&A."""
    keywords = extract_keywords(query)
    if not keywords:
        return [0.0] * len(sentences)
    return [len(keywords & extract_keywords(sentence)) / len(keywords) for sentence in sentences]


def score_sentences(sentences: list[str], frequencies: Counter[str]) -> list[float]:
    if not frequencies:
        return [0.0] * len(sentences)
    max_freq = max(frequencies.values())
    scores = []
    for sentence in sentences:
        words = [w.lower() for w in _WORD.findall(sentence)]
        content_words = [w for w in words if w not in STOPWORDS and len(w) > 1]
        if not content_words:
            scores.append(0.0)
            continue
        raw_score = sum(frequencies.get(w, 0) for w in content_words) / max_freq
        # Normalize by length so long sentences don't win purely on word count.
        scores.append(raw_score / len(content_words) ** 0.5)
    return scores
