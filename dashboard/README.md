# Track — Dashboard, demo video, submission

**Owner:** Benjamin

## Deliverable

A live paste-and-split page: paste any AI answer in, see it split into
kept (signal) and dropped (filler) sentences instantly, with the noise
ratio/level and filler-category breakdown from the `SignalCard`.

Simplest honest version: a small FastAPI endpoint wrapping
`sipa_signal.extract.extract()`, a page that posts the pasted text to it and
renders `kept_sentences` / `dropped_sentences` as two lists (strike through
the dropped ones — see the build-plan artifact for the visual reference).

## Also this track's job

- 2-minute demo video: paste a genuinely noisy real AI answer, show the
  split happening, show the noise score landing in VERY_NOISY, then a clean
  answer landing in CLEAN for contrast.
- lablab.ai project page + final README pass before the 24.09 deadline.
