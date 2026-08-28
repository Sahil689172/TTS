# Phase 1 — Tanglish Implications

**Date:** 2026-08-29
**Scope:** Phase 1 Step 19. **No Tanglish training was performed** and none was
attempted (Phase 1: "Do NOT train Tanglish").

This document answers the ten Step 19 questions from Phase 1 evidence. Where
evidence does not exist, the answer is UNKNOWN rather than a guess.

---

## 1. The ten questions

### Q1. Can the existing English system represent Tamil?
**UNANSWERABLE — no English system exists.** (`model_inventory.md`)

### Q2. Can the existing Tamil system represent English?
**UNANSWERABLE — no Tamil system exists.**

### Q3. Can either model condition on language?
**UNANSWERABLE — no model exists.**

What Phase 1 *can* say: the frontend **produces** a per-segment language signal
(`lang_segments`), so if a Phase 2 model supports language conditioning, the
input side is already solved. If it does not, that signal is discarded.

### Q4. Can the tokenizer represent both scripts?
**UNANSWERABLE for a model tokenizer.**

For the **frontend** tokenizer: **YES, verified.** `tokenizer.py` handles Tamil
script, Latin script, mixed-script strings, and — critically — *intra-word*
mixing where a Tamil suffix attaches to an English stem. Verified by
`TestTokenizer::test_tamil_suffix_on_english_stem`:

```
"Chennai Central-ல"  ->  Token(text="Central", lang=EN, suffix="ல")
```

The stem retains **English** identity while the suffix retains **Tamil**
identity. This is the property that makes intra-word code-mixing representable
at all.

### Q5. Can Tamil-in-Latin text be represented?
**PARTIALLY — with a measured, honest limitation.**

`langid.py` distinguishes `TA_LATIN` from `EN` inside Latin script using a
closed lexicon (~120 romanized Tamil forms) plus five orthographic cues.
Verified working on the Phase 0 example `unga pickup location enga?` → matrix
`ta-latn`, code-mixed `true`.

**But:** accuracy is **unmeasured** because no labelled TA-Latin evaluation set
exists. Known failures: out-of-lexicon romanized Tamil defaults to English;
spelling variation is only partly covered; genuinely ambiguous tokens (`car`,
`auto`, `ok`) are resolved by lexicon precedence rather than context. Phase 0
§5.1's point that Latin-script Tanglish has **no canonical orthography** is the
root cause and is not solvable by a bigger lexicon alone.

### Q6. How is speaker identity represented?
**UNANSWERABLE — no model.** Additionally blocked by unanswered Phase 0 **Q-09**
(similarity to a reference voice vs self-consistency) and **Q-11** (one voice or
several). See `speaker_audit.md`.

### Q7. Can the architecture theoretically support code-switching?
**UNANSWERABLE for the acoustic architecture.**

For the frontend architecture: **YES by construction.** Three properties were
built in specifically to keep code-switching reachable:

1. **Per-token language tags** carried from the first stage to the output.
2. **Intra-word stem/suffix separation** with independent language identity.
3. **Matrix-language routing** of entity verbalization, so a number inside a
   Tamil sentence reads in Tamil (Phase 0 §8 N14) — verified:
   `Driver இன்னும் 5 minutes-ல வருவார்.` → `... ஐந்து நிமிடம் ...`

### Q8. What would have to change?
Based on Phase 1 evidence, the changes fall into three tiers:

| Tier | Change | Why |
|---|---|---|
| **Cheap (frontend)** | expand the TA-Latin lexicon; add transliteration; author the full Phase 0 §8.2 case counts; validate Tamil verbalization | all are data/lexicon work in `src/tnorm/`, no retraining |
| **Moderate (integration)** | make the acoustic model consume `lang_segments`; decide the acoustic realisation of a stranded Tamil suffix | needs a model that supports language conditioning |
| **Expensive (model)** | tokenizer/symbol inventory covering both scripts; speaker representation disentangled from language; code-mixed training data | **requires retraining** — see Q9 |

### Q9. What cannot be changed without retraining?
This is the Phase 0 RULE 9 / §19.6 question, and Phase 1 confirms its shape:

1. **The symbol/token inventory.** If a model ships with a Tamil-only or
   English-only vocabulary, mixed-script input has no representation. Cannot be
   fixed post hoc.
2. **Whether the model conditions on language at all.** If there is no language
   input, `lang_segments` cannot be injected without architectural change.
3. **Speaker/language entanglement.** Phase 0 C-07: if the speaker embedding is
   entangled with language identity, timbre will drift at code-switch
   boundaries — the most audible Tanglish failure — and disentangling it is a
   retrain.
4. **Native sample rate** (Phase 0 Q-02 / R-13): a model trained at 24 kHz
   cannot be made natively narrowband.

### Q10. What should Phase 2 investigate?
See `phase2_requirements.md` for the full evidence-based list. In priority
order: script coverage of the tokenizer; language-conditioning mechanism;
speaker/language separability; streaming support; native sample rate; CPU
feasibility; licence permissiveness for derivative models and redistribution.

## 2. The Phase 1 finding that matters most for Tanglish

> **The frontend deliberately does not commit to a phoneme inventory.**

Phase 0 §19.6 names the symbol inventory as the decision most likely to make
Tanglish impossible later. Phase 1 avoided it by emitting normalized *text* plus
language tags rather than phonemes (`architecture_audit.md` §3).

The consequence is that **Phase 2 inherits the choice unconstrained** — no
Phase 1 artifact has to be thrown away whichever representation is selected.
That is the concrete way Phase 1 discharges Phase 0 CX-06 / RULE 9.

## 3. Risks confirmed or sharpened by Phase 1

| Phase 0 risk | Phase 1 evidence | Status |
|---|---|---|
| **R-02** insufficient Tanglish data | no corpus found; none exists in-repo; Phase 0 already rated this H/H | **CONFIRMED, unchanged — still the project's single greatest risk** |
| **R-03** poor Tanglish pronunciation | frontend can tag language per token, so the *input* side is prepared; acoustic side untested | **OPEN** |
| **R-04** unnatural code-switching | cannot be assessed without audio | **OPEN** |
| **R-05** speaker inconsistency | segmentation for O-05(ii) now exists (`speaker_audit.md` §3) | **partially mitigated (measurement path prepared)** |
| **R-13** train/inference mismatch | frontend emits mixed-script text; a single-script tokenizer would break on it | **SHARPENED — now a concrete Phase 2 selection criterion** |
| **R-16** telephony bandwidth blind spot | Q-02 still unanswered; no audio path exists to test | **UNCHANGED — still blocking** |

## 4. Reiteration of scope

No Tanglish model was trained, fine-tuned, adapted or evaluated. No Tanglish
audio exists. No claim is made about Tanglish speech quality. Everything above
concerns the **text frontend** and what it implies for future model choices.
