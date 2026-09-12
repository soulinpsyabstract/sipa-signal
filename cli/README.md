# Track — CLI tool

**Owner:** Qais

## Deliverable

A pipeable command:

```bash
cat transcript.txt | sipa-signal              # prints kept/dropped view
cat transcript.txt | sipa-signal --json        # prints the SignalCard as JSON
sipa-signal "Great question! The answer is 4." # accepts a direct argument too
```

Built on `sipa_signal.extract.extract()` — this track doesn't touch the core
extraction logic, just wraps it in something usable from a shell pipeline
(stdin/argument in, formatted text or JSON out). `click` or `typer` both fit;
either add it to `requirements.txt`.

Exit code should reflect the noise level (e.g. non-zero for `VERY_NOISY`) so
it's usable as a lint-style check in a script, not just a human-facing tool.
