# Corpus Findings

Real AI transcripts tested against `sipa_signal.extract.extract()`. 
Each entry: original text, what the extractor likely does, what should happen, and suggested patch.

---

## Finding 1 — standalone "Sure."
- **Original:** "Sure. First tell me what Wi-Fi issue you're having..."
- **Extractor currently:** likely keeps or misses "Sure." as filler (not in FILLER_PATTERNS as a standalone word)
- **Should be:** "Sure." alone (no comma, no follow-up like "i'd be happy to") should count as THROAT_CLEARING
- **Patch:** add "sure" as a standalone pattern to THROAT_CLEARING in patterns.py

---

## Finding 2 — "the process generally goes like this"
- **Original:** "If you mean how to build a house, the process generally goes like this:"
- **Should be:** META_COMMENTARY filler
- **Patch:** add "generally goes like this" to META_COMMENTARY list

---

## Finding 3 — "I can teach you from zero" (borderline, no patch yet)
- **Original:** "I can teach you from zero."
- **Issue:** doesn't cleanly fit existing 5 categories (not hedge, not apology, not self-reference)
- **Decision:** log as borderline example only; do NOT create a new category without more supporting examples

---

## Finding 4 — Low-filler transcripts confirm threshold behavior
- **Tested:** Wi-Fi troubleshooting, house-building steps, motorcycle-riding steps
- **Observation:** all 3 had minimal filler — most content was genuine and structured
- **Confirms:** extractor should not over-strip clean, structured answers

---

## Finding 5 — "there can be" as soft intro hedge (weak, needs more examples)
- **Original:** "If you mean membership in a professional/student society, there can be several benefits:"
- **Issue:** possible HEDGE pattern before a list-style answer
- **Decision:** log only, do not add to patterns.py yet — need 2-3 more similar examples before confirming

---

## Finding 6 — Overall pattern across 5 real transcripts (Wi-Fi, house-building, motorcycle, society x2)
- **Observation:** none contained "classic" cliché filler ("great question", "as an AI", "I apologize")
- **Only filler-like elements found:** subtle soft intros ("Sure.", "the process generally goes like this", "there can be several benefits")
- **Suggests:** FILLER_PATTERNS table may be too narrowly focused on hackathon-style clichés and should also watch for softer, natural intro phrasing

---

## Finding 7 — "Below is a [adj] answer" opening meta-commentary
- **Original:** "Below is a simple, assignment-friendly answer with 15 common problems..."
- **Should be:** META_COMMENTARY (describes the answer rather than answering)
- **Patch:** add "below is" / "here is a" framing phrases to META_COMMENTARY list

---

## Finding 8 — Whole-paragraph conclusion filler (structural, not single-phrase)
- **Original:** full "Conclusion" paragraph restating a 15-point list with no new information
- **Issue:** current extractor works sentence-by-sentence (per README); this is a multi-sentence redundant block, not a single filler phrase
- **Flag for core owner (Aelin):** pattern table may need a way to catch "restates prior content with no new claim" blocks, not just fixed phrases

---

## Finding 9 — Stray artifact ("Writing")
- **Original:** isolated word "Writing" appearing before a document title
- **Issue:** likely a leaked internal label, not a filler pattern
- **Decision:** noted as anomaly only, no action needed
