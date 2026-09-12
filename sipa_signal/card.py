"""The fixed schema. Every extraction produces exactly this shape - same
fields, same order, whether the input was three sentences or three
paragraphs."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class NoiseLevel(IntEnum):
    CLEAN = 0       # under 5% filler
    NOISY = 1       # 5-20% filler
    VERY_NOISY = 2  # over 20% filler


@dataclass
class SignalCard:
    original_word_count: int
    signal_word_count: int
    filler_hits: dict            # FillerCategory value -> count
    kept_sentences: list[str]    # sentences with no filler match, in order
    dropped_sentences: list[str] # sentences that were pure filler, in order
    noise_ratio: float           # filler words / original words
    noise_level: NoiseLevel

    def compression(self) -> float:
        """Fraction of the original word count removed."""
        if self.original_word_count == 0:
            return 0.0
        return 1.0 - (self.signal_word_count / self.original_word_count)

    def to_dict(self) -> dict:
        return {
            "original_word_count": self.original_word_count,
            "signal_word_count": self.signal_word_count,
            "filler_hits": dict(self.filler_hits),
            "kept_sentences": list(self.kept_sentences),
            "dropped_sentences": list(self.dropped_sentences),
            "noise_ratio": round(self.noise_ratio, 4),
            "noise_level": self.noise_level.name,
            "compression": round(self.compression(), 4),
        }
