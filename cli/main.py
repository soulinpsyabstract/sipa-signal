"""sipa-signal CLI entry point.

Usage examples
--------------
# Pipe from stdin (default: print kept sentences)
echo "Great question! The build failed at step 3." | sipa-signal

# Read from a file
sipa-signal path/to/input.txt

# Output structured JSON
cat file.txt | sipa-signal --json

# Human-readable summary
sipa-signal report.txt --summary
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

from sipa_signal import extract
from sipa_signal.card import SignalCard


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def _fmt_default(card: SignalCard) -> str:
    """Return the kept sentences joined by newlines (default output mode)."""
    return "\n".join(card.kept_sentences)


def _fmt_json(card: SignalCard) -> str:
    """Return the full SignalCard serialised as indented JSON."""
    return json.dumps(card.to_dict(), indent=2, ensure_ascii=False)


def _fmt_summary(card: SignalCard) -> str:
    """Return a compact, human-readable summary of the extraction results."""
    lines: list[str] = [
        "=== sipa-signal summary ===",
        f"Noise level  : {card.noise_level.name}",
        f"Noise ratio  : {card.noise_ratio:.1%}",
        f"Words total  : {card.original_word_count}",
        f"Words kept   : {card.signal_word_count}",
        f"Compression  : {card.compression():.1%}",
        "",
        f"Kept sentences ({len(card.kept_sentences)}):",
    ]
    for i, s in enumerate(card.kept_sentences, 1):
        lines.append(f"  {i}. {s}")

    if card.dropped_sentences:
        lines.append("")
        lines.append(f"Dropped sentences ({len(card.dropped_sentences)}):")
        for i, s in enumerate(card.dropped_sentences, 1):
            lines.append(f"  {i}. {s}")

    if any(v for v in card.filler_hits.values()):
        lines.append("")
        lines.append("Filler hits by category:")
        for category, count in card.filler_hits.items():
            if count:
                lines.append(f"  {category}: {count}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sipa-signal",
        description=(
            "Strip hedging and filler from text and extract a signal card. "
            "Reads from a FILE path or from stdin when no file is given."
        ),
    )
    parser.add_argument(
        "file",
        metavar="FILE",
        nargs="?",
        default=None,
        help="Path to input text file. Omit to read from stdin.",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output the full SignalCard as formatted JSON.",
    )
    mode.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Output a human-readable analysis summary.",
    )

    return parser


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _die(message: str, exit_code: int = 1) -> NoReturn:
    """Print *message* to stderr and exit with *exit_code*."""
    print(f"sipa-signal: error: {message}", file=sys.stderr)
    sys.exit(exit_code)


def _read_stdin() -> str:
    """Read all of stdin, raising SystemExit if nothing is available."""
    if sys.stdin.isatty():
        _die(
            "no input provided. Pass a FILE argument or pipe text via stdin.\n"
            "Example: echo 'Hello.' | sipa-signal"
        )
    return sys.stdin.read()


def _read_file(path_str: str) -> str:
    """Read *path_str* from disk, producing helpful errors on failure."""
    path = Path(path_str)
    if not path.exists():
        _die(f"file not found: {path_str}")
    if not path.is_file():
        _die(f"not a regular file: {path_str}")
    try:
        return path.read_text(encoding="utf-8")
    except PermissionError:
        _die(f"permission denied: {path_str}")
    except OSError as exc:
        _die(f"could not read '{path_str}': {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    """Parse *argv* (or ``sys.argv[1:]``) and run the CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # --- read input ---------------------------------------------------------
    if args.file is not None:
        text = _read_file(args.file)
    else:
        text = _read_stdin()

    text = text.strip()
    if not text:
        _die("input is empty.")

    # --- extract ------------------------------------------------------------
    card = extract(text)

    # --- format & emit ------------------------------------------------------
    if args.json:
        output = _fmt_json(card)
    elif args.summary:
        output = _fmt_summary(card)
    else:
        output = _fmt_default(card)

    # Ensure output always ends with a single newline for clean shell piping.
    print(output)


if __name__ == "__main__":  # pragma: no cover
    main()
