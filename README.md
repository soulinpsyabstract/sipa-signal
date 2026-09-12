# sipa-signal

**Strips hedging and filler from AI text into a fixed-schema signal card.**

Built for the [WeAreDevelopers Hackathon](https://lablab.ai/ai-hackathons/wearedevelopers-hackathon)
(online build 18–24 Sep 2026) by team **SIPA_OS**.

## The idea

The team's own line on every hackathon page so far: *"eliminate cognitive
noise with a clean terminal."* This is that, built literally. AI answers
bury the actual claim in throat-clearing, hedges, and self-referential
filler — "great question," "it's worth noting," "as an AI, I think." Reading
past that costs real effort.

sipa-signal doesn't ask a model to write more concisely — there's no fixed
standard for "concise" a model can be graded against by itself. It runs a
fixed phrase table against the text, drops sentences that are pure filler
once the phrases are stripped, and keeps everything else exactly as written.

## Quickstart (no API keys)

```bash
pip install -e ".[dev]"
python run_demo.py     # real example, before/after
pytest -q              # 12 tests
```

```python
from sipa_signal import extract

card = extract("Great question! The invoice total is $412.")
card.kept_sentences     # ["The invoice total is $412."]
card.dropped_sentences  # ["Great question!"]
card.noise_level        # NoiseLevel.NOISY
```

## Repo structure

| Dir | Track | Owner | Status |
| --- | --- | --- | --- |
| [`sipa_signal/`](sipa_signal/) | Core: patterns, extraction, scoring, schema | Aelin | **built, 12 tests** |
| [`corpus/`](corpus/) | Real-world pattern coverage | Hussnain, Khuda Bux | to build |
| [`cli/`](cli/) | Pipeable command-line tool | Qais | to build |
| [`dashboard/`](dashboard/) | Live demo + video + submission | Benjamin | to build |
| [`docs/`](docs/) | Build plan, timeline, checklist | — | — |

## Build plan

Full concept, timeline, and submission checklist:
[docs/BUILD_PLAN.md](docs/BUILD_PLAN.md)

## Team

Aelin AquaSoul · Benjamin Hong · Hussnain Dawood · Khuda Bux Mahar · Qais Amro
— team **SIPA_OS** on lablab.ai

## License

Apache 2.0
