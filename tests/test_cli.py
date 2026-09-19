"""Comprehensive tests for the sipa-signal CLI (cli/main.py).

Strategy
--------
All tests drive the CLI through its public ``main(argv)`` function so that the
logic is tested at the integration level without requiring the ``sipa-signal``
console script to be installed.  Where stdin interaction is needed we patch
``sys.stdin`` with an ``io.StringIO`` object and set ``isatty`` to return
``False`` so the TTY-guard is bypassed.

Test groups
-----------
1. Input: stdin (pipe), file path
2. Output modes: default (kept sentences), --json, --summary
3. Error paths: empty input, missing file, unreadable file, TTY with no args
4. Edge cases: clean text, very noisy text, multi-sentence mix
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cli.main import (
    _build_parser,
    _fmt_default,
    _fmt_json,
    _fmt_summary,
    main,
)
from sipa_signal import extract


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

CLEAN_TEXT = "The build failed at step 3. Exit code 137. Memory limit exceeded."
NOISY_TEXT = "Great question! I'd be happy to help. The invoice total is $412."
MIXED_TEXT = (
    "Great question! "
    "The server has 4 CPUs and 16 GB of RAM. "
    "As an AI, I think it's worth noting the disk is 90% full."
)


def _fake_stdin(text: str) -> MagicMock:
    """Return a mock that looks like a non-TTY stdin containing *text*."""
    mock = MagicMock(spec=io.StringIO)
    mock.read.return_value = text
    mock.isatty.return_value = False
    return mock


def _run(argv: list[str], stdin_text: str | None = None, capsys=None):
    """Run ``main(argv)`` and return ``(stdout, stderr)``."""
    ctx = (
        patch("sys.stdin", _fake_stdin(stdin_text))
        if stdin_text is not None
        else patch("sys.stdin", sys.stdin)  # leave stdin untouched
    )
    with ctx:
        main(argv)


# ---------------------------------------------------------------------------
# 1. Input handling
# ---------------------------------------------------------------------------

class TestStdinInput:
    def test_reads_piped_stdin_default(self, capsys):
        with patch("sys.stdin", _fake_stdin(CLEAN_TEXT)):
            main([])
        out = capsys.readouterr().out
        assert "build failed" in out

    def test_piped_stdin_with_json_flag(self, capsys):
        with patch("sys.stdin", _fake_stdin(CLEAN_TEXT)):
            main(["--json"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "kept_sentences" in data
        assert "noise_level" in data

    def test_piped_stdin_with_summary_flag(self, capsys):
        with patch("sys.stdin", _fake_stdin(CLEAN_TEXT)):
            main(["--summary"])
        out = capsys.readouterr().out
        assert "=== sipa-signal summary ===" in out
        assert "Noise level" in out

    def test_tty_stdin_without_file_exits_1(self, capsys):
        """When stdin is a TTY and no file is given, exit with code 1."""
        tty_mock = MagicMock()
        tty_mock.isatty.return_value = True
        with patch("sys.stdin", tty_mock):
            with pytest.raises(SystemExit) as exc_info:
                main([])
        assert exc_info.value.code == 1
        err = capsys.readouterr().err
        assert "no input provided" in err


class TestFileInput:
    def test_reads_text_file(self, tmp_path: Path, capsys):
        f = tmp_path / "input.txt"
        f.write_text(CLEAN_TEXT, encoding="utf-8")
        main([str(f)])
        out = capsys.readouterr().out
        assert "build failed" in out

    def test_reads_file_with_json_flag(self, tmp_path: Path, capsys):
        f = tmp_path / "input.txt"
        f.write_text(CLEAN_TEXT, encoding="utf-8")
        main([str(f), "--json"])
        data = json.loads(capsys.readouterr().out)
        assert isinstance(data["kept_sentences"], list)

    def test_reads_file_with_summary_flag(self, tmp_path: Path, capsys):
        f = tmp_path / "input.txt"
        f.write_text(NOISY_TEXT, encoding="utf-8")
        main([str(f), "--summary"])
        out = capsys.readouterr().out
        assert "Dropped sentences" in out

    def test_missing_file_exits_1(self, tmp_path: Path, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main([str(tmp_path / "nonexistent.txt")])
        assert exc_info.value.code == 1
        assert "file not found" in capsys.readouterr().err

    def test_directory_path_exits_1(self, tmp_path: Path, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main([str(tmp_path)])  # a directory, not a file
        assert exc_info.value.code == 1
        assert "not a regular file" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# 2. Output modes
# ---------------------------------------------------------------------------

class TestDefaultOutput:
    """Default mode: only kept sentences, one per line."""

    def test_only_kept_sentences_printed(self, capsys):
        with patch("sys.stdin", _fake_stdin(NOISY_TEXT)):
            main([])
        out = capsys.readouterr().out
        lines = [l for l in out.splitlines() if l.strip()]
        card = extract(NOISY_TEXT)
        assert lines == card.kept_sentences

    def test_clean_text_all_kept(self, capsys):
        with patch("sys.stdin", _fake_stdin(CLEAN_TEXT)):
            main([])
        out = capsys.readouterr().out.strip()
        assert out  # non-empty
        card = extract(CLEAN_TEXT)
        assert len(out.splitlines()) == len(card.kept_sentences)

    def test_output_ends_with_newline(self, capsys):
        with patch("sys.stdin", _fake_stdin(CLEAN_TEXT)):
            main([])
        raw = capsys.readouterr().out
        assert raw.endswith("\n")


class TestJsonOutput:
    """--json mode: valid JSON matching SignalCard.to_dict() schema."""

    def test_valid_json_structure(self, capsys):
        with patch("sys.stdin", _fake_stdin(MIXED_TEXT)):
            main(["--json"])
        data = json.loads(capsys.readouterr().out)
        required_keys = {
            "original_word_count",
            "signal_word_count",
            "filler_hits",
            "kept_sentences",
            "dropped_sentences",
            "noise_ratio",
            "noise_level",
            "compression",
        }
        assert required_keys.issubset(data.keys())

    def test_json_lists_are_lists(self, capsys):
        with patch("sys.stdin", _fake_stdin(MIXED_TEXT)):
            main(["--json"])
        data = json.loads(capsys.readouterr().out)
        assert isinstance(data["kept_sentences"], list)
        assert isinstance(data["dropped_sentences"], list)

    def test_json_noise_level_is_string(self, capsys):
        with patch("sys.stdin", _fake_stdin(CLEAN_TEXT)):
            main(["--json"])
        data = json.loads(capsys.readouterr().out)
        assert isinstance(data["noise_level"], str)
        assert data["noise_level"] in ("CLEAN", "NOISY", "VERY_NOISY")

    def test_json_ratios_are_floats(self, capsys):
        with patch("sys.stdin", _fake_stdin(CLEAN_TEXT)):
            main(["--json"])
        data = json.loads(capsys.readouterr().out)
        assert isinstance(data["noise_ratio"], float)
        assert isinstance(data["compression"], float)

    def test_json_matches_extract(self, capsys):
        with patch("sys.stdin", _fake_stdin(MIXED_TEXT)):
            main(["--json"])
        data = json.loads(capsys.readouterr().out)
        expected = extract(MIXED_TEXT).to_dict()
        assert data == expected

    def test_json_and_summary_are_mutually_exclusive(self):
        parser = _build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--json", "--summary"])


class TestSummaryOutput:
    """--summary mode: human-readable text with all key sections."""

    def test_contains_header(self, capsys):
        with patch("sys.stdin", _fake_stdin(MIXED_TEXT)):
            main(["--summary"])
        assert "=== sipa-signal summary ===" in capsys.readouterr().out

    def test_contains_noise_level(self, capsys):
        with patch("sys.stdin", _fake_stdin(MIXED_TEXT)):
            main(["--summary"])
        out = capsys.readouterr().out
        assert "Noise level" in out

    def test_contains_noise_ratio(self, capsys):
        with patch("sys.stdin", _fake_stdin(MIXED_TEXT)):
            main(["--summary"])
        out = capsys.readouterr().out
        assert "Noise ratio" in out
        assert "%" in out

    def test_contains_kept_section(self, capsys):
        with patch("sys.stdin", _fake_stdin(MIXED_TEXT)):
            main(["--summary"])
        assert "Kept sentences" in capsys.readouterr().out

    def test_contains_dropped_section_when_noise_present(self, capsys):
        with patch("sys.stdin", _fake_stdin(NOISY_TEXT)):
            main(["--summary"])
        assert "Dropped sentences" in capsys.readouterr().out

    def test_no_dropped_section_for_clean_text(self, capsys):
        with patch("sys.stdin", _fake_stdin(CLEAN_TEXT)):
            main(["--summary"])
        assert "Dropped sentences" not in capsys.readouterr().out

    def test_filler_hits_section_present_for_noisy(self, capsys):
        with patch("sys.stdin", _fake_stdin(NOISY_TEXT)):
            main(["--summary"])
        assert "Filler hits by category" in capsys.readouterr().out

    def test_compression_present(self, capsys):
        with patch("sys.stdin", _fake_stdin(NOISY_TEXT)):
            main(["--summary"])
        assert "Compression" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# 3. Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_empty_stdin_exits_1(self, capsys):
        with patch("sys.stdin", _fake_stdin("   \n\t  ")):
            with pytest.raises(SystemExit) as exc_info:
                main([])
        assert exc_info.value.code == 1
        assert "empty" in capsys.readouterr().err

    def test_empty_file_exits_1(self, tmp_path: Path, capsys):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        with pytest.raises(SystemExit) as exc_info:
            main([str(f)])
        assert exc_info.value.code == 1

    def test_error_message_goes_to_stderr(self, tmp_path: Path, capsys):
        with pytest.raises(SystemExit):
            main([str(tmp_path / "no_such_file.txt")])
        captured = capsys.readouterr()
        assert captured.err  # stderr has content
        assert not captured.out  # stdout is silent


# ---------------------------------------------------------------------------
# 4. Formatter unit tests (pure functions, no I/O)
# ---------------------------------------------------------------------------

class TestFormatterFunctions:
    def _card(self, text: str):
        return extract(text)

    def test_fmt_default_returns_kept_sentences(self):
        card = self._card(NOISY_TEXT)
        result = _fmt_default(card)
        assert result == "\n".join(card.kept_sentences)

    def test_fmt_json_is_valid_json(self):
        card = self._card(CLEAN_TEXT)
        result = _fmt_json(card)
        data = json.loads(result)
        assert data["kept_sentences"] == card.kept_sentences

    def test_fmt_summary_contains_all_sections(self):
        card = self._card(MIXED_TEXT)
        result = _fmt_summary(card)
        assert "Noise level" in result
        assert "Kept sentences" in result

    def test_fmt_default_empty_kept(self):
        """If all sentences are dropped, default output is an empty string."""
        # Construct a card where kept_sentences is empty via a known pure-filler text.
        card = extract("Great question!")
        if not card.kept_sentences:
            assert _fmt_default(card) == ""

    def test_fmt_json_noise_ratio_rounded(self):
        card = self._card(NOISY_TEXT)
        data = json.loads(_fmt_json(card))
        # to_dict() rounds to 4 decimal places
        assert len(str(data["noise_ratio"]).split(".")[-1]) <= 4


# ---------------------------------------------------------------------------
# 5. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_single_clean_sentence(self, capsys):
        text = "The database replication lag is 42 ms."
        with patch("sys.stdin", _fake_stdin(text)):
            main([])
        out = capsys.readouterr().out.strip()
        assert out == text

    def test_unicode_text(self, capsys):
        text = "Ångström units are used. Naïve assumptions fail."
        with patch("sys.stdin", _fake_stdin(text)):
            main(["--json"])
        data = json.loads(capsys.readouterr().out)
        assert isinstance(data["kept_sentences"], list)

    def test_very_noisy_text_json(self, capsys):
        text = (
            "Great question! I'd be happy to help. As an AI, I think it's worth "
            "noting that, in my opinion, arguably, to some extent, the answer is 4."
        )
        with patch("sys.stdin", _fake_stdin(text)):
            main(["--json"])
        data = json.loads(capsys.readouterr().out)
        assert data["noise_level"] in ("NOISY", "VERY_NOISY")

    def test_file_and_json_flag_together(self, tmp_path: Path, capsys):
        f = tmp_path / "data.txt"
        f.write_text(CLEAN_TEXT, encoding="utf-8")
        main([str(f), "--json"])
        data = json.loads(capsys.readouterr().out)
        assert data["original_word_count"] > 0
