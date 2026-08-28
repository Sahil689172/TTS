# Phase 1 — Baseline Results

**Date:** 2026-08-29
**Covers:** Phase 1 Steps 9 (English baseline), 10 (Tamil baseline),
12 (performance baseline), 13 (quality baseline).

> **LABEL FOR EVERYTHING IN THIS DOCUMENT: DEVELOPMENT MACHINE BASELINE.**
> This machine has no dedicated NVIDIA GPU. Nothing here represents, predicts or
> substitutes for production performance. Phase 0 HC-8 (p99 ≤ 500 ms) and HC-9
> (15–20 sustainable concurrency) **must** be benchmarked later on appropriate
> GPU hardware.

---

## 1. English TTS baseline (Step 9) — BLOCKED

> **Status: BLOCKED — blocker B-01. No audio was generated.**

**Reason:** no English TTS model exists in the repository, none is referenced,
and no weights are present (`model_inventory.md`). Phase 1 did not download one,
per the audit-before-download rule and because model selection is Phase 2 work.

Per Phase 1's instruction — *"If it cannot: document why and DO NOT force it"* —
no substitute was fabricated. Specifically, **no** inference time, audio
duration, output path or quality figure is reported for English, because none
was measured.

**What was delivered instead:** the frozen English baseline *text* set
(`data/testsets/golden_seed.yaml`, section `english`), covering the categories
Step 9 requires — conversational, short, medium, long, numbers, dates, times,
phone numbers, OTP, booking IDs, prices, addresses, names, vehicle terminology,
abbreviations. It is ready to drive audio generation the moment a model exists.

| Step 9 field | Value |
|---|---|
| Input text | **available** (15 seed items) |
| Normalized text | **available** — produced by `tnorm`, verified |
| Model | **NONE** |
| Inference time | **NOT MEASURED** |
| Audio duration | **NOT MEASURED** |
| Errors | **N/A** |
| Output path | **N/A — no audio produced** |

## 2. Tamil TTS baseline (Step 10) — BLOCKED

> **Status: BLOCKED — blocker B-01.** Identical reason and identical honesty.

Frozen Tamil baseline text set delivered (`golden_seed.yaml`, section `tamil`),
covering normal and conversational Tamil, transportation terminology, numbers,
times, formal/colloquial register pairs, retroflex and trill contrast pairs, and
loanwords already naturalized into Tamil.

Mixed-language input was **not forced** onto any system, as instructed — there
is no system to force it onto.

## 3. Mixed-text / Tanglish baseline (Step 11)

TTS-side: **BLOCKED** (no model).
Frontend-side: **PERFORMED AND MEASURED** — see `normalization_audit.md` §2.2.

The Step 11 example sentences were all processed successfully by the frontend,
with correct matrix-language detection and correct code-mix flags. Failures at
the frontend level are catalogued in `normalization_audit.md` §4.

## 4. Performance baseline (Step 12) — FRONTEND ONLY

Phase 0 §6.6 puts text normalization **inside** the user-perceived latency
budget and forbids excluding it from measurement. So although no TTS model
exists, the frontend's contribution to the budget is real and measurable — and
Phase 0 conflict C-11 explicitly flags it as a risk to the 500 ms target.

**Command:** `python scripts/bench_frontend.py --iterations 300`
**Artifact:** `artifacts/frontend_bench.json` (gitignored)

### 4.1 Environment (Phase 0 §12 record)

| Field | Value |
|---|---|
| OS | Windows-11-10.0.26200-SP0 |
| CPU | Intel64 Family 6 Model 154 (Alder Lake-P; i7-1255U) |
| Logical cores | 12 |
| Python | 3.13.4 |
| torch | 2.11.0+cpu |
| CUDA available | **False** |

### 4.2 Measured results — normalization frontend

Workload mirrors the Phase 0 §6.2 corpus composition (EN 35 % / TA 35 % /
TG 30 %, 30 % entity-heavy). Warm-up discarded per PERF-14.

| Metric | Value |
|---|---|
| Requests measured | 5,400 |
| Warm-up | 20 iterations, discarded |
| Mean | 0.281 ms |
| **p50** | **0.222 ms** |
| **p95** | **0.613 ms** |
| **p99** | **0.837 ms** |
| Max | 2.152 ms |
| Throughput | 3,551 req/s (single process, single thread) |
| Error rate | **0.0** |

Per stratum:

| Stratum | n | p50 (ms) | p95 (ms) | p99 (ms) |
|---|---|---|---|---|
| en / entity-heavy | 900 | 0.406 | 0.744 | 1.004 |
| en / plain | 1200 | 0.212 | 0.668 | 1.132 |
| ta / entity-heavy | 600 | 0.246 | 0.430 | 0.649 |
| ta / plain | 900 | 0.177 | 0.331 | 0.502 |
| tg / entity-heavy | 900 | 0.249 | 0.411 | 0.626 |
| tg / plain | 900 | 0.168 | 0.324 | 0.483 |

### 4.3 Interpretation — and its limits

**Finding:** the frontend consumes **≈0.84 ms at p99**, about **0.17 %** of the
500 ms budget in Phase 0 PERF-01. Entity-heavy English is the most expensive
stratum (~1.0 ms p99) but remains negligible.

**Phase 0 conflict C-11 is, on this evidence, not currently a risk** — provided
normalization stays rule-based. If Phase 2 introduces a *learned* entity
disambiguator (an option Phase 0 Q-12 leaves open), this measurement must be
repeated; a model-based frontend would be orders of magnitude more expensive.

**What this is NOT:**

- **Not** a Phase 0 §6 benchmark result. Phase 0 requires n ≥ 1,000 per
  concurrency level, 3 repetitions, a 300 s window and a concurrency sweep over
  {1,5,10,15,20}. This is a single-process micro-benchmark.
- **Not** TTFA, E2E latency, RTF or throughput of a TTS system. Those need a
  model.
- **Not** transferable to production hardware.

### 4.4 Concurrency (Step 12) — NOT RUN, deliberately

Step 12 asks for 1 / 5 / 10 concurrency. **Not run**, because Phase 0 §7 defines
concurrency over a *TTS service* with think-time, queueing, batching and
resource saturation. None of that exists. Running "5 concurrent" against a
0.2 ms pure-Python function would produce a number with no relationship to the
requirement, which Phase 0 §19 explicitly warns against ("benchmark
self-deception", risk R-18).

**Cold start vs warm inference:** the harness discards a warm-up phase and
reports steady state. A meaningful cold-start measurement (`T_load`,
`T_first_request`, `T_to_steady`) requires model loading — the dominant term —
so it is deferred with the rest.

## 5. Quality baseline (Step 13) — NOT ESTABLISHED

> **Status: BLOCKED. No quality metric was computed. No MOS was fabricated.**

| Phase 0 metric | Status | Blocker |
|---|---|---|
| O-01 WER | **NOT MEASURED** | no synthesized audio; no ASR model present |
| O-02 CER | **NOT MEASURED** | same |
| O-03 pronunciation accuracy (entity exactness) | **PARTIALLY ESTABLISHED at the TEXT level** — the exact-match suite passes (`normalization_audit.md` §2.1). **NOT established acoustically**, which is what the metric ultimately means | no audio |
| O-04 intelligibility | **NOT MEASURED** | no audio |
| O-05 speaker similarity | **NOT MEASURED** | no audio, no speaker encoder |
| O-06 code-switch quality | **NOT MEASURED** | no audio, no LID model |
| H-01…H-10 human evaluation | **NOT PERFORMED** | no audio to rate; **no human has evaluated anything in this project** |

Phase 1 makes **no claim** of human-evaluated quality, per the explicit
instruction. The Phase 0 §5.2 protocol exists on paper; the operational
artifacts it requires (rater instructions in English and Tamil, the frozen
anchor set, trap items, the rating form schema) **have not been created** — they
are Phase 0 gate items G-05, still open.

## 6. Summary table

| Baseline | Status | Evidence |
|---|---|---|
| English TTS | **BLOCKED** (B-01) | no model |
| Tamil TTS | **BLOCKED** (B-01) | no model |
| Tanglish TTS | **BLOCKED** (B-01) | no model |
| Normalization frontend — function | **ESTABLISHED** | 104 tests pass, 4 xfail |
| Normalization frontend — latency | **ESTABLISHED** | p99 0.837 ms, n=5,400 |
| TTS latency / TTFA / RTF | **NOT MEASURED** | no model |
| Concurrency | **NOT RUN** (deliberate) | no service |
| Objective quality | **NOT MEASURED** | no audio, no eval models |
| Human quality | **NOT PERFORMED** | no audio, no rater materials |
