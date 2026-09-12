# Track — Real-world pattern coverage

**Owners:** Hussnain, Khuda Bux

`sipa_signal/patterns.py` currently has phrases we typed from memory — a
starting seed, not a real corpus. This track grows it against real text.

## Deliverable

1. Collect real AI-assistant transcripts from a few different domains
   (support chat, code review comments, meeting-notes summarizers). A few
   dozen real examples beats a hundred invented ones.
2. Run `sipa_signal.extract.extract()` against each one. For every sentence
   that a human would call "filler" but the extractor kept (or vice versa),
   note it.
3. Add the missed phrases to `FILLER_PATTERNS` in `sipa_signal/patterns.py`
   — same shape as what's there: `FillerCategory` + the literal phrase.
   Don't invent a new category unless a real example genuinely doesn't fit
   the existing five.
4. If the drop threshold (`_MIN_CONTENT_WORDS` in `extract.py`) is
   consistently too strict or too loose against real examples, that's a
   real finding — write it down with the examples that show it, not just a
   number change.

## Where to put findings

`corpus/findings.md` — one entry per real example: the original text, what
the extractor did, what should have happened, and the patch (if any) applied
to `patterns.py`. This becomes the evidence trail for why the table looks
the way it does by submission day.
