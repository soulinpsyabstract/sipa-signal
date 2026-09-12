"""sipa-signal: strip hedging and filler out of AI text, deterministically.

The problem isn't that AI answers are wrong - it's that the actual claim is
buried in throat-clearing, hedges, and meta-commentary a reader has to wade
through to find it. This doesn't ask a model to "summarize more concisely"
(a model grading its own prose has no fixed standard for concise). It runs a
fixed pattern table against the text and reports, mechanically, what's
filler and what's signal - then extracts the signal into a fixed-schema card.
"""
from .patterns import FillerCategory, FILLER_PATTERNS
from .card import SignalCard, NoiseLevel
from .extract import extract
from .score import noise_score, classify_noise

__all__ = [
    "FillerCategory",
    "FILLER_PATTERNS",
    "SignalCard",
    "NoiseLevel",
    "extract",
    "noise_score",
    "classify_noise",
]
