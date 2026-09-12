"""The fixed pattern table. Every phrase here was picked because it adds no
claim, no number, no action - only tone. Extend this table (via `corpus/`,
see that track's README) rather than hand-tuning matches per document; the
whole point is one table applied the same way to any text.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class FillerCategory(str, Enum):
    THROAT_CLEARING = "throat_clearing"   # "Great question!", "Sure, happy to help"
    HEDGE = "hedge"                        # "it's worth noting", "arguably", "to some extent"
    META_COMMENTARY = "meta_commentary"    # "as mentioned above", "in conclusion", "let me explain"
    SELF_REFERENCE = "self_reference"      # "as an AI", "I think", "in my opinion"
    APOLOGY = "apology"                    # "I apologize", "unfortunately I"


@dataclass(frozen=True)
class FillerPattern:
    category: FillerCategory
    pattern: re.Pattern


def _p(category: FillerCategory, *phrases: str) -> list[FillerPattern]:
    return [FillerPattern(category, re.compile(re.escape(ph), re.IGNORECASE)) for ph in phrases]


_RAW_PATTERNS: list[FillerPattern] = [
    *_p(FillerCategory.THROAT_CLEARING,
        "great question", "happy to help", "sure, i'd be happy to",
        "i'd be glad to", "let's dive in", "let's take a look"),
    *_p(FillerCategory.HEDGE,
        "it's worth noting", "it is worth noting", "arguably", "to some extent",
        "in some sense", "it could be argued", "one might say", "to a certain degree",
        "it's important to note", "it is important to note"),
    *_p(FillerCategory.META_COMMENTARY,
        "as mentioned above", "as previously mentioned", "in conclusion",
        "let me explain", "to summarize", "with that said", "having said that",
        "moving on to", "let's break this down"),
    *_p(FillerCategory.SELF_REFERENCE,
        "as an ai", "as an ai language model", "i think", "i believe",
        "in my opinion", "personally, i", "i would say"),
    *_p(FillerCategory.APOLOGY,
        "i apologize", "i'm sorry", "unfortunately, i", "i must apologize"),
]

# Longest phrase first: "sure, i'd be happy to" has to be tried before
# "happy to help" or the shorter phrase eats part of the longer one and
# leaves an orphan fragment ("Sure, I'd be") that isn't real content but
# also isn't recognized as filler.
FILLER_PATTERNS: list[FillerPattern] = sorted(
    _RAW_PATTERNS, key=lambda fp: len(fp.pattern.pattern), reverse=True
)
