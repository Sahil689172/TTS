# Phase 1 — Architecture Audit

**Date:** 2026-08-29
**Goal (Phase 1 Step 14):** document the text→audio pipeline of each existing
model. **Explicitly NOT** to choose an architecture (Phase 0 RULE 3).

---

## 1. Result

> **BLOCKED — no model exists to reverse-engineer.**

The requested breakdown (text → tokenizer → text representation → encoder →
acoustic model → decoder/vocoder → audio, plus autoregressive vs
non-autoregressive, speaker conditioning, language conditioning, phoneme
handling, duration, pitch, prosody, streaming support, batching support,
inference memory) requires a model. There is none. Every field would read
UNKNOWN, and filling them with plausible-sounding values would be fabrication.

## 2. The one pipeline that DOES exist

Phase 1 built the **frontend** half of the chain. Documenting it now fixes the
interface any Phase 2 acoustic model must accept.

```
raw text
  |
  v  scripts.py        Unicode script detection; Tamil digits -> ASCII
script-tagged text
  |
  v  langid.py         per-token language ID: EN / TA / TA_LATIN
  |                    + matrix-language decision for the utterance
language-tagged tokens
  |
  v  tokenizer.py      tokenization + Tamil-suffix splitting
  |                    "Central-ல" -> stem "Central"[EN] + suffix "ல"[TA]
tokens (script, lang, suffix)
  |
  v  entities.py       context-sensitive entity detection
  |                    trigger words + structural patterns + upstream tags
typed entities (with determinism level)
  |
  v  verbalizer.py     entity -> spoken words, routed by MATRIX language
  |                    numbers_en.py / numbers_ta.py
  |
  v  pipeline.py       reassembly, abbreviation expansion, whitespace tidy
  v
TTS-ready output:
    spoken        - normalized orthographic text
    lang_segments - [(text, lang), ...]  <- language-conditioning signal
    entities      - typed, for diagnostics and upstream reconciliation
    tokens        - script/lang/suffix, for stage-level debugging
    warnings      - e.g. unvalidated Tamil forms
```

## 3. Deliberate architectural decision: text out, NOT phonemes

The frontend emits **normalized text plus language tags**, not phonemes or IPA.

**Why** (recorded as a decision so it can be revisited): Phase 0 RULE 2 forbids
selecting a model in Phase 0/1, and the phoneme inventory is a *property of the
chosen model*. Emitting phonemes now would require inventing a symbol set —
which Phase 0 §19.6 identifies as the single decision most likely to make
Tanglish impossible later:

> "If Phase 3 ships a Tamil model with a Tamil-only phoneme set … Phase 8
> discovers that intra-word code-mixing has no representation and the fix is a
> retrain."

Emitting text keeps every downstream option open: grapheme input, phoneme input
via a Phase 2-selected G2P, or byte/subword input.

**Cost of this choice:** the training/inference representation mismatch is
*deferred*, not solved. See `normalization_audit.md` §6.

## 4. What Phase 2 must document per candidate

This is the table Phase 1 could not fill. Phase 2 must complete it for every
candidate **before** any selection:

| Field | Why it matters here |
|---|---|
| Input representation (grapheme / phoneme / byte / subword) | determines whether `tnorm` output is directly consumable |
| Tokenizer script coverage | must represent **both** Tamil and Latin, or Tanglish is impossible (Phase 0 CX-06) |
| Language conditioning mechanism | needed to consume `lang_segments`; its absence is a serious Tanglish risk |
| Speaker conditioning mechanism | Phase 0 C-07 — entangling speaker with language breaks code-switch consistency |
| Autoregressive vs non-autoregressive | drives the TTFA/quality trade-off (Phase 0 C-01, C-05) |
| Streaming support | Phase 0 IR-01 is mandatory |
| Native sample rate | Phase 0 Q-02 / risks R-13, R-16 |
| Batching support | Phase 0 C-04, concurrency vs latency |
| Inference memory (CPU and GPU) | this machine had 2.6 GB RAM free at measurement |
