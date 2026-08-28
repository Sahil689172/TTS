# Phase 1 — Exit Report

**Date:** 2026-08-29
**Phase:** 1 — Existing System Audit + Normalization Foundation
**Source of truth:** `docs/PHASE_0_REQUIREMENTS_FREEZE.md` (unmodified)

---

## 1. Headline

Phase 1 set out to audit an existing English/Tamil TTS system. **No such system
exists.** The repository contained exactly one file — the Phase 0 contract.

Phase 1 therefore did the work that was actually possible without fabricating
evidence:

- audited and documented the true repository and environment state, including
  **two corrections** to stated facts (disk layout, and the empty repository);
- built and tested the **normalization foundation** (Phase 0 §16), the one
  Phase 1 deliverable that never depended on a model;
- froze test-set **structure** for normalization and the golden language sets;
- produced a **licence-aware download manifest** with nothing downloaded;
- produced **evidence-based Phase 2 requirements**.

Every model-dependent step is reported as **BLOCKED**, not as passed.

## 2. Findings

| # | Finding | Severity |
|---|---|---|
| **F-01** | The repository contained no TTS implementation, code, weights, config, tokenizer, dataset, test or dependency file. Only `docs/PHASE_0_REQUIREMENTS_FREEZE.md`. | **Critical — invalidates the Phase 1 premise** |
| **F-02** | Stated storage "954 GB total / 494 GB free" is the **sum of two drives**. The project drive **C: has 16.4 GB free**; the 475 GB is on **D:**. | **High — changes where models may be stored** |
| **F-03** | The repository is inside **OneDrive**. Weights written into it would be sync-uploaded. | **High** |
| **F-04** | All five Phase 0 **blocking** exit gates (G-00, G-03, G-18, G-19, G-20) are still open; no git tags exist. | **High — process deviation** |
| **F-05** | Only **2.60 GB of 15.68 GB RAM** was free at measurement (83 % load). | Medium |
| **F-06** | System interpreter is **Python 3.13.4**, ahead of many TTS stacks' support. | Medium |
| **F-07** | Phase 0 §17's machine-readable registers and CI validators were never created, so "CI fails on an unassigned requirement" is unenforced. | Medium |
| **F-08** | Frontend latency is **0.837 ms p99** — Phase 0 conflict C-11 is not currently a risk. | Positive |
| **F-09** | Tamil verbalization is **unvalidated by any native speaker**. | **High — quality risk** |
| **F-10** | Frozen test sets fall short of Phase 0 §8.2 and §9 count floors. | Medium |

## 3. Blockers

| ID | Blocker | Blocks | Owner |
|---|---|---|---|
| **B-01** | No TTS model exists or is referenced | Steps 3, 4, 7, 9, 10, 12 (TTS part), 13, 14, 15, 18 (model side) | **User** — supply the real repo, or confirm greenfield |
| **B-02** | No dependency declaration or lockfile | reproducibility (Phase 0 §12) | Phase 2 |
| **B-03** | Phase 0 **Q-01** (latency metric) unanswered | Phase 2 selection target | **User** |
| **B-04** | Phase 0 **Q-02** (audio/telephony contract) unanswered | validity of all quality work (R-13/R-16) | **User** |
| **B-05** | No native Tamil speaker has validated any Tamil output | Tamil quality claims | **User** |
| **B-06** | No GPU environment | Phase 0 HC-8, HC-9 | **User** |

## 4. Phase 1 exit criteria — measured status

| # | Criterion | Status |
|---|---|---|
| 1 | Repository audited | **PASS** — `repository_audit.md` |
| 2 | Phase 0 consumed | **PASS** — `phase0_consumption.md` |
| 3 | Existing English system identified | **PASS (negative result)** — none exists, documented |
| 4 | Existing Tamil system identified | **PASS (negative result)** — none exists |
| 5 | Model sources documented | **PASS (vacuous)** — inventory empty |
| 6 | Licences documented | **PARTIAL** — no models to license; GPL/Indic-corpus risks flagged |
| 7 | Hardware requirements documented | **PASS** — `environment.md` |
| 8 | Download requirements documented | **PASS** — `download_manifest.md` |
| 9 | No unnecessary large downloads | **PASS** — zero bytes downloaded, zero packages installed |
| 10 | Reproducibility status documented | **PASS** — `reproducibility_audit.md` |
| 11 | English baseline or blocker documented | **BLOCKER DOCUMENTED** (B-01) |
| 12 | Tamil baseline or blocker documented | **BLOCKER DOCUMENTED** (B-01) |
| 13 | Dev-machine performance measured where feasible | **PASS** — frontend only, clearly labelled |
| 14 | Quality evaluation established | **NOT ESTABLISHED** — no audio, no eval models, no humans |
| 15 | Architecture documented | **PARTIAL** — frontend documented; no model to reverse-engineer |
| 16 | Speaker representation documented | **BLOCKED** — plus Phase 0 Q-09/Q-11 unanswered |
| 17 | Normalization foundation implemented | **PASS** — `src/tnorm/`, 11 modules |
| 18 | Normalization automated tests implemented | **PASS** — 104 pass, 4 xfail |
| 19 | Normalization failures documented | **PASS** — 4 xfail + §4 gaps, nothing hidden |
| 20 | Training/inference mismatch documented | **PARTIAL** — our side documented; model side UNKNOWN |
| 21 | Mixed-language limitations documented | **PASS** — `normalization_audit.md` §4.3 |
| 22 | Tanglish implications documented | **PASS** — `tanglish_implications.md` |
| 23 | Phase 2 requirements produced | **PASS** — `phase2_requirements.md` |
| 24 | Tests pass | **PASS** — 104 passed, 4 xfailed, 0.45 s |
| 25 | Git status clean or changes documented | **PASS** — all changes new and enumerated |
| 26 | Phase 1 exit report created | **PASS** — this document |

**Score: 18 PASS · 4 PARTIAL · 3 BLOCKED/NOT ESTABLISHED · 1 vacuous PASS.**

Criteria 11, 12, 14 and 16 are **not** satisfied. They are blocked by B-01,
which is outside Phase 1's control.

## 5. Files created

```
.gitignore                                    new
pytest.ini                                    new
src/tnorm/__init__.py                         new
src/tnorm/types.py                            new
src/tnorm/scripts.py                          new
src/tnorm/langid.py                           new
src/tnorm/tokenizer.py                        new
src/tnorm/entities.py                         new
src/tnorm/numbers_en.py                       new
src/tnorm/numbers_ta.py                       new
src/tnorm/verbalizer.py                       new
src/tnorm/pipeline.py                         new
src/tnorm/lexicons/__init__.py                new
tests/test_units.py                           new
tests/test_normalization_cases.py             new
data/testsets/normalization_cases.yaml        new
data/testsets/golden_seed.yaml                new
scripts/bench_frontend.py                     new
models/README.md                              new
models/manifest.yaml                          new
docs/phase1/README.md                         new
docs/phase1/phase0_consumption.md             new
docs/phase1/repository_audit.md               new
docs/phase1/environment.md                    new
docs/phase1/model_inventory.md                new
docs/phase1/download_manifest.md              new
docs/phase1/reproducibility_audit.md          new
docs/phase1/architecture_audit.md             new
docs/phase1/speaker_audit.md                  new
docs/phase1/normalization_audit.md            new
docs/phase1/baseline_results.md               new
docs/phase1/tanglish_implications.md          new
docs/phase1/phase2_requirements.md            new
docs/phase1/phase1_exit_report.md             new
artifacts/frontend_bench.json                 new (gitignored)
```

**Files modified: none.** `docs/PHASE_0_REQUIREMENTS_FREEZE.md` is untouched.
**Files deleted: none.**

## 6. Risks added to the Phase 0 register

| ID | Risk | P | I | Detection | Mitigation |
|---|---|---|---|---|---|
| **R-23** | Project premise mismatch — work planned against systems that do not exist | H | H | this audit | resolve B-01 before Phase 2 |
| **R-24** | C: drive exhaustion (16.4 GB free) / OneDrive sync of weights | M | H | disk check before download | `TTS_MODEL_ROOT=D:\tts-models`; `.gitignore` |
| **R-25** | Python 3.13 incompatible with chosen TTS stack | M | M | first install attempt | pinned venv; be ready to downgrade Python |
| **R-26** | Tamil normalization is wrong in ways no one has checked | **H** | **H** | native-speaker review | action A-04; all Tamil output currently warning-flagged |
| **R-27** | TA-Latin language ID accuracy unmeasured | H | M | build a labelled TA-Latin set | expand lexicon; measure before relying on it |

## 7. Recommendation

Do **not** start Phase 2 model downloads until **B-01, B-03 (Q-01) and B-04
(Q-02)** are resolved. Q-02 in particular determines whether any quality
measurement taken in Phase 2 is meaningful at all.

The normalization foundation is usable now and is independent of every one of
those decisions.
