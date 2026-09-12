"""Deterministic noise scoring. Same text always scores the same - the ratio
is computed from a fixed pattern table, never from a model's own judgment of
how "clean" it sounds."""
from __future__ import annotations

from .card import NoiseLevel

CLEAN_MAX = 0.05
NOISY_MAX = 0.20


def noise_score(filler_word_count: int, total_word_count: int) -> float:
    if total_word_count == 0:
        return 0.0
    return filler_word_count / total_word_count


def classify_noise(ratio: float) -> NoiseLevel:
    if ratio <= CLEAN_MAX:
        return NoiseLevel.CLEAN
    if ratio <= NOISY_MAX:
        return NoiseLevel.NOISY
    return NoiseLevel.VERY_NOISY
