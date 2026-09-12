"""Before/after on a real, typical AI-assistant answer. No API keys, no
network - the point is what the extraction does, not where the text came from.

    python run_demo.py
"""
from __future__ import annotations

from sipa_signal.extract import extract

SAMPLE = (
    "Great question! I'd be happy to help you with that. "
    "As an AI, I think it's worth noting that, in my opinion, database "
    "migrations can be risky to some extent. "
    "The migration ran on 2026-09-11 at 03:14 UTC and affected 40,212 rows. "
    "Arguably, one might say that backups are important. "
    "The backup completed successfully at 03:09 UTC, five minutes before "
    "the migration started. "
    "To summarize, unfortunately, I must apologize if this wasn't exactly "
    "what you were looking for. "
    "Exit code was 0 and no errors were logged."
)


def main() -> None:
    card = extract(SAMPLE)

    print("== ORIGINAL ==")
    print(SAMPLE)
    print(f"\n{card.original_word_count} words\n")

    print("== KEPT (the signal) ==")
    for s in card.kept_sentences:
        print(f"  + {s}")

    print("\n== DROPPED (pure filler) ==")
    for s in card.dropped_sentences:
        print(f"  - {s}")

    print(f"\nfiller hits by category: {card.filler_hits}")
    print(f"noise ratio: {card.noise_ratio:.2%}  ->  {card.noise_level.name}")
    print(f"compression: {card.compression():.0%} of the original stripped out")


if __name__ == "__main__":
    main()
