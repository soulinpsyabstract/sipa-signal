"""The extractor. Splits text into sentences, matches every sentence against
the fixed pattern table, and sorts each sentence into kept (carries content)
or dropped (nothing left once the filler is stripped out).

A sentence is dropped only when almost nothing survives removing the matched
filler spans - a sentence can mention a hedge word AND still carry a real
claim, and that sentence is kept, filler and all. This isn't trying to be
clever about meaning; it's counting.
"""
from __future__ import annotations

import re

from .card import NoiseLevel, SignalCard
from .patterns import FILLER_PATTERNS, FillerCategory
from .score import classify_noise, noise_score

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
# A "word" has to contain at least one alphanumeric character - a lone "."
# or "," left behind after stripping a filler phrase doesn't count as content.
_WORD = re.compile(r"\S*\w\S*")

# A sentence with this few content words left after stripping filler spans
# is treated as pure filler - the threshold is a word count, not a guess.
_MIN_CONTENT_WORDS = 3


def _word_count(text: str) -> int:
    return len(_WORD.findall(text))


def _strip_matches(sentence: str) -> tuple[str, dict]:
    """Remove every filler-pattern match from the sentence; return what's
    left plus a per-category hit count for this sentence."""
    hits: dict[str, int] = {}
    remaining = sentence
    for fp in FILLER_PATTERNS:
        matches = list(fp.pattern.finditer(remaining))
        if matches:
            hits[fp.category.value] = hits.get(fp.category.value, 0) + len(matches)
            remaining = fp.pattern.sub(" ", remaining)
    return remaining, hits


def extract(text: str) -> SignalCard:
    original_word_count = _word_count(text)
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]

    kept: list[str] = []
    dropped: list[str] = []
    filler_hits: dict[str, int] = {c.value: 0 for c in FillerCategory}
    filler_word_total = 0

    for sentence in sentences:
        remaining, hits = _strip_matches(sentence)
        for cat, n in hits.items():
            filler_hits[cat] += n
        filler_word_total += _word_count(sentence) - _word_count(remaining)

        if _word_count(remaining) < _MIN_CONTENT_WORDS and hits:
            dropped.append(sentence)
        else:
            kept.append(sentence)

    signal_word_count = sum(_word_count(s) for s in kept)
    ratio = noise_score(filler_word_total, original_word_count)

    return SignalCard(
        original_word_count=original_word_count,
        signal_word_count=signal_word_count,
        filler_hits=filler_hits,
        kept_sentences=kept,
        dropped_sentences=dropped,
        noise_ratio=ratio,
        noise_level=classify_noise(ratio),
    )
