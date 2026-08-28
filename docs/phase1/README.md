# Phase 1 — Existing System Audit + Normalization Foundation

**Status:** complete with documented blockers
**Date:** 2026-08-29
**Source of truth:** `../PHASE_0_REQUIREMENTS_FREEZE.md` — read first, unmodified

---

## Read this first

Phase 1 was scoped to audit an **existing English/Tamil TTS system**.
**No such system exists in this repository.** The repo contained one file: the
Phase 0 contract. See `repository_audit.md`.

Everything model-dependent is therefore reported as **BLOCKED**, not as passed.
Nothing was fabricated: no MOS, no WER, no TTFA, no concurrency number, no model
compatibility claim.

## Documents

| Document | What it answers |
|---|---|
| `phase0_consumption.md` | which Phase 0 requirements Phase 1 addressed, and which it could not |
| `repository_audit.md` | what was actually in the repository; contradictions found |
| `environment.md` | measured hardware/software; **corrects the stated disk figure** |
| `model_inventory.md` | every TTS model present — the result is empty |
| `download_manifest.md` | what would be needed, licences, sizes, approval gates |
| `reproducibility_audit.md` | what can be reproduced; missing pins |
| `architecture_audit.md` | frontend pipeline; why no phonemes are emitted |
| `speaker_audit.md` | speaker representation (blocked) and what Phase 1 prepared |
| `normalization_audit.md` | the normalization engine, tests, bugs, honest gaps |
| `baseline_results.md` | EN/TA baselines (blocked) + measured frontend latency |
| `tanglish_implications.md` | the ten Step 19 questions, answered from evidence |
| `phase2_requirements.md` | evidence-based Phase 2 selection criteria |
| `phase1_exit_report.md` | findings, blockers, exit-criteria scoring |

## What Phase 1 built

A rule-based, **zero-dependency** text normalization frontend at `src/tnorm/`,
implementing the Phase 0 §16 staged architecture:

```
raw text -> script detection -> language ID -> tokenization
         -> entity detection -> verbalization -> TTS-ready text + language tags
```

Key property: **per-token language identity is preserved end to end**, and no
phoneme inventory is committed to — the two things Phase 0 §19.6 names as most
likely to make Tanglish impossible later.

## Quick start

```bash
# run the test suite (104 passed, 4 xfailed)
python -m pytest

# try the normalizer
PYTHONPATH=src python -c "from tnorm import normalize; print(normalize('Your OTP is 4821.'))"
# -> Your O T P is four eight two one.

# frontend latency benchmark
python scripts/bench_frontend.py --iterations 300
```

## The requirement that matters most

Phase 0 PN-14 (release-blocking): the *same digit string* must render
differently by context. Verified:

| Input | Output |
|---|---|
| `Your OTP is 4821.` | `... four eight two one.` |
| `The fare is 4821 rupees.` | `... four thousand eight hundred twenty-one rupees.` |

## Known gaps — read before trusting anything

- **Tamil verbalization is UNVALIDATED by a native speaker** (`numbers_ta.py`
  carries an explicit banner). Tamil tests pin behaviour, not correctness.
- **TA-Latin language-ID accuracy is unmeasured** — no labelled set exists.
- **Test-set counts fall short** of the Phase 0 §8.2 / §9 floors.
- **All five Phase 0 blocking exit gates are still open** (G-00, G-03, G-18,
  G-19, G-20).

## Storage rule

Model weights must **never** be stored in this repository. C: has 16.4 GB free
and is OneDrive-synced. Use `D:\tts-models` via `TTS_MODEL_ROOT` — see
`../../models/README.md`.
