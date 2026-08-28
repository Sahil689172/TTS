# Phase 0 — Requirements Freeze, Evaluation Framework & Project Contract

**Project:** Self-hosted Text-to-Speech for a real-time transportation/taxi voice-agent & contact-center system
**Languages:** English · Tamil · Tamil–English code-mixed (Tanglish)
**Phase:** 0 (Requirements + Evaluation Framework) — **no implementation, no model selection, no architecture commitment**
**Document status:** Draft for freeze
**Date:** 2026-08-28

---

## 0. Provenance & source-of-truth note

The referenced problem-statement document was **not found**. The working directory (`c:\Users\hp\OneDrive\Desktop\TTS`), the session scratchpad, the memory store and the Desktop tree were all searched; no TTS/Tanglish/taxi-related document exists on disk and none was attached to the conversation.

This document therefore treats **the project brief as stated in the originating request** as the problem statement of record, referred to throughout as **`PS`**, with section anchors such as `PS§LANGUAGE`, `PS§PERFORMANCE`.

> **Phase 0 is not truly frozen until a delta pass reconciles this extraction against the real problem-statement document, if one exists.** Tracked as exit-gate item `G-00` (blocking).

### Labelling convention (RULE 5)

| Label | Meaning |
|---|---|
| **[S]** | Source requirement — explicitly stated in `PS` |
| **[S-implied]** | Directly entailed by an explicit `PS` statement |
| **[ED]** | Engineering decision / project decision |
| **[RR]** | Research recommendation |
| **[A]** | Assumption — not in `PS`, must be confirmed |

`TBE` = *Threshold to be established during Phase 0/benchmark design* — used wherever `PS` gives no number. **No numeric threshold has been invented** (RULE 4).

---

## 1. Executive Summary

You are building a self-hosted, real-time, multilingual TTS engine for a taxi contact-center voice agent, covering English, Tamil, and Tamil–English code-mixed speech (Tanglish), where Tanglish is the research contribution and English+Tamil is the engineering foundation.

Phase 0's job is to convert `PS` into a **contract**: 84 numbered requirements, 12 hard constraints, a frozen evaluation protocol, a frozen benchmark methodology, a frozen normalization test taxonomy, and a traceability matrix in which no requirement is unassigned.

Four findings dominate this phase:

1. **The single most important ambiguity is `PERF-01`.** `PS§PERFORMANCE` says "p99 latency ≤ 500 ms" without saying *latency of what*. If it means end-to-end synthesis of a complete utterance, it is unachievable for long utterances by any architecture, self-hosted or not — a 12-second announcement cannot be fully synthesized in 500 ms at 15–20 concurrency on low-cost hardware. If it means **time-to-first-audio (TTFA)**, it is demanding but reasonable. Phase 0 must not guess. Both interpretations are specified below; TTFA-as-primary is recommended; it is the #1 blocking clarification (`Q-01`).

2. **`PS` never states the audio delivery format, and for a contact-center system this is decisive.** Telephony is typically 8 kHz narrowband. If the model is trained, evaluated and MOS-scored at 22/24 kHz and then deployed down-sampled to 8 kHz μ-law, every quality number collected is measuring something the customer never hears. This is the largest silent risk in the plan (`R-16`, `Q-02`).

3. **RULE 9 has a concrete failure mode with a name: the symbol inventory.** The thing most likely to make Tanglish impossible in Phase 8 is a decision made casually in Phase 3 — the text-token/phoneme vocabulary, the script normalization policy, and the speaker representation. Phase 0 therefore freezes a *constraint on* those choices (`CX-06`, `MR-05`) without freezing the choices themselves.

4. **ASR-based WER/CER is a weak objective metric for Tamil and a near-invalid one for Tanglish.** Tamil ASR error rates are high enough that a TTS-WER number conflates synthesis failure with recognition failure; for Latin-script Tanglish there is no canonical orthography to score against at all. WER/CER are specified as **relative regression tripwires with a fixed, version-pinned ASR**, never as absolute quality claims; absolute intelligibility is routed to human transcription on a subset.

Nothing about model, architecture, vocoder, tokenizer, or hardware is decided here (RULES 2–3).

---

## 2. Requirements Table

**M** = mandatory, **O** = optional/desirable. **Source** cites `PS` sections. **Verification** names the artifact/phase that proves it.

### A. Functional Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| FR-01 | Synthesize intelligible speech from text for a transportation/taxi voice agent | `PS§PROBLEM CONTEXT` [S] | M | Golden test set §9 synthesized end-to-end; human intelligibility ≥ threshold |
| FR-02 | Cover the taxi-booking use case | `PS§PROBLEM CONTEXT` [S] | M | Domain coverage audit of golden set; ≥1 scenario family per use case |
| FR-03 | Cover ride-status use case | `PS§PROBLEM CONTEXT` [S] | M | as FR-02 |
| FR-04 | Cover cancellation use case | `PS§PROBLEM CONTEXT` [S] | M | as FR-02 |
| FR-05 | Cover driver-coordination use case | `PS§PROBLEM CONTEXT` [S] | M | as FR-02 |
| FR-06 | Cover customer-support use case | `PS§PROBLEM CONTEXT` [S] | M | as FR-02 |
| FR-07 | Mixed-language input must be rendered as **one naturally produced utterance**, not by stitching separately generated Tamil and English audio | `PS§LANGUAGE` ("rather than simply stitching") [S] | M | Architecture review gate (Phase 2) + human code-switch-boundary listening test §5.2 |
| FR-08 | System must be suitable for integration into a real-time voice agent | `PS§PROBLEM CONTEXT`, `PS§Phase 10` [S] | M | Phase 10 integration acceptance run |
| FR-09 | System must be self-hosted end-to-end for speech generation | `PS§PROJECT CONSTRAINT` [S] | M | Dependency audit §13; network-egress test during synthesis |
| FR-10 | Expose a stable synthesis API contract (text in → audio out) used identically by the benchmark harness and the voice agent | [ED] | M | Same client used in Phase 5/6 benchmarks and Phase 10 integration |
| FR-11 | Support mid-utterance cancellation / barge-in | [A] — implied by "real-time voice agent" but **not stated in PS** | O→M pending `Q-04` | Cancellation latency measured in §6.8 |

### B. Language Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| LR-01 | English speech synthesis | `PS§LANGUAGE` [S] | M | English golden set §9.1 |
| LR-02 | Tamil speech synthesis | `PS§LANGUAGE` [S] | M | Tamil golden set §9.2 |
| LR-03 | Tamil–English code-mixed (Tanglish) synthesis | `PS§LANGUAGE` [S] | M | Tanglish golden set §9.3 |
| LR-04 | Handle Tamil-script sentences with embedded Latin-script English (`உங்கள் pickup location எங்கே?`) | `PS§LANGUAGE` example [S] | M | Golden subset TG-A |
| LR-05 | Handle Tamil written in Latin script (`unga pickup location enga?`) | `PS§LANGUAGE` example [S] | M | Golden subset TG-B |
| LR-06 | Handle Tamil grammatical suffixes attached to English tokens (`Chennai Central-ல`) | `PS§LANGUAGE` example [S] | M | Golden subset TG-C; normalization case N-15 |
| LR-07 | Handle English embedded in Tamil as a general phenomenon | `PS§CONTEXT-AWARE PRONUNCIATION` [S] | M | Golden subsets TG-A/TG-C |
| LR-08 | Regional pronunciation must be handled | `PS§PROBLEM CONTEXT` [S] | M | Human eval axis H-09 (regional naturalness) |
| LR-09 | Tanglish is the primary research contribution and major research challenge | `PS§LANGUAGE`, `PS` preamble [S] | M | Stage 2 research deliverables; Phase 8 |
| LR-10 | English + Tamil foundation must be built **before** Tanglish extension | `PS§PROJECT STRATEGY` Stage 1→2 [S] | M | Phase ordering; Phase 6 MVP gate precedes Phase 7 |
| LR-11 | Final system must be a **unified** Tamil + English + Tanglish system | `PS§Phase 9`, Stage 3 [S] | M | Phase 9 acceptance: one deployed system serves all three golden sets |

### C. Pronunciation & Normalization Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| PN-01 | Numbers rendered correctly | `PS§CONTEXT-AWARE` [S] | M | §8 category N1 |
| PN-02 | Dates rendered correctly | `PS§CONTEXT-AWARE` [S] | M | §8 N2 |
| PN-03 | Times rendered naturally (`7:30 PM`) | `PS§CONTEXT-AWARE` explicit example [S] | M | §8 N3 |
| PN-04 | Phone numbers rendered **digit-by-digit** | `PS§CONTEXT-AWARE` explicit [S] | M | §8 N4 — exact-match |
| PN-05 | OTPs rendered digit-by-digit (`4821` → "four eight two one") | `PS§CONTEXT-AWARE` explicit [S] | M | §8 N5 — exact-match |
| PN-06 | Booking IDs rendered as character/digit sequence, **not** as a normal number (`TN45AB1234`) | `PS§CONTEXT-AWARE` explicit [S] | M | §8 N6 — exact-match |
| PN-07 | Addresses rendered correctly | `PS§CONTEXT-AWARE` [S] | M | §8 N7 |
| PN-08 | Abbreviations rendered correctly | `PS§CONTEXT-AWARE` [S] | M | §8 N8 |
| PN-09 | Vehicle names/types rendered correctly | `PS§CONTEXT-AWARE` [S] | M | §8 N9 |
| PN-10 | Prices rendered correctly | `PS§PROBLEM CONTEXT` [S] | M | §8 N10 |
| PN-11 | Distances rendered correctly | `PS§PROBLEM CONTEXT` [S] | M | §8 N11 |
| PN-12 | Person names rendered correctly | `PS§PROBLEM CONTEXT` [S] | M | §8 N12 |
| PN-13 | Locations rendered correctly | `PS§PROBLEM CONTEXT` [S] | M | §8 N13 |
| PN-14 | The **same digit string must be rendered differently depending on context** | `PS§CONTEXT-AWARE` (section premise) [S] | M | §8 ambiguity suite N-AMB — minimal pairs |
| PN-15 | Normalization must operate on Tamil+English mixed text | `PS§CONTEXT-AWARE` [S] | M | §8 N14 |
| PN-16 | Normalization must operate on Tamil written in Latin characters | `PS§CONTEXT-AWARE` [S] | M | §8 N15 |
| PN-17 | Normalization output representation must be language-neutral enough to serve English, Tamil and Tanglish from one engine | [ED] | M | Phase 1 design review; single engine passes all three suites |
| PN-18 | Every normalization rule must be traceable to a frozen test case with an expected output string | [ED] | M | 1:1 coverage report rule↔test |

### D. Data Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| DR-01 | Tamil training/adaptation data must be obtained | LR-02 + `PS§Phase 3` [S-implied] | M | Dataset registry §13 |
| DR-02 | A Tanglish dataset must be built (dataset + linguistic foundation) | `PS§Phase 7` explicit [S] | M | Phase 7 deliverable; dataset card |
| DR-03 | Datasets may be used only where licenses permit the intended use | `PS§PROJECT CONSTRAINT` [S] | M | License matrix §13, per-dataset sign-off |
| DR-04 | Data must cover transportation/taxi domain vocabulary | `PS§PROBLEM CONTEXT` [S-implied] | M | Domain term coverage report |
| DR-05 | Every dataset must carry a dataset card recording the fields in §13 | [ED] | M | Registry completeness check |
| DR-06 | Synthetic/model-generated training data must be flagged, and never sourced from a prohibited third-party TTS API | [ED] from CX-01 | M | Provenance field mandatory; audit |
| DR-07 | Golden/eval sets must be **speaker- and text-disjoint** from training data | [ED] | M | Overlap check script, reported per model version |
| DR-08 | Golden test sets are frozen and version-controlled; additions create a new version, never mutate v1 | [ED] | M | Git tag per golden-set version |

### E. Model Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| MR-01 | Models must be self-hostable | `PS§PROJECT CONSTRAINT` [S] | M | Runs with no external inference call |
| MR-02 | Open-source models permitted where license allows the intended use | `PS§PROJECT CONSTRAINT` [S] | M | License matrix §13 |
| MR-03 | Model must not be selected in Phase 0 | `PS§RULE 2` [S] | M | Phase 0 output contains no model choice |
| MR-04 | No architecture assumed correct in Phase 0 | `PS§RULE 3` [S] | M | Phase 0 output contains no architecture choice |
| MR-05 | Architecture chosen for English+Tamil must **not preclude** Tanglish later | `PS§RULE 9` [S] | M | Phase 2 architecture gate includes an explicit Tanglish-feasibility argument |
| MR-06 | Speaker consistency must be maintained | `PS§QUALITY` [S] | M | Objective O-05 + human H-08 |
| MR-07 | Tanglish adaptation must not regress English/Tamil | `PS§Phase 9` + `PS§9` [S-implied] | M | Regression suite §10, release-blocking |

### F. Inference Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| IR-01 | Streaming inference must be implemented | `PS§Phase 5` explicit [S] | M | Streaming benchmark path §6; TTFA measurable |
| IR-02 | Inference must be real-time capable | `PS§PROBLEM CONTEXT` [S] | M | RTF and TTFA at target concurrency |
| IR-03 | Optimization pass required before MVP | `PS§Phase 6` [S] | M | Before/after benchmark on identical protocol |
| IR-04 | Speech generation pipeline must remain self-hosted even if external tools are used for research/reference | `PS§PROJECT CONSTRAINT` [S] | M | Egress audit during synthesis |
| IR-05 | Support incremental/partial text input if the upstream agent streams LLM text | [A] — not in `PS`; `Q-05` | O | Deferred |

### G. Performance Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| PERF-01 | p99 latency ≤ ~500 ms | `PS§PERFORMANCE` [S] — **metric subject ambiguous, see `Q-01`** | M | §6 benchmark at defined concurrency |
| PERF-02 | Measure TTFA | `PS§PERFORMANCE` [S] | M | §6 F-1 |
| PERF-03 | Measure p50 latency | `PS§PERFORMANCE` [S] | M | §6 F-6 |
| PERF-04 | Measure p95 latency | `PS§PERFORMANCE` [S] | M | §6 F-6 |
| PERF-05 | Measure p99 latency | `PS§PERFORMANCE` [S] | M | §6 F-6 |
| PERF-06 | Measure end-to-end latency | `PS§PERFORMANCE` [S] | M | §6 F-2 |
| PERF-07 | Measure throughput | `PS§PERFORMANCE` [S] | M | §6 F-4 |
| PERF-08 | Measure requests/second | `PS§PERFORMANCE` [S] | M | §6 F-3 |
| PERF-09 | Measure GPU utilization | `PS§PERFORMANCE` [S] | M | §6 sampler, 1 Hz |
| PERF-10 | Measure CPU utilization | `PS§PERFORMANCE` [S] | M | §6 sampler |
| PERF-11 | Measure VRAM | `PS§PERFORMANCE` [S] | M | §6 sampler, peak + steady |
| PERF-12 | Measure RAM | `PS§PERFORMANCE` [S] | M | §6 sampler, RSS peak + steady |
| PERF-13 | Measure error rate | `PS§PERFORMANCE` [S] | M | §6 F-7 |
| PERF-14 | Benchmarks must exclude model-loading time from steady-state latency | `PS§5` explicit [S] | M | Harness design; warm-up discard |
| PERF-15 | Cold-start must be measured separately | `PS§5` [S] | M | Cold-start protocol §6.7 |

### H. Concurrency Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| CC-01 | Target ~15–20 concurrent requests | `PS§PERFORMANCE` [S] | M | §7 sustainable-concurrency test |
| CC-02 | "20 concurrent" must **not** mean 20 simultaneous requests once | `PS§PERFORMANCE` explicit [S] | M | §7 definition; sustained-load protocol |
| CC-03 | A reproducible definition of sustainable concurrency must exist | `PS§PERFORMANCE` explicit [S] | M | §7 definition frozen in Phase 0 |
| CC-04 | Benchmark at concurrency levels 1, 5, 10, 15, 20 | `PS§5` explicit [S] | M | §6 sweep |
| CC-05 | Pass condition must combine latency + error rate + resource saturation, not request count | `PS§6` explicit [S] | M | §7 PASS predicate |

### I. Cost Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| CO-01 | Infrastructure cost should be as low as possible | `PS§COST` [S] | M (directional) | §11 comparative cost report per config |
| CO-02 | Compute infrastructure cost/hour | `PS§COST` [S] | M | §11 C-1 |
| CO-03 | Compute audio minutes generated/hour | `PS§COST` [S] | M | §11 C-2 |
| CO-04 | Compute cost/minute of audio | `PS§COST` [S] | M | §11 C-3 |
| CO-05 | Compute cost at different concurrency levels | `PS§COST` [S] | M | §11 C-7 |
| CO-06 | Report hardware utilization | `PS§COST` [S] | M | §11 C-4/C-5 |
| CO-07 | Cost methodology must permit fair comparison across models and optimizations | `PS§10` explicit [S] | M | Identical workload + environment record §12 |

### J. Evaluation Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| EV-01 | Objective: WER | `PS§QUALITY` [S] | M | §5.1 O-01 |
| EV-02 | Objective: CER | `PS§QUALITY` [S] | M | §5.1 O-02 |
| EV-03 | Objective: pronunciation accuracy | `PS§QUALITY` [S] | M | §5.1 O-03 |
| EV-04 | Objective: intelligibility | `PS§QUALITY` [S] | M | §5.1 O-04 |
| EV-05 | Objective: speaker similarity | `PS§QUALITY` [S] | M | §5.1 O-05 |
| EV-06 | Objective: code-switching quality | `PS§QUALITY` [S] | M | §5.1 O-06 |
| EV-07 | Human: MOS | `PS§QUALITY` [S] | M | §5.2 H-01 |
| EV-08 | Human: naturalness | `PS§QUALITY` [S] | M | §5.2 H-02 |
| EV-09 | Human: intelligibility | `PS§QUALITY` [S] | M | §5.2 H-03 |
| EV-10 | Human: Tamil pronunciation | `PS§QUALITY` [S] | M | §5.2 H-04 |
| EV-11 | Human: English pronunciation | `PS§QUALITY` [S] | M | §5.2 H-05 |
| EV-12 | Human: Tanglish / code-switching quality | `PS§QUALITY` [S] | M | §5.2 H-06 |
| EV-13 | Human: prosody | `PS§QUALITY` [S] | M | §5.2 H-07 |
| EV-14 | Human: speaker consistency | `PS§QUALITY` [S] | M | §5.2 H-08 |
| EV-15 | Human: regional naturalness | `PS§QUALITY` [S] | M | §5.2 H-09 |
| EV-16 | Evaluation protocol must be reproducible | `PS§4` explicit [S] | M | Protocol doc + fixed seeds/sample lists |
| EV-17 | Objective metrics must use a **version-pinned** ASR/speaker/LID model, never swapped mid-project | [ED] | M | Environment record §12 |

### K. Deployment Requirements

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| DP-01 | Self-hosted deployment | `PS§PROJECT CONSTRAINT` [S] | M | Deployment audit |
| DP-02 | Voice-agent integration | `PS§Phase 10` [S] | M | Phase 10 integration test |
| DP-03 | Production-oriented unified system (Stage 3) | `PS§PROJECT STRATEGY` [S] | M | Phase 9/10 acceptance |
| DP-04 | Audio output format, sample rate and codec must be specified and held constant across eval and production | [ED] — **not in `PS`**, `Q-02` | M | §12 environment record |

### L. Deliverables

| ID | Requirement | Source | M/O | Verification |
|---|---|---|---|---|
| DL-01 | Phase 0 requirements + evaluation framework documents | `PS§Phase 0`, `PS§16` [S] | M | §17 deliverable list exists |
| DL-02 | English+Tamil MVP | `PS§Phase 6` [S] | M | Phase 6 gate |
| DL-03 | Tanglish dataset + linguistic foundation | `PS§Phase 7` [S] | M | Phase 7 gate |
| DL-04 | Unified Tamil+English+Tanglish system | `PS§Phase 9` [S] | M | Phase 9 gate |
| DL-05 | Final benchmark | `PS§Phase 10` [S] | M | Phase 10 report |
| DL-06 | Voice agent integration | `PS§Phase 10` [S] | M | Phase 10 |
| DL-07 | Open-source release | `PS§Phase 10` [S] | M | Release artifacts + license review |
| DL-08 | Every later phase traceable back to Phase 0 | `PS§RULE 6` [S] | M | §14 matrix maintained per phase |

### M. Constraints

| ID | Constraint | Source | M/O | Verification |
|---|---|---|---|---|
| CX-01 | No third-party commercial TTS API in the speech-generation path | `PS§PROJECT CONSTRAINT`, `RULE 7` [S] | M | Dependency + egress audit each release |
| CX-02 | Specifically excluded: ElevenLabs, Google Cloud TTS, Azure TTS, Amazon Polly, OpenAI TTS, any other hosted TTS API | `PS§PROJECT CONSTRAINT` [S] | M | Blocklist check in CI |
| CX-03 | No third-party TTS API may become a **hidden** dependency (incl. transitively or via training data) | `PS§RULE 8` [S] | M | Provenance audit DR-06 |
| CX-04 | Open-source assets usable only within license terms | `PS§PROJECT CONSTRAINT` [S] | M | §13 matrix |
| CX-05 | Do not optimize a benchmark number at the cost of natural speech quality | `PS§RULE 10` [S] | M | Every perf change re-runs quality regression §10; both must pass |
| CX-06 | English/Tamil architecture must not make Tanglish impossible later | `PS§RULE 9` [S] | M | Phase 2 gate argument; §15 C-06 |
| CX-07 | Mixed-language output must not be produced by concatenating separately generated audio | `PS§LANGUAGE` [S] | M | Architecture review + boundary listening test |
| CX-08 | Do not invent requirements absent from the problem statement | `PS§RULE 4` [S] | M | Every row cites a source or is labelled derived |
| CX-09 | Source requirement / engineering decision / research recommendation / assumption must remain distinguished | `PS§RULE 5` [S] | M | Label present on every non-source item |
| CX-10 | No coding in Phase 0 | `PS§RULE 1` [S] | M | Phase 0 output is documents only |
| CX-11 | No final model selection in Phase 0 | `PS§RULE 2` [S] | M | — |
| CX-12 | No architecture assumed correct in Phase 0 | `PS§RULE 3` [S] | M | — |

> **Requirement count: 84.**

---

## 3. Hard Constraints vs Design Preferences

### 3.1 HARD CONSTRAINTS — may never be violated

| # | Hard constraint | Ref | Violation = |
|---|---|---|---|
| HC-1 | Speech generation is fully self-hosted | CX-01, FR-09 | Project failure — non-negotiable |
| HC-2 | No third-party hosted TTS API anywhere in the generation path, including hidden/transitive/data-provenance paths | CX-02, CX-03 | Project failure |
| HC-3 | English synthesis supported | LR-01 | Scope failure |
| HC-4 | Tamil synthesis supported | LR-02 | Scope failure |
| HC-5 | Tanglish synthesis supported, in **both** directions of script mixing | LR-03/04/05 | Scope failure — this is the research contribution |
| HC-6 | Code-mixed output is single-pass generated, never stitched | CX-07, FR-07 | Research contribution void |
| HC-7 | System is streaming and real-time capable | IR-01, IR-02 | Use-case failure |
| HC-8 | Latency target in `PERF-01` met at the defined concurrency (subject to `Q-01`) | PERF-01 | Release blocker |
| HC-9 | Sustainable concurrency of 15–20 under the §7 PASS predicate | CC-01, CC-05 | Release blocker |
| HC-10 | All licenses permit the intended use, including redistribution and derivative models if open-sourcing | CX-04, DL-07 | Legal blocker |
| HC-11 | Naturalness must not be traded away for benchmark numbers | CX-05 | Quality gate blocker |
| HC-12 | Foundation architecture must keep Tanglish reachable | CX-06, MR-05 | Strategic failure |

### 3.2 DESIGN PREFERENCES — strongly desired, negotiable with evidence

| # | Preference | Ref | Why negotiable |
|---|---|---|---|
| DP-a | Minimize infrastructure cost | CO-01 | `PS` says "as low as possible" — directional, no threshold |
| DP-b | A single unified model rather than per-language models + router | LR-11 [interpretation] | `PS` requires a unified *system*; whether that is one model is an open Phase 2 question |
| DP-c | Single consistent voice identity across all three languages | MR-06 | Required as a *metric*; the target level is unset |
| DP-d | GPU-based serving | [A] | `PS` never mandates GPU; CPU-only/hybrid admissible if HC-8/HC-9 hold at lower cost |
| DP-e | Open-source release scope (weights vs code vs data) | DL-07 | `PS` says "Open Source" without scope; constrained by HC-10 |
| DP-f | Specific accent/dialect target within Tamil | LR-08 | "Regional pronunciation" required; *which* region unspecified — `Q-03` |
| DP-g | Phase ordering as listed | `PS§PROJECT STRATEGY` ("tentative phases") | `PS` itself calls them tentative |

**Precedence rule (frozen):** cost (DP-a) is a preference; latency and concurrency (HC-8, HC-9) are constraints — when they collide, cost yields. Conversely **HC-11 outranks HC-8**: if the only way to hit latency is to degrade speech quality below the quality gate, the correct outcome is a hardware or architecture change, not a quality concession.

---

## 4. Success Criteria

`TBE` = threshold to be established. Every `TBE` gets an owner and a setting-method in §17/§18. **21 TBE items total.** None are invented here.

### 4.1 Quality

| Req | Metric | Target | Test method | Pass/Fail rule |
|---|---|---|---|---|
| EV-01 | WER (English) via pinned ASR | **TBE** — set as *relative* delta vs baseline | Synthesize English golden set, ASR-transcribe, WER vs reference | FAIL if WER > baseline + Δ (Δ TBE) |
| EV-01 | WER (Tamil) | **TBE** — relative only; absolute WER is not a valid quality claim | as above, pinned Tamil ASR | FAIL if relative regression > Δ |
| EV-01 | WER (Tanglish) | **TBE** — no canonical orthography, see §5.1 | Human transcription on subset + ASR on Tamil-script subset only | FAIL on human-transcription intelligibility regression |
| EV-02 | CER, all three | **TBE**, relative | as WER | as WER |
| EV-03 | Pronunciation accuracy (entity exactness) | **100%** on the frozen exact-match suite — derivable, `PS` specifies these outputs | §8 N4/N5/N6 scored by expected-token-sequence match | Any failure blocks release |
| EV-03 | Pronunciation accuracy (general lexicon) | **TBE** | Curated hard-word list, human phoneme-level judgement | **TBE** |
| EV-04 | Intelligibility (objective proxy) | **TBE** | ASR-based + human transcription on subset | **TBE** |
| EV-05 | Speaker similarity | **TBE** | Cosine similarity of speaker embeddings vs reference; and cross-language within-utterance | FAIL below TBE floor, or if cross-language drop exceeds TBE |
| EV-06 | Code-switch quality (objective) | **TBE** | §5.1 O-06 composite | **TBE** |
| EV-07 | MOS (naturalness), per language | **TBE** | §5.2, 5-point ACR | FAIL if MOS < TBE or CI overlaps prior release downward |
| EV-08–15 | Each human axis | **TBE** | §5.2 | §10 regression rules |
| CX-05 | Quality must not regress after any optimization | **Zero tolerance beyond noise band** | Re-run full quality regression after each perf change | FAIL if any axis drops beyond its CI |

### 4.2 Latency

| Req | Metric | Target | Test method | Pass/Fail rule |
|---|---|---|---|---|
| PERF-01 | **p99 of the primary latency metric** | **≤ 500 ms** [S] — primary metric pending `Q-01`; recommended TTFA | §6 steady-state benchmark at concurrency 15 and 20 | FAIL if p99 > 500 ms at declared target concurrency |
| PERF-02 | TTFA p50 / p95 / p99 | p99 ≤ 500 ms (if `Q-01`→TTFA); p50/p95 **TBE** | §6 F-1 | Reported at every concurrency level |
| PERF-06 | E2E latency p50/p95/p99 | **TBE** — must be an RTF-normalized bound, not a fixed ms figure | §6 F-2 | FAIL if RTF ≥ 1.0 at target concurrency (derivable from IR-02) |
| PERF-15 | Cold start | **TBE** | §6.7, separate from steady state | Reported, not gated (unless autoscaling adopted) |
| FR-11 | Cancellation latency | **TBE**, pending `Q-04` | §6.8 | Deferred |

### 4.3 Concurrency, throughput, resources

| Req | Metric | Target | Test method | Pass/Fail rule |
|---|---|---|---|---|
| CC-01/05 | Max sustainable concurrency `C*` | **≥ 15, goal 20** [S] | §7 protocol | PASS only if the full §7 predicate holds for the whole window |
| PERF-07 | Throughput (audio-min/hour) | **TBE** (derived, not independently targeted) | §6 F-4 | Reported |
| PERF-08 | RPS | **TBE** | §6 F-3 | Reported |
| PERF-13 | Error rate | **TBE** — recommend ≤ 0.1% at target concurrency [RR] | §6 F-7 | FAIL above TBE |
| PERF-09/10 | GPU / CPU utilization | No hard target; saturation detection | 1 Hz sampling | Informational + §7 predicate input |
| PERF-11/12 | VRAM / RAM | Must fit declared hardware with headroom **TBE** | Peak sampling | FAIL on OOM or exceeding headroom |

### 4.4 Cost

| Req | Metric | Target | Test method | Pass/Fail rule |
|---|---|---|---|---|
| CO-04 | Cost per audio minute | **TBE** — `PS` says only "as low as possible" | §11 C-3 at each concurrency level | No absolute pass/fail; ranks configurations |
| CO-05 | Cost curve vs concurrency | Reported at 1/5/10/15/20 | §11 | Must be reported for every candidate config |
| CO-01 | Cost minimization | Comparative | §11 identical workload + environment | Chosen config must be justified against cheaper rejected configs |

### 4.5 Pronunciation, code-switching, speaker consistency

| Req | Metric | Target | Test method | Pass/Fail rule |
|---|---|---|---|---|
| PN-04/05/06 | Digit/character-sequence exactness | **100%** (explicit in `PS`) | §8 exact-match suite | Any failure blocks release |
| PN-14 | Context-sensitivity | **100%** on frozen minimal pairs | §8 N-AMB | Any failure blocks release |
| PN-01–13,15,16 | Category correctness | **TBE per category** | §8 | Set at Phase 0 close after case authoring |
| LR-03–07 | Code-switch naturalness | **TBE** (H-06) | §5.2 boundary-focused listening | Regression-blocking after Phase 8 baseline |
| MR-06 | Speaker consistency across a code-switch boundary | **TBE** (O-05 + H-08) | Within-utterance embedding drift + human A/B | Regression-blocking |

---

## 5. Quality Evaluation Protocol

### 5.0 Test-set structure (shared by objective and human evaluation)

```
eval/
  golden/
    en/    # §9.1
    ta/    # §9.2
    tg/    # §9.3  (tg-a: Tamil-script+English, tg-b: Latin Tamil, tg-c: suffixed)
  normalization/   # §8, text-level + audio-level
  hard_cases/      # curated difficult pronunciations
  manifest.json    # id, text, lang_tag, script, category, entity_labels,
                   # expected_spoken_form (where deterministic), duration_bucket,
                   # golden_set_version
```

Every item carries a stable `id`. Results are always reported **per stratum** (language × utterance length × entity-heavy/plain), never as a single pooled average — pooling hides Tamil and Tanglish regressions behind English gains. [ED]

### 5.1 Objective evaluation

| ID | Metric | Definition | Notes / caveats |
|---|---|---|---|
| O-01 | **WER** | `(S+D+I)/N` on ASR transcript vs reference text, after a **frozen text-normalization function** applied to both sides | Version-pin the ASR model; record in §12. Report per language stratum |
| O-02 | **CER** | Same at character level | Preferred over WER for Tamil — agglutinative morphology makes word-level errors coarse [RR] |
| O-03 | **Pronunciation accuracy** | (a) **entity exactness** — synthesized entity matches the frozen `expected_spoken_form` token sequence; (b) **lexical accuracy** — phone-level correctness on a curated hard-word list, judged by a Tamil-literate annotator | (a) is automatable and release-blocking; (b) is human |
| O-04 | **Intelligibility** | Human transcription accuracy on a randomized subset (primary), ASR-WER as cheap proxy (secondary) | Do not report ASR-WER *as* intelligibility — it is a proxy |
| O-05 | **Speaker similarity** | Cosine similarity of speaker embeddings (pinned encoder) between (i) synth vs reference-voice enrollment, and (ii) **within-utterance across the code-switch boundary** | (ii) is what actually measures the Tanglish risk [RR] |
| O-06 | **Code-switch quality** | Composite: (a) boundary discontinuity — spectral/F0/energy discontinuity at switch points vs matched within-language points; (b) **language-ID consistency** via a pinned spoken-LID model; (c) duration sanity — pause length at switch vs non-switch points | No standard metric exists; this composite is [RR] and must itself be validated against human H-06 in Phase 7. If correlation is weak, the metric is discarded — not the human score |

**Critical caveat on O-01/O-02 for Tamil and Tanglish** [RR]

- Tamil ASR error rates on clean human speech are non-trivial; a TTS-WER number mixes synthesis error with recognition error and cannot support an absolute quality claim.
- Latin-script Tanglish has **no canonical orthography** — `enga` / `engae` / `engey` are all defensible, so WER against a single reference is systematically inflated.
- **Therefore:** WER/CER are *relative regression tripwires* against a pinned ASR and a frozen reference, never absolute quality claims or cross-system comparisons. Absolute intelligibility comes from human transcription (O-04a).

### 5.2 Human evaluation

**Who evaluates** [ED]

- **Panel A — Native Tamil speakers from the target region**, everyday code-switchers, non-experts. Score naturalness, regional naturalness, Tanglish quality. Minimum 8–12 raters per release. They are the authority on H-06 and H-09.
- **Panel B — Speech/linguistics-literate raters** (2–4). Score pronunciation-level axes (H-04, H-05) and diagnose failures. Diagnostic, not averaged into MOS.
- **Exclusion:** anyone who worked on the model being evaluated may not rate it.

**What the evaluator sees and hears**

- **Blind and randomized.** Systems labelled `A/B/C…`, remapped per rater; sample order randomized per rater.
- Text visibility depends on the axis:
  - **Intelligibility (H-03):** text hidden → rater transcribes what they hear.
  - **Naturalness / MOS / prosody (H-01, H-02, H-07):** text hidden → judged as speech, not as a reading.
  - **Pronunciation axes (H-04, H-05, H-06) and speaker consistency (H-08):** text shown → rendering judged against intent.
- **Anchors:** each session begins with 3 unscored calibration clips spanning obviously-bad to obviously-good, drawn from a frozen anchor set. [ED]

**Axes and scales**

| ID | Axis | Scale | Prompt to rater |
|---|---|---|---|
| H-01 | MOS (overall quality) | 5-pt ACR (1 Bad – 5 Excellent) | "Overall quality of this speech" |
| H-02 | Naturalness | 5-pt | "How human-like / natural does this sound?" |
| H-03 | Intelligibility | Transcription task → scored as WER on human transcript | (no rating; transcribe) |
| H-04 | Tamil pronunciation | 5-pt | "Are the Tamil words pronounced correctly?" |
| H-05 | English pronunciation | 5-pt | "Are the English words pronounced correctly?" |
| H-06 | Tanglish / code-switch quality | 5-pt | "Does the switch between Tamil and English sound like how people actually speak?" |
| H-07 | Prosody | 5-pt | "Is the rhythm, stress and intonation appropriate?" |
| H-08 | Speaker consistency | 5-pt + binary "did the voice change?" | "Does it sound like the same person throughout?" |
| H-09 | Regional naturalness | 5-pt | "Does this sound like a natural speaker from this region?" |
| H-10 | *(comparative, optional)* Preference | A/B forced choice + CMOS −3…+3 | Release-vs-release comparison |

**Sample size considerations** [ED/RR]

- Per language stratum per release: **≥ 60 utterances**, each rated by **≥ 5 raters** → ≥ 300 ratings per stratum. Pragmatic floor; a project decision, not a `PS` requirement.
- Tanglish gets **≥ 100 utterances** — highest expected variance and the research contribution. [RR]
- Report **mean + 95% CI** always. **Never compare bare means.**
- For release-vs-release decisions prefer **CMOS / preference tests** over absolute MOS — far more sensitive at the same sample size. [RR]

**Bias controls** [ED]

1. Blind system labels, remapped per rater.
2. Randomized presentation order.
3. Calibration anchors at session start.
4. **Trap items** — deliberately degraded clips (and natural-speech clips where licensing permits); a rater failing traps is excluded from that round.
5. Rater fatigue cap: **≤ 30 minutes** per session, ≤ 100 items.
6. Fixed listening conditions recorded: headphones required, quiet environment attested.
7. **Loudness normalization** to a fixed LUFS target applied identically to every clip before rating — otherwise raters score loudness as quality.
8. Rater pool composition recorded per round; a substantially changed pool invalidates cross-round comparison unless anchors show equivalence.

**Reproducibility artifacts (EV-16):** frozen sample-id list, rater-instruction text, anchor set, random seed, per-rater raw scores retained.

---

## 6. Performance Benchmark Protocol

### 6.1 Load model

`PS§6` explicitly rejects "20 requests sent once". Two load models are specified and **both are run** [ED]:

- **Closed-loop (primary, defines "concurrency C").** `C` persistent virtual users. Each: send request → wait for full response → think-time → send next. Think-time models an agent turn; fixed at **T_think = 3 s** (project decision; recorded, tunable, constant across all compared configs). This is what "15–20 concurrent requests" means operationally (§7).
- **Open-loop (secondary, saturation finding).** Poisson arrivals at rate λ independent of server response. Finds the knee and exposes queueing behaviour closed-loop hides.

**Coordinated omission must be avoided** in the open-loop test: latency is measured from the request's *intended* dispatch time, not from when the client actually sent it. A harness that stalls its own send loop under load will silently under-report p99. [ED — the most common way TTS benchmarks lie.]

### 6.2 Per-level protocol (levels 1, 5, 10, 15, 20 — CC-04)

| Parameter | Value | Rationale |
|---|---|---|
| Warm-up | **60 s** or 3×C requests, whichever is longer; results **discarded** | Excludes lazy init, CUDA graph capture, cache fill (PERF-14) |
| Measurement window | **300 s** steady state | Long enough for p99 to be meaningful |
| Minimum completed requests | **≥ 1,000** per level; extend window if needed | **p99 from 200 samples is noise.** ≥1,000 gives ~10 samples in the tail — still thin, so report p99 with a bootstrap CI |
| Repetitions | **3 independent runs**, fresh process each | Report median-of-runs and inter-run spread |
| Cooldown between levels | 30 s idle | Thermal/clock settling |
| Request text | Sampled without replacement from the frozen benchmark corpus, fixed seed | Reproducibility |

**Benchmark corpus composition** (frozen in Phase 0 as `bench_corpus_v1`) [ED]

| Dimension | Split |
|---|---|
| Language | English 35% / Tamil 35% / Tanglish 30% |
| Length | Short (≤ 8 words / ~2 s) 40% · Medium (9–25 words / ~2–7 s) 45% · Long (> 25 words / > 7 s) 15% |
| Entity load | Entity-heavy (≥ 2 normalizable entities) **30%** of all requests |
| Mode | Streaming 100% for the primary latency benchmark; separate non-streaming pass for E2E/throughput comparison |

The length distribution is deliberately skewed short to mirror real agent turns. **This distribution is an assumption** [A] — not in `PS` — and must be replaced with the true production distribution once available (`Q-06`). It is frozen now so all comparisons are fair; any later change invalidates cross-version comparison.

### 6.3 Timestamps

Recorded per request, client-side unless noted:

```
t0  request dispatched (intended dispatch time for open-loop)
t1  request accepted by server            (server-side, optional)
t2  first audio byte received by client
t3  last audio byte received by client
tA  audio duration of the generated waveform (seconds)
```

### 6.4 Formulas

| ID | Metric | Formula |
|---|---|---|
| F-1 | **TTFA** | `t2 − t0` |
| F-2 | **E2E latency** | `t3 − t0` |
| F-3 | **RPS** | `completed_requests / measurement_window_seconds` |
| F-4 | **Throughput (audio-min/hour)** | `(Σ tA over window / 60) × (3600 / window_seconds)` |
| F-5 | **RTF** (per request) | `(t3 − t0) / tA` — real-time capable ⇔ RTF < 1 |
| F-6 | **p50/p95/p99** | Percentiles over **successful** requests only, on the pooled 3-run sample; per-run values also reported. Nearest-rank on the raw sample; **never** average per-run percentiles |
| F-7 | **Error rate** | `(failed + timed_out + malformed_audio) / total_attempted`. Frozen taxonomy: `5xx`, timeout (> 10 s), zero-length audio, truncated audio, connection error |
| F-8 | **Queue depth** | Server-side pending-request count, 1 Hz |
| F-9 | **GPU util** | Mean and p95 of 1 Hz samples over the window (NVML equivalent) |
| F-10 | **CPU util** | Mean and p95, normalized to total cores, 1 Hz |
| F-11 | **VRAM** | Steady-state mean and **peak** over window |
| F-12 | **RAM** | Process RSS steady-state mean and peak |

**Percentiles are always reported with the sample size that produced them. A p99 without `n` is not a result.** [ED]

### 6.5 EXCLUDED from steady-state latency

- Model loading / weight deserialization / device transfer (PERF-14, explicit in `PS§5`)
- Warm-up requests
- Compilation, kernel autotuning, CUDA-graph capture, first-call allocator growth
- Client process startup, DNS, TLS handshake on the *first* connection (connections are pre-established and reused)
- Offline text preprocessing that would be cached in production — **only if it is genuinely cached in production**; otherwise it counts

### 6.6 INCLUDED (and must not be quietly dropped)

- **Text normalization / frontend processing** — part of user-perceived latency and, for entity-heavy taxi utterances, a real cost. Excluding it is a common and inadmissible cheat. [ED]
- Queueing/scheduling delay inside the server
- Batching wait time
- Vocoder / waveform generation and encoding to the delivery format
- Network transfer within the measurement environment (loopback vs LAN must be stated)

### 6.7 Cold-start protocol (separate, PERF-15)

Measured, reported, **never** mixed into steady state:

- `T_load`: process start → model ready to accept requests
- `T_first_request`: ready → first response complete (captures lazy init)
- `T_to_steady`: requests until TTFA stabilizes within ±10% of steady-state p50
- Measured 3× from a cold page cache where the environment permits

### 6.8 Cancellation benchmark (conditional on `Q-04`)

If barge-in is required: time from cancel signal to (a) last audio byte emitted, (b) resources released. Also verify a cancelled request leaves the server undegraded — run the standard level-15 test immediately after a cancellation storm.

---

## 7. Concurrency Definition

`PS` explicitly demands this and explicitly rejects the naive reading. Frozen definitions:

| Term | Definition |
|---|---|
| **Simultaneous requests (burst)** | `N` requests dispatched within a window smaller than one request's service time. A one-shot burst. **NOT the target** (CC-02) |
| **Offered concurrency `C`** | Number of persistent virtual users in the closed-loop model (§6.1), each looping request → response → 3 s think-time |
| **In-flight concurrency** | Instantaneous count of accepted-but-unfinished requests, 1 Hz. Reported as mean and p95; an *observed* quantity, not a control knob |
| **Sustained concurrency** | Offered concurrency `C` held continuously for the full 300 s window after warm-up |
| **Maximum sustainable concurrency `C*`** | The largest `C` in {1,5,10,15,20,…} for which the PASS predicate holds on **all three** repetitions |
| **Queueing** | Server-side backlog, detected via F-8. Bounded queueing is acceptable; *growing* queueing is not |
| **Overload** | Queue depth grows monotonically, or error rate exceeds threshold, or latency percentiles diverge run-over-run. Overload is a FAIL regardless of how many requests completed |

### 7.1 PASS predicate for "concurrency level `C` is sustainable"

All conditions must hold **for every one of the 3 repetitions**, over the entire 300 s window:

1. **Latency** — `p99(primary latency metric) ≤ 500 ms` (PERF-01, pending `Q-01`), **and** `p95 ≤ TBE`, **and** `RTF < 1.0` at p95.
2. **Error rate** — `F-7 ≤ TBE` (recommended ≤ 0.1% [RR]); **zero** OOM events; zero truncated-audio events.
3. **Stability, not just level** — linear regression of TTFA against wall-clock over the window has slope statistically indistinguishable from zero. *A system whose latency is climbing throughout the window has not passed; it has merely not yet failed.* [ED — the single most important clause here.]
4. **Queue stationarity** — F-8 slope ≈ 0; queue-depth p95 bounded by a declared limit.
5. **Resource headroom** — peak VRAM ≤ 90% of device capacity; peak RSS ≤ 85% of system RAM; no swap activity. Saturation without headroom is a FAIL even if latency passed, because it will not survive production variance. [ED]
6. **Quality unchanged under load** — a sample of outputs generated *during* the load test passes the normalization exact-match suite and shows no audio artifacts. Passing latency while emitting degraded audio is a FAIL (CX-05). [ED]

### 7.2 Reported result format

> `C* = 15` at `p99 TTFA = 412 ms`, `error 0.02%`, `GPU util p95 = 78%`, `VRAM peak 9.2/12 GB`, `queue slope ≈ 0`, `n = 1,043 × 3 runs`, config `<env hash>`.

`CC-01` is met when `C* ≥ 15`; the goal is `C* ≥ 20`.

---

## 8. Normalization Test Specification

Purpose: freeze, in Phase 0, the test set that Phase 1's normalization engine is built *against*. Every case has a **frozen expected spoken form**; the engine is scored by exact match on that token sequence (transcribed by ASR + human adjudication for disputes).

**Case record schema** [ED]

```
id, category, input_text, input_lang, input_script, context_hint,
expected_spoken_form_en, expected_spoken_form_ta, expected_spoken_form_tanglish,
determinism: {exact | preferred | open}, notes, source_ref
```

`determinism` matters: OTP/phone/booking-ID are **exact** (`PS` specifies them). Most others are **preferred** (a canonical form we choose, alternatives allowed) or **open** (must be decided in Phase 1 with a recorded rationale).

### 8.1 Categories and representative cases

#### N1 — Numbers

| In | Expected | Notes |
|---|---|---|
| `10 minutes` | "ten minutes" | cardinal |
| `1st stop` | "first stop" | ordinal |
| `2.5 km` | "two point five kilometres" | decimal |
| `1,50,000` | Indian grouping — lakh reading | **ambiguous vs Western grouping** → `open` |
| `100000` | "one lakh" vs "one hundred thousand" | locale decision required |
| `10 நிமிடம்` | "pathu nimidam" | Tamil numeral reading |
| `௧௦` (Tamil digits) | same as `10` | Tamil numeral script input |

#### N2 — Dates

| In | Expected | Notes |
|---|---|---|
| `2/3/2026` | **AMBIGUOUS** — DD/MM vs MM/DD | resolved by locale policy; `open` |
| `3rd March` | "third of March" | |
| `03-03-2026` | | separator handling |
| `tomorrow 9 AM` | relative date | |
| Tamil month names | | Tamil calendar vs Gregorian in Tamil |

#### N3 — Times (`PS` explicit)

| In | Expected | Notes |
|---|---|---|
| `7:30 PM` | EN: "seven thirty PM" / "half past seven in the evening" | `PS` requires "natural"; choose one canonical, record rationale |
| `7:30 PM` in Tamil | "ezhu muppadhu" vs "ezharai" (colloquial) | **major regional-naturalness case** |
| `12:00 AM` | midnight | edge |
| `7:05` | "seven oh five" — not "seven five" | leading-zero trap |
| `10 mins` / `10 min` | "ten minutes" | abbreviation |
| `ETA 7:30` | | combined abbreviation + time |

#### N4 — Phone numbers (`PS` explicit: digit-by-digit)

| In | Expected | determinism |
|---|---|---|
| `9876543210` | "nine eight seven six five four three two one zero" | **exact** |
| `+91 98765 43210` | country code handling | exact |
| Tamil context | Tamil digit names, digit-by-digit | exact |
| `98765 43210` grouped | grouping must **not** cause "ninety-eight thousand…" | exact — **key trap** |

#### N5 — OTP (`PS` explicit)

| In | Expected | determinism |
|---|---|---|
| `Your OTP is 4821.` | "four eight two one" | **exact** (`PS` verbatim) |
| `OTP: 0042` | "zero zero four two" — leading zeros preserved | exact — **key trap** |
| `உங்கள் OTP 4821` | Tamil digit names, digit-by-digit | exact |
| 6-digit OTP | digit-by-digit | exact |

#### N6 — Booking IDs (`PS` explicit)

| In | Expected | determinism |
|---|---|---|
| `TN45AB1234` | character/digit sequence, **not** "one thousand two hundred thirty-four" | **exact** |
| — | Open sub-question: `T-N-four-five-A-B-one-two-three-four` vs grouped `TN forty-five AB…` — `PS` says "appropriate", not which → decide in Phase 1, record | open |
| Letters in Tamil context | Tamil letter names vs English letter names — **regional-naturalness question**; real Tamil speakers usually use English letter names for alphanumerics | open, high research value |
| `BK-2026-0093` | separator handling | |

#### N7 — Addresses

| In | Expected | Notes |
|---|---|---|
| `No. 12, 3rd Cross St` | "number twelve, third cross street" | `No.` ≠ "no" — **trap** |
| `1st Main Rd` | | |
| `Anna Nagar West Extn` | | abbreviation inside a proper name |
| `Chennai 600040` | PIN code — digit-by-digit vs grouped | open |
| `Dr. Radhakrishnan Salai` | "Doctor" (title in a street name) vs "Drive" | **ambiguity trap** |

#### N8 — Abbreviations

`OTP`, `ETA`, `AC`, `SUV`, `KM`, `ID`, `PM/AM`, `Rs.`, `INR`, `GPS`, `A/C`, `Nr.`, `St.`

Traps: `St.` = Street vs Saint · `AC` = air-conditioned (spell out letters) · `KM` = "kilometres" not "kay-em" · `A/C` in Tamil context.

#### N9 — Vehicle names/types

`Sedan`, `SUV`, `Auto`, `Mini`, `Prime Sedan`, `XL`, `Bike`, `Innova`, `Etios`, `Swift Dzire`

Traps: brand names must not be Tamil-ized incorrectly; `XL` = letter names; `Auto` in Tamil context (`ஆட்டோ`).

#### N10 — Prices

`₹250`, `Rs. 250`, `250 rupees`, `₹1,250.50`, `₹0`, `surge 1.5x`

Traps: currency symbol position; paise handling; `1.5x` = "one point five times".

#### N11 — Distances

`2.5 km`, `500 m`, `2 kms`, `1.2 KM`

Traps: unit pluralization in Tamil; `m` = metres vs minutes ambiguity in `5 m`.

#### N12 — Names

Tamil names in Latin script (`Karthik`, `Sivakumar`, `Meenakshi`), English names in Tamil script, initials (`R. Kumar` → "R Kumar"), mononyms, names that collide with common words.

#### N13 — Locations

`Chennai Central`, `T. Nagar` (→ "Tea Nagar" trap — locally "Thyagaraya Nagar" but spoken as "T Nagar"), `Velachery`, `OMR`, `ECR`, `Guindy`, `Koyambedu`, airport terminal names. **A curated Chennai-area location lexicon is a Phase 1 deliverable** [RR].

#### N14 — Tamil + English mixed text

`உங்கள் pickup location எங்கே?` · `Driver 5 minutes-ல வருவார்` · `Your ride ₹250 ஆகும்`

Traps: entity inside the English span but sentence is Tamil; number reading language must follow the **matrix language**, not the digit's script — an open Phase 1 policy question.

#### N15 — Tamil in Latin script + suffix attachment

`unga pickup location enga?` · `Chennai Central-ல இருக்கா?` · `booking-ah cancel pannunga` · `driver kitta pesunga`

Traps: `-ல`, `-ah`, `-kku` suffixes glued to English tokens; ambiguous Latin spellings (`enga`/`engae`); `pannunga` vs `panunga`; single letters that are Tamil words.

#### N-AMB — Ambiguity suite (the heart of PN-14)

Minimal pairs where **the same string must be rendered differently**:

| String | Context A | Rendering A | Context B | Rendering B |
|---|---|---|---|---|
| `4821` | "Your OTP is 4821" | four eight two one | "The fare is 4821 rupees" | four thousand eight hundred twenty-one |
| `1234` | booking ID suffix | one two three four | price | one thousand two hundred thirty-four |
| `2026` | year | twenty twenty-six | booking count | two thousand twenty-six |
| `10` | "10 minutes" | ten | inside a phone number | one, zero |
| `600040` | PIN code | six zero zero zero four zero | quantity | six hundred thousand forty |
| `TN45` | booking ID prefix | T N four five | vehicle plate spoken aloud | (may differ) |
| `5 m` | distance | five metres | duration | five minutes |
| `St.` | `St. Thomas Mount` | Saint | `3rd Cross St.` | Street |
| `Dr.` | `Dr. Kumar` | Doctor | `Palm Grove Dr.` | Drive |

**Every one of these pairs is release-blocking** because `PS§CONTEXT-AWARE PRONUNCIATION` states context-sensitivity as a requirement, not a nicety.

### 8.2 Sizing (Phase 0 freeze)

Structure and category list are frozen now; **case authoring is a Phase 0 deliverable** with a minimum of **25 cases per category** and **≥ 40** in N-AMB, of which ≥ 30% must be Tamil-context and ≥ 20% Tanglish-context. [ED]

---

## 9. Language Golden Test Specification

Structure and coverage requirements only — **no large dataset generated in Phase 0**.

### 9.0 Common structure

Every golden item: `id`, `text`, `language`, `script`, `category`, `length_bucket`, `entity_labels[]`, `domain_scenario`, `expected_notes`, `set_version`.

Coverage requirements apply **per language**; a golden set version is invalid if any required category is empty.

### 9.1 English golden set (`en_v1`)

| Category | Min items | Notes |
|---|---|---|
| Conversational agent turns | 40 | Real taxi-agent phrasing |
| Short (≤ 8 words) | 25 | "Your cab is arriving." |
| Long (> 25 words) | 15 | Multi-clause confirmations, prosody stress test |
| Person names | 20 | Indian + non-Indian |
| Locations | 20 | Chennai-area heavy |
| Numbers / prices / distances | 25 | |
| Dates / times | 20 | |
| Phone / OTP / booking ID | 25 | Overlaps §8 exact-match |
| Transportation terminology | 20 | fare, surge, pickup, drop, waiting charge, toll |
| Difficult pronunciation | 15 | Homographs (`read`, `live`, `minute`), acronym-in-sentence |
| Questions / imperatives / confirmations | 15 | Intonation contour coverage |
| **Total floor** | **~200** | |

### 9.2 Tamil golden set (`ta_v1`)

Same category skeleton, plus Tamil-specific:

| Additional category | Min items | Notes |
|---|---|---|
| Formal vs colloquial register pairs | 20 | `வருகிறார்` vs `வர்றாரு` — register strongly affects naturalness |
| Agglutinative long words | 15 | Long suffix chains stress the duration model |
| Retroflex / trill contrasts | 15 | `ழ` `ள` `ல`, `ற` `ர` — classic Tamil TTS failure points |
| Sandhi / word-boundary junctions | 15 | |
| Loanwords already naturalized into Tamil | 15 | `பஸ்`, `ஆட்டோ`, `ரோடு` — distinct from code-switching |
| **Total floor** | **~230** | |

### 9.3 Tanglish golden set (`tg_v1`) — largest and most structured

| Sub-set | Definition | Min items |
|---|---|---|
| **TG-A** | Tamil script matrix + Latin English inserts (`உங்கள் pickup location எங்கே?`) | 80 |
| **TG-B** | Fully Latin script, Tamil matrix (`unga pickup location enga?`) | 80 |
| **TG-C** | Mixed script + Tamil suffix on English token (`Chennai Central-ல இருக்கா?`) | 60 |

Cross-cutting coverage required in **each** sub-set:

| Dimension | Requirement |
|---|---|
| Switch granularity | intra-word (suffixed), single-word insert, phrase insert, clause alternation |
| Switch count per utterance | 1 switch / 2 switches / ≥3 switches — all represented |
| Switch position | utterance-initial, medial, final |
| Matrix language | Tamil-matrix (majority) and English-matrix (minority) both present |
| Entities inside switched spans | ≥ 30% of items |
| Length | short/medium/long as §6.2 |
| Domain scenarios | all six `PS` use cases represented |
| Register | formal and colloquial |
| **Total floor** | **~220** |

### 9.4 Rules

- Golden sets are **frozen and versioned** (DR-08). Never edited in place.
- **Held out from all training data** (DR-07), verified by an overlap script.
- A **stable 50-item "canary" subset** per language is designated for fast per-commit smoke runs. [ED]
- Ground-truth human recordings are **desirable but not required** — where they exist they enable speaker-similarity and CMOS-vs-human comparisons; where they don't, evaluation is system-vs-system. Recording a reference human read of the golden sets is a [RR] worth the cost.

---

## 10. Regression Strategy

### 10.1 What gets frozen (the regression baseline)

| Frozen artifact | Version tag | Changes how |
|---|---|---|
| Golden sets `en_v1` / `ta_v1` / `tg_v1` | `golden@v1` | New version only; old version retained forever |
| Normalization suite (§8) with expected spoken forms | `norm@v1` | Additive only within a version; corrections bump version |
| Benchmark corpus + load protocol (§6) | `bench@v1` | Any change invalidates cross-version perf comparison |
| Human-eval sample lists, rater instructions, anchor clips | `humaneval@v1` | |
| Pinned ASR model, speaker encoder, LID model | recorded in §12 | Swapping any invalidates all historical objective numbers |
| Environment record (§12) | per-run hash | |
| The **reference release** (last shipped model) | `release@N` | The comparison target |

### 10.2 Regression suites

| Suite | Contents | Trigger | Runtime |
|---|---|---|---|
| **RS-0 Smoke** | 50-item canary per language; normalization exact-match subset | Every commit to model/frontend/serving | minutes |
| **RS-1 Normalization** | Full §8 suite, text-level + audio-level on exact-match cases | Any frontend/normalization change; every release | minutes–hours |
| **RS-2 English quality** | `en_v1` objective (O-01..05) + human subset | Every model change; every release | |
| **RS-3 Tamil quality** | `ta_v1` objective + human subset | Every model change; every release | |
| **RS-4 Tanglish quality** | `tg_v1` objective (O-05, O-06) + human H-06/H-08/H-09 | Every model change from Phase 7 onward; every release | |
| **RS-5 Performance** | Full §6 sweep 1/5/10/15/20, 3 reps | Any serving/optimization/model/precision/hardware change; every release | hours |
| **RS-6 Cost** | §11 recomputation | Whenever RS-5 runs | |
| **RS-7 Compliance** | License matrix diff; dependency + egress audit (CX-01/02/03) | Every dependency change; every release | |

### 10.3 What constitutes a regression

| Type | Definition |
|---|---|
| **Hard regression (blocking)** | Any exact-match normalization case that previously passed now fails; any `PS`-explicit behaviour (OTP/phone/booking-ID/time) broken; `p99 > 500 ms` at declared `C*`; `C*` drops below 15; error rate above threshold; OOM; any HC-1…HC-12 violation; any license/compliance failure |
| **Quality regression (blocking)** | Any human axis mean drops by more than its 95% CI vs `release@N`, on any language stratum. **Stratum-level, not pooled** — an English gain must never mask a Tamil loss |
| **Soft regression (warn + justify)** | Objective metric moves adversely within noise band; a `preferred`-determinism normalization case changes rendering; cost/minute increases without a corresponding quality or latency gain |
| **Not a regression** | Changes to `open`-determinism cases where the new behaviour is documented and reviewed |

### 10.4 Release-blocking rules

A release ships only if:

1. RS-1 exact-match subset: **100% pass**.
2. RS-2, RS-3, RS-4: **no quality regression on any stratum** (MR-07 — Tanglish work must not cost Tamil).
3. RS-5: `C* ≥ 15` with the full §7 predicate.
4. RS-7: clean.
5. CX-05 check: if this release included a performance optimization, RS-2/3/4 must be re-run **after** the optimization, and both quality and perf must pass together. A perf win with an unmeasured quality cost is not a release.

**Asymmetric rule protecting the research contribution** [ED]: after Phase 7, any Tanglish improvement that causes a Tamil or English regression beyond CI is **rejected by default** and may only be accepted by an explicit, documented trade-off decision. This operationalizes MR-07 and conflict C-06.

---

## 11. Cost Benchmark Methodology

Formulas only — no invented prices.

### 11.1 Inputs to record (never assumed)

| Symbol | Meaning | Source |
|---|---|---|
| `H_cost` | Cost per hour of the hardware unit (owned or rented) | Actual procurement/rental; if owned, see amortization |
| `H_capex` | Purchase price of owned hardware | |
| `L_life` | Amortization lifetime in hours | Project decision, recorded |
| `U_power` | Average power draw (W) during the benchmark | **Measured**, not spec-sheet |
| `P_rate` | Electricity cost per kWh | Recorded |
| `O_overhead` | Hosting overhead multiplier (cooling, networking, ops) | Recorded assumption |
| `N_units` | Number of hardware units used | |
| `W` | Measurement window (hours) | §6 |
| `A_min` | Audio minutes generated in `W` | F-4 |

### 11.2 Formulas

```
C-0  (owned hardware hourly)   H_cost = H_capex / L_life
                                        + (U_power/1000 × P_rate)
                                        × O_overhead
     (rented)                  H_cost = quoted hourly rate × O_overhead

C-1  Infrastructure cost/hour  Cost_hr = N_units × H_cost

C-2  Audio minutes/hour        A_hr    = A_min × (1 / W)          [= F-4]

C-3  Cost per audio minute     Cost_min = Cost_hr / A_hr
                                        = (N_units × H_cost) / A_hr

C-4  Compute utilization       Util_gpu = mean GPU util over window   [F-9]
C-5  Capacity utilization      Util_cap = A_hr(at C) / A_hr(at C_max_observed)

C-6  Cost per 1k requests      Cost_1k = Cost_hr / (RPS × 3.6)

C-7  Cost at concurrency C     Cost_min(C) — C-3 evaluated at each C ∈ {1,5,10,15,20}

C-8  Marginal cost of a config Δ = Cost_min(config_B) − Cost_min(config_A)
```

### 11.3 Fair-comparison rules (CO-07)

For any comparison of Model A / B / C or Optimization A / B to be admissible:

1. **Identical benchmark corpus** (`bench@v1`), identical seed, identical language/length/entity distribution.
2. **Identical hardware and environment record** (§12), or — if hardware differs — the comparison must report `Cost_min` *and* the environment delta explicitly, and must not claim a model-quality conclusion.
3. **Identical `C`**, and each config's `Cost_min` reported **at its own `C*`** as well as at a common `C` (both numbers; they answer different questions).
4. **Quality reported alongside cost, always.** A cost table without the matching quality-regression result is inadmissible (CX-05, RULE 10). The comparison unit is the pair `(Cost_min, quality_vector)`, never cost alone.
5. Comparisons must state whether they are at **saturation** (fair for throughput) or at **fixed low load** (fair for latency) — a config optimized for batching wins the first and loses the second.
6. Report the **cost curve**, not a point. `Cost_min` falls steeply with concurrency; quoting `Cost_min` at `C=20` for one model and `C=5` for another is the most common way cost comparisons mislead.

---

## 12. Reproducibility Environment

Every benchmark, evaluation and training run emits a machine-readable `env_record.json` with the fields below. **A result without an env record is not a result.** [ED]

**Hardware**
`gpu_model`, `gpu_count`, `gpu_vram_gb`, `gpu_driver_version`, `gpu_power_limit_w`, `gpu_clock_policy`, `cpu_model`, `cpu_cores_physical`, `cpu_cores_logical`, `cpu_governor`, `ram_gb`, `ram_speed`, `storage_type`, `numa_topology`, `virtualized (bool + hypervisor)`, `cloud_instance_type`

**System software**
`os_name`, `os_version`, `kernel`, `container_image_digest`, `cuda_version`, `cudnn_version`, `nccl_version`, `python_version`, `pip_freeze_hash` (+ full lockfile stored)

**ML stack**
`framework` + `version` (torch/onnxruntime/tensorrt/…), `inference_runtime` + version, `compile_flags`, `attention_backend`, `random_seeds`

**Model config**
`model_id`, `model_weights_sha256`, `precision` (fp32/fp16/bf16/int8/fp8 — per component), `quantization_method`, `batch_size` (max + dynamic policy), `batching_strategy` (static/continuous/none), `max_sequence_length`, `vocoder_id + version`, `frontend/normalizer version`, `speaker_id / speaker_embedding_hash`

**Audio contract** (DP-04 — currently unspecified in `PS`, see `Q-02`)
`sample_rate_hz`, `bit_depth`, `channels`, `audio_format` (wav/pcm/opus/μ-law), `codec + bitrate`, `chunk_size_ms` (streaming), `loudness_target_lufs`, `resampling_chain` (train SR → serve SR → delivery SR)

**Eval-tooling pins** (EV-17)
`asr_model_id + version`, `speaker_encoder_id + version`, `lid_model_id + version`, `text_normalizer_for_scoring_version`, `metric_library_versions`

**Run metadata**
`run_id`, `timestamp_utc`, `git_commit`, `golden_set_version`, `bench_corpus_version`, `operator`, `run_type` (steady/cold/regression), `repetition_index`

**Thermal/noise controls** [ED]: record ambient conditions where possible; ensure no other GPU workload on the device; report whether the machine was otherwise idle. A benchmark on a thermally throttling laptop is not comparable to one on a rack GPU, and the record must make that visible.

---

## 13. Data + License Requirements

Compliance **framework** only — no specific models/datasets recommended (MR-03).

### 13.1 Mandatory record per dataset (dataset card)

| Field | Notes |
|---|---|
| `name`, `version`, `source_url`, `retrieval_date` | |
| `license_name`, `license_url`, `license_text_archived` | Archive the text — licenses change |
| `language(s)`, `script(s)`, `dialect/region` | Critical for LR-08 |
| `speaker_count`, `speaker_ids`, `speaker_demographics` (as permitted), `consent_basis` | |
| `recording_conditions` | studio/field/telephony, mic, SNR, background |
| `native_sample_rate`, `bit_depth`, `codec history` | **Telephony-sourced data is band-limited; upsampling does not restore it** |
| `size` | hours of audio, utterance count, token count |
| `transcription_source` | human / ASR-generated / mixed — and quality estimate |
| `commercial_use_allowed` | yes/no/unclear |
| `redistribution_allowed` | yes/no/conditions |
| `derivative_model_allowed` | **the field most often overlooked** |
| `model_output_redistribution_allowed` | can we ship a model trained on this, or its audio? |
| `attribution_required`, `share_alike` | |
| `synthetic_data_flag` + `generator_provenance` | DR-06 / CX-03 |
| `pii_present` + handling | names, phone numbers, addresses in taxi data |
| `approved_by`, `approval_date`, `approval_notes` | human sign-off, per dataset |

### 13.2 Mandatory record per model/checkpoint

Same license fields, plus: `base_model_lineage` (full chain — a permissive wrapper over a restrictive base is still restrictive), `training_data_disclosure` (known/partial/unknown), `weights_license` vs `code_license` (frequently different), `fine-tuning_allowed`, `commercial_inference_allowed`, `output_license` (some licenses claim rights over generated audio), `voice_cloning_restrictions`, `named_use_restrictions` (acceptable-use addenda).

### 13.3 Compliance process [ED]

1. **No dataset or model enters the repository without an approved card.** A `pending` card blocks use in any run producing a reported result.
2. **Two-tier approval:** `research_only` (experiments only, may not ship) vs `production_approved` (may ship). Every checkpoint records which tier its inputs were.
3. **Lineage propagation:** a model's effective license is the *most restrictive* element in its lineage, including data. Recorded automatically in the model card.
4. **Open-source gate (DL-07):** before Phase 10 release, verify the intersection of all lineage licenses permits the intended release form. If weight release is forbidden, the release scope narrows to code+recipe — decided then, not assumed now.
5. **CX-03 audit:** confirm no training data, distillation target or evaluation dependency originates from a prohibited hosted TTS API — including third-party datasets whose "synthetic" portion was generated by such an API. A real and easily missed contamination path.
6. **Voice rights:** if a target voice is recorded or cloned, record consent scope (commercial use, duration, revocability). Not in `PS`, but a legal hard edge for a production contact center. [A → `Q-07`]

---

## 14. Requirement Traceability Matrix

Format: **Requirement → Component → Metric → Test → Acceptance → Phase**.

| Req | Component | Metric | Test | Acceptance | Phase |
|---|---|---|---|---|---|
| FR-01 | TTS engine | O-04, H-03 | Golden §9 | ≥ TBE | 3,6,9 |
| FR-02..06 | Content/domain coverage | coverage % | Golden domain audit | 100% scenarios | 0,3,9 |
| FR-07 | Model architecture | H-06, O-06 | TG boundary test | no stitching; ≥ TBE | 2,8,9 |
| FR-08 | Serving API | E2E latency, integration pass | Phase 10 integration run | pass | 5,10 |
| FR-09 | Whole system | egress audit | RS-7 | zero external TTS calls | 0–10 |
| FR-10 | API contract | — | harness parity check | same client both paths | 5 |
| FR-11 | Serving | cancel latency | §6.8 | TBE (pending Q-04) | 5,10 |
| LR-01 | Model | O-01/02, H-01..05 | `en_v1` | ≥ TBE | 3,6,9 |
| LR-02 | Model | O-01/02, H-01..05 | `ta_v1` | ≥ TBE | 3,6,9 |
| LR-03 | Model | H-06, O-06 | `tg_v1` | ≥ TBE | 7,8,9 |
| LR-04 | Frontend + model | H-06 | TG-A | ≥ TBE | 7,8 |
| LR-05 | Frontend + model | H-06 | TG-B | ≥ TBE | 7,8 |
| LR-06 | Frontend (suffix handling) | H-06, N-15 | TG-C + §8 N15 | ≥ TBE | 1,7,8 |
| LR-07 | Model | H-05, H-06 | TG-A/C | ≥ TBE | 7,8 |
| LR-08 | Data + model | H-09 | Golden ta/tg | ≥ TBE | 3,7,8 |
| LR-09 | Research track | H-06 + publication | Stage 2 | contribution documented | 7,8,10 |
| LR-10 | Programme plan | phase gates | Phase 6 gate before Phase 7 | ordering enforced | 3–7 |
| LR-11 | Unified system | all quality metrics | one deployed system, 3 golden sets | all pass | 9 |
| PN-01..13,15,16 | Normalization engine | O-03a | §8 N1–N15 | TBE / 100% for exact | 1,4 |
| PN-04,05,06 | Normalization engine | O-03a exactness | §8 N4/N5/N6 | **100%** | 1,4 |
| PN-14 | Normalization engine (context) | O-03a | §8 N-AMB | **100%** | 1,4 |
| PN-17 | Frontend design | — | single-engine 3-suite pass | pass | 1 |
| PN-18 | Frontend | rule↔test coverage | coverage report | 100% | 1 |
| DR-01 | Data pipeline | hours, coverage | dataset card | sufficient for Phase 3 gate | 1,3 |
| DR-02 | Tanglish corpus | hours, switch-type coverage | dataset card + §9.3 dims | all dims populated | 7 |
| DR-03,05,06 | Data governance | card completeness | RS-7 | 100% cards approved | 0–10 |
| DR-04 | Data | domain term coverage | coverage report | ≥ TBE | 1,7 |
| DR-07 | Data governance | overlap % | overlap script | 0% | 3,7,8 |
| DR-08 | Eval infra | version tag | git | frozen | 0 |
| MR-01,02 | Model selection | license fields | §13 | approved | 2 |
| MR-03,04 | Phase 0 discipline | — | doc review | no model/arch named | 0 |
| MR-05 | Architecture | Tanglish-feasibility argument | Phase 2 gate | documented + reviewed | 2 |
| MR-06 | Model / speaker repr. | O-05, H-08 | cross-boundary similarity | ≥ TBE | 3,8,9 |
| MR-07 | Training procedure | RS-2/3 deltas | regression | no stratum regression | 8,9 |
| IR-01 | Streaming server | TTFA measurable | §6 streaming path | streaming works | 5 |
| IR-02 | Serving | RTF | F-5 | RTF < 1 at C* | 5,6 |
| IR-03 | Optimization | before/after §6 + RS-2/3/4 | RS-5 + quality | both pass | 6 |
| IR-04 | Deployment | egress audit | RS-7 | clean | 0–10 |
| IR-05 | Serving | — | deferred | pending Q-05 | 5 |
| PERF-01 | Serving | p99 primary latency | §6 at C=15,20 | ≤ 500 ms | 5,6,9,10 |
| PERF-02..06 | Bench harness | F-1,F-2,F-6 | §6 | reported at all C | 5,6,10 |
| PERF-07,08 | Bench harness | F-3,F-4 | §6 | reported | 5,6,10 |
| PERF-09..12 | Resource sampler | F-9..F-12 | §6 1 Hz | reported + headroom | 5,6,10 |
| PERF-13 | Serving | F-7 | §6 | ≤ TBE | 5,6,10 |
| PERF-14 | Bench harness | — | warm-up discard verified | excluded | 0,5 |
| PERF-15 | Bench harness | T_load, T_first | §6.7 | reported separately | 5,6 |
| CC-01 | Serving | C* | §7 | C* ≥ 15 (goal 20) | 5,6,9,10 |
| CC-02,03,05 | Bench methodology | §7 predicate | §7 | definition frozen + applied | 0,5,6 |
| CC-04 | Bench harness | sweep | §6 | all 5 levels run | 5,6,10 |
| CO-01 | Config selection | Cost_min | §11 | justified vs alternatives | 6,9,10 |
| CO-02..06 | Cost harness | C-1..C-5 | §11 | reported per config | 6,9,10 |
| CO-07 | Cost methodology | comparability rules | §11.3 | rules satisfied | 2,6,9,10 |
| EV-01..06 | Objective eval harness | O-01..06 | §5.1 | ≥ TBE / no regression | 0,3,6,8,9,10 |
| EV-07..15 | Human eval protocol | H-01..09 | §5.2 | ≥ TBE / no regression | 0,3,6,8,9,10 |
| EV-16 | Eval infra | reproducibility artifacts | protocol doc | artifacts exist | 0 |
| EV-17 | Eval infra | pinned model versions | §12 | pinned + recorded | 0 |
| DP-01 | Deployment | egress audit | RS-7 | clean | 6,9,10 |
| DP-02 | Integration | Phase 10 acceptance | integration run | pass | 10 |
| DP-03 | Unified system | all gates | Phase 9 | pass | 9 |
| DP-04 | Audio contract | env record fields | §12 | specified + constant | 0 (pending Q-02) |
| DL-01 | Phase 0 docs | §17 checklist | exit gate §18 | complete | 0 |
| DL-02..07 | Phase deliverables | phase gates | per phase | pass | 6,7,9,10 |
| DL-08 | Traceability | matrix completeness | this table, maintained | zero unassigned | 0–10 |
| CX-01,02,03 | Compliance | egress + dependency + provenance audit | RS-7 | clean | 0–10 |
| CX-04 | Compliance | license matrix | §13 | approved | 0–10 |
| CX-05 | Release process | quality-after-perf rerun | §10.4 rule 5 | both pass | 6,9,10 |
| CX-06 | Architecture | Phase 2 gate argument | design review | documented | 2 |
| CX-07 | Architecture | boundary listening test | §5.2 H-06 | no stitching artifacts | 2,8,9 |
| CX-08,09 | Doc process | label audit | doc review | every item labelled | 0–10 |
| CX-10,11,12 | Phase 0 discipline | — | doc review | satisfied | 0 |

> **Unassigned-requirement check: 84 requirements defined in §2; 84 appear above. Zero unassigned.**

---

## 15. Requirement Conflict Analysis

| # | Conflict | Nature | How later experiments resolve it |
|---|---|---|---|
| C-01 | **Quality vs latency** (EV-07 vs PERF-01) | Larger/autoregressive models sound better and start slower | Phase 2 benchmarks candidates on the *pair* `(H-01, p99 TTFA)`, plotting a quality–latency frontier rather than picking a winner on either axis. Phase 5 attacks it structurally with streaming. Decision rule: HC-8 and HC-11 are both constraints — if no frontier point satisfies both, escalate to hardware (DP-a yields), not to quality |
| C-02 | **Quality vs memory** (EV-07 vs PERF-11) | Bigger models, bigger VRAM, fewer concurrent streams | Phase 6 quantization sweep: measure quality delta per precision level on RS-2/3/4. Accept the lowest precision whose quality delta is within CI |
| C-03 | **Model size vs quality** | Smaller = cheaper + faster but typically worse, and *disproportionately* worse on low-resource Tamil and on Tanglish | Phase 2/3 evaluates size scaling **per language stratum**. A size adequate for English may be inadequate for Tamil. Never choose size on English metrics |
| C-04 | **Concurrency vs latency** (CC-01 vs PERF-01) | Batching raises throughput and `C*` but adds queueing/batch-wait to TTFA | Phase 5/6 sweeps batching policy (static vs continuous, max batch, max wait). The §7 predicate forces both to be satisfied simultaneously, so this cannot be resolved by reporting only the favourable one |
| C-05 | **Streaming vs quality** | Chunked generation limits global prosody planning; boundaries can produce artifacts; look-ahead improves quality but raises TTFA | Phase 5: chunk-size / look-ahead sweep scored on H-07 and H-02 vs TTFA, plus a dedicated chunk-boundary artifact listening test. A genuine research trade-off, not a tuning detail |
| C-06 | **Tanglish adaptation vs Tamil/English regression** (LR-09 vs MR-07) | Fine-tuning on code-mixed data commonly degrades monolingual performance | Phase 8 compares adaptation strategies (full fine-tune / adapters / mixed-data replay / multi-task) on the *joint* vector `(tg quality, ta regression, en regression)`. §10.4's asymmetric rule makes monolingual regression rejecting-by-default. Monolingual replay mix is the leading [RR] hypothesis |
| C-07 | **Speaker consistency vs multilingual adaptation** (MR-06 vs LR-03) | Language-conditioned models often drift in timbre across languages; drift is most audible exactly at code-switch boundaries | Phase 3 establishes the cross-language similarity baseline (O-05ii) *before* Tanglish work. Phase 8: disentangled speaker conditioning, speaker-consistency loss, single-speaker multilingual data. Measure **within-utterance** drift, not just utterance-level similarity |
| C-08 | **Cost vs performance** (CO-01 vs PERF-01/CC-01) | Cheaper hardware → lower `C*` or higher latency | §11 forces the cost curve to be reported with the quality vector. Precedence fixed in §3: HC-8/HC-9 outrank DP-a |
| C-09 | **Naturalness vs entity exactness** (H-02 vs PN-04/05/06) | Rigid digit-by-digit rendering can sound robotic; natural prosody can blur digit boundaries | `PS` makes exactness explicit and MOS un-thresholded — exactness wins. Phase 4 research question: *prosodically natural* digit sequences (grouping pauses, intonation contour) that remain exactly correct. An under-appreciated sub-problem worth real effort |
| C-10 | **Regional naturalness vs English pronunciation** (H-09 vs H-05) | Should embedded English inside Tamil use Tamil-accented or "correct" English phonology? These score against each other | **A genuine research question, not a bug.** `PS`'s inclusion of "regional pronunciation" and "regional naturalness" strongly implies Tamil-accented English is the target for code-mixed speech. **Phase 7 must settle this empirically** via an A/B human study; the H-05 rubric is then rewritten to score "appropriate for context" rather than "native-English-like". `Q-08` |
| C-11 | **Latency budget vs frontend richness** (PERF-01 vs PN-01..16) | Context-aware normalization (especially model-based entity disambiguation) consumes the same 500 ms budget | Phase 4 measures frontend latency separately against a declared sub-budget. §6.6 forbids excluding it. A learned disambiguator's cost is a first-class latency line item |
| C-12 | **Open-source release vs license lineage** (DL-07 vs CX-04) | The best-performing base model may forbid weight redistribution | §13.3 gate, decided at Phase 10 on facts — but **Phase 2 model selection must record redistribution-permissiveness as a selection criterion** so the choice isn't foreclosed |

---

## 16. Risk Register

Probability / Impact: L / M / H.

| ID | Risk | P | I | Detection | Mitigation | Phase |
|---|---|---|---|---|---|---|
| R-01 | Insufficient Tamil training data (quantity or quality) | M | H | Phase 1 data audit vs Phase 3 requirement estimate | Early inventory; multi-speaker aggregation; adaptation from multilingual bases; budget for targeted recording | 1,3 |
| R-02 | Insufficient Tanglish data — likely the hardest data problem; code-mixed *speech* corpora barely exist | **H** | **H** | Phase 7 inventory | Plan collection early (Phase 0/1, not Phase 7); read-speech elicitation from code-mixed scripts; controlled synthesis only with provenance flags (DR-06), never from prohibited APIs (CX-03) | 0,1,7 |
| R-03 | Poor Tanglish pronunciation — Tamil words read with English phonology or vice versa | H | H | H-06, O-06, TG golden set | Explicit script/language tagging in the frontend; per-token language identity carried into the model; Phase 8 ablations | 2,7,8 |
| R-04 | Unnatural code-switching — audible seam, wrong pause, timbre jump at boundary | H | H | H-06 + O-06 boundary metrics + O-05ii | Prohibit stitching (CX-07); boundary-focused eval from day 1; architecture chosen for single-pass mixed generation | 2,8 |
| R-05 | Speaker inconsistency across languages | M | H | O-05ii within-utterance drift; H-08 | Baseline measured in Phase 3 before adaptation; disentangled conditioning; single-speaker multilingual data if obtainable | 3,8,9 |
| R-06 | Normalization errors on OTP/phone/booking-ID — customer-visible, high severity in a real contact center | M | **H** | §8 exact-match suite, 100% gate | Frozen exact-match suite; release-blocking; context-tagged input from the agent where available | 1,4 |
| R-07 | Latency target missed | M | H | §6 benchmark | Streaming (Phase 5); early feasibility probe in Phase 2 *before* model commitment; disambiguate `Q-01` immediately | 2,5,6 |
| R-08 | Concurrency target missed at acceptable cost | M | H | §7 predicate | Batching/scheduling work in Phase 6; hardware escalation as last resort | 5,6 |
| R-09 | VRAM/RAM limits on low-cost hardware | M | M | F-11/F-12 headroom rule | Quantization sweep; model-size selection informed by C-03 | 2,6 |
| R-10 | Model license forbids commercial use, derivatives or redistribution | M | **H** | §13 card at selection time | License screening as a **Phase 2 selection criterion**, not a Phase 10 discovery; maintain a permissively-licensed fallback candidate | 2,10 |
| R-11 | Dataset license issues (incl. PII in taxi-domain data) | M | H | §13 cards, RS-7 | Two-tier approval; archive license texts; PII field mandatory | 1,7 |
| R-12 | Synthetic-data bias; risk of contaminating with prohibited-API output | M | H | Provenance fields; diversity metrics; human eval | Hard cap on synthetic proportion (TBE); provenance audit (CX-03); never train on prohibited-API audio | 7,8 |
| R-13 | Training/inference mismatch — trained at 24 kHz served at 8 kHz; or normalization differing between training transcripts and inference frontend | **H** | **H** | Env record diff (§12); eval run through the *production* audio path | Freeze the audio contract (`Q-02`) before Phase 3; require evaluation audio to traverse the identical serving path used in production | 0,3,5 |
| R-14 | Regional pronunciation mismatch — wrong Tamil variety for the target customer base | M | M | H-09 with region-matched raters | Resolve `Q-03` in Phase 0/1; recruit region-matched rater panel; region-tagged data | 0,1,3,7 |
| R-15 | Production integration issues — audio format, streaming protocol, timing, cancellation semantics mismatch | M | H | Phase 10 integration; earlier if FR-10 is exercised early | Define API + audio contract in Phase 0/1; run a thin end-to-end integration spike **before** Phase 6 | 1,5,10 |
| R-16 | **Telephony bandwidth blind spot** — quality work at wideband while production is 8 kHz narrowband, making every MOS number unrepresentative | **H** | **H** | Compare MOS at wideband vs through the production codec chain | Resolve `Q-02`; add a narrowband evaluation condition to §5.2 if telephony is confirmed | 0,3,6 |
| R-17 | Evaluation invalidity — ASR-based Tamil/Tanglish WER treated as ground truth; MOS compared across differently-composed rater pools | M | M | Anchor drift; metric–human correlation check | §5.1 caveats enforced; anchors; CMOS for release comparisons; validate O-06 against H-06 before trusting it | 0,3,7 |
| R-18 | Benchmark self-deception — coordinated omission, warm-up leakage, frontend excluded, p99 from small `n` | M | H | Harness review + `n` reported with every percentile | §6 rules explicit and auditable; independent re-run of one config per release | 0,5,6 |
| R-19 | Scope drift — Tanglish work begins before the English/Tamil foundation is stable (violating LR-10) | M | M | Phase gates | Phase 6 MVP gate is a hard precondition for Phase 7 | 6,7 |
| R-20 | Hidden third-party TTS dependency creeps in (a convenience call during data prep, a demo, an eval tool) | L | **H** | RS-7 egress + dependency audit every release | Blocklist in CI; provenance fields; explicit policy in contributor docs | 0–10 |
| R-21 | Voice rights / consent gap for the target speaker | M | H | §13.3 item 6 | Resolve `Q-07`; obtain written consent scoped to commercial use and redistribution before recording | 1,3 |
| R-22 | Frozen golden/normalization sets turn out to be unrepresentative | M | M | Failure analysis on production text once available | Versioned sets; `Q-06` replaces the assumed utterance distribution with real traffic when obtainable | 1,6,10 |

---

## 17. Phase 0 Deliverables

The originally proposed `docs/` tree is a good start. Missing from it: a home for the open-questions/decision log; the concurrency definition (which `PS` singles out); the API/audio contract; the golden test *specification* as distinct from the normalization spec; the regression policy; the environment/reproducibility spec; human-eval operational materials (rater instructions, anchors) which are protocol *artifacts* not prose; and machine-readable schemas — the matrices and registers should be data files validated in CI, with Markdown generated or linked, otherwise they rot.

**Revised structure** [ED]

```
docs/
  00_source/
    problem_statement.md            # verbatim PS + provenance note (see §0)
    open_questions.md               # Q-01..Q-12, owner, blocking-or-not, due phase
    decision_log.md                 # ADR-style; every ED/RR/A with rationale + date
    glossary.md                     # Tanglish, TTFA, C*, matrix language, etc.
  01_contract/
    requirements.md                 # §2 — generated from requirements.yaml
    hard_constraints.md             # §3
    acceptance_criteria.md          # §4, incl. the TBE register with owners
    traceability_matrix.md          # §14 — generated, CI-validated for zero orphans
    conflict_analysis.md            # §15
  02_evaluation/
    evaluation_protocol.md          # §5
    human_eval/
      rater_instructions_en.md
      rater_instructions_ta.md
      rating_form_schema.json
      anchor_set/                   # frozen calibration clips + manifest
      trap_items/
    objective_eval_spec.md          # metric definitions + pinned tool versions
  03_benchmark/
    benchmark_protocol.md           # §6
    concurrency_definition.md       # §7 — separate, because PS demands it explicitly
    cost_methodology.md             # §11
    environment_spec.md             # §12
    env_record.schema.json
  04_testsets/
    normalization_spec.md           # §8 taxonomy + rules
    normalization_cases.yaml        # the frozen cases (authored in Phase 0)
    golden_set_spec.md              # §9 structure + coverage requirements
    golden_manifest.schema.json
    bench_corpus_spec.md            # §6.2 composition (frozen)
  05_governance/
    dataset_spec.md
    dataset_card.schema.json
    model_card.schema.json
    license_matrix.md               # §13, generated from cards
    compliance_process.md           # §13.3
    risk_register.md                # §16 — generated from risk_register.yaml
  06_interfaces/
    api_contract.md                 # FR-10: request/response, streaming, errors, cancellation
    audio_contract.md               # DP-04: SR, format, codec, chunking, loudness
  07_process/
    regression_policy.md            # §10
    release_checklist.md            # §10.4 gate
    phase_gates.md                  # exit criteria for every phase, Phase 0 first
data/
  requirements.yaml                 # machine-readable source of §2
  risk_register.yaml
  tbe_register.yaml                 # every TBE: id, owner, method, due phase
scripts/                            # SPECIFIED in Phase 0, IMPLEMENTED in Phase 1 (RULE 1)
  validate_traceability.py          # fails CI if any requirement is unassigned
  validate_cards.py                 # fails CI if any dataset/model lacks approval
  check_no_thirdparty_tts.py        # CX-02 blocklist
README.md
```

**Note on `scripts/`:** these are *specified* in Phase 0 and *implemented* in Phase 1, respecting RULE 1. Their specifications are Phase 0 deliverables; their code is not.

---

## 18. Phase 0 Exit Gate

Phase 0 is complete when **every** box below is checked. Any unchecked box blocks Phase 1.

| # | Gate item | Evidence | Status |
|---|---|---|---|
| G-00 | **Source-document reconciliation** — if a separate problem-statement document exists, a delta pass has been run and differences resolved | delta note in `00_source/` | **BLOCKING — document not found; see §0** |
| G-01 | All explicit requirements extracted and ID'd | `requirements.yaml`, 84 items | Done (this document) |
| G-02 | Hard constraints separated from design preferences | §3 | Done |
| G-03 | Every requirement has a named human owner | `requirements.yaml` `owner` field | **Open — owners not yet assigned** |
| G-04 | Acceptance criteria written; every unspecified threshold marked TBE with owner + method + due phase | `tbe_register.yaml`, 21 items | Structure done / owners open |
| G-05 | Evaluation methodology exists (objective + human), reproducible | §5 + human-eval materials | Spec done / anchor clips + rater instructions to author |
| G-06 | Benchmark methodology exists, including exclusions and cold-start | §6 | Done |
| G-07 | Concurrency definition frozen with a combined PASS predicate | §7 | Done |
| G-08 | Normalization test categories defined with ambiguity suite | §8 | Taxonomy done / cases to author (≥25/category, ≥40 N-AMB) |
| G-09 | Golden test set structure + coverage requirements defined | §9 | Spec done / items to author |
| G-10 | Benchmark corpus composition frozen | §6.2 | Spec done / corpus to assemble |
| G-11 | Regression policy and release-blocking rules defined | §10 | Done |
| G-12 | Cost methodology defined as formulas with fair-comparison rules | §11 | Done |
| G-13 | Reproducibility environment record schema defined | §12 | Done |
| G-14 | Licensing/compliance process defined, with card schemas and two-tier approval | §13 | Done |
| G-15 | Risk register exists with detection + mitigation + owning phase | §16 | Done |
| G-16 | Traceability matrix complete, **zero unassigned requirements** | §14 | Done |
| G-17 | Open questions logged, each marked blocking / non-blocking with an owner | `open_questions.md`, Q-01..Q-12 | Logged / unanswered |
| G-18 | **Q-01 (latency metric definition) answered** | decision log | **BLOCKING** |
| G-19 | **Q-02 (audio/telephony contract) answered** | `audio_contract.md` | **BLOCKING** — determines whether all Phase 3+ quality work is valid (R-13, R-16) |
| G-20 | Acceptance criteria formally frozen and version-tagged | git tag `phase0@v1` | Open |
| G-21 | Phase 1 entry criteria agreed | `phase_gates.md` | Open |

**Blocking to enter Phase 1: G-00, G-03, G-18, G-19, G-20.**

G-08/G-09/G-10 authoring may overlap the start of Phase 1 **only** if Phase 1's normalization implementation does not begin before G-08 is complete — otherwise the engine is built against a moving target, which is the exact failure Phase 0 exists to prevent.

---

## 19. Critical Review

### 19.1 What requirement are we likely to forget?

**The audio delivery contract, and specifically telephony bandwidth.** `PS` specifies latency to the millisecond and enumerates thirteen resource metrics, but never says sample rate, codec, or channel. For a *contact center*, the audio very plausibly ends up as 8 kHz μ-law over a phone line. If Phases 3–6 train, evaluate, MOS-score and optimize at 22/24 kHz and production is narrowband, **every quality number in the project describes audio no customer ever hears**, and the perceptual ranking of models can genuinely invert under band-limiting. This is the most expensive silent mistake available here.

Close behind:

- **Barge-in / cancellation.** Real voice agents get interrupted constantly. If the engine can't be stopped mid-utterance and free its slot immediately, `C*` in production will be far below `C*` in the benchmark.
- **Response caching.** A taxi agent says "Your driver is arriving" thousands of times a day. A cache of frequent static phrases could dominate the cost and latency picture — and would distort benchmarks if accidentally enabled during measurement.
- **PII in logs.** You will be synthesizing OTPs, phone numbers and addresses. Logging request text for debugging is the default behaviour of every serving stack, and it is a compliance problem here.
- **Production observability** — per-request latency histograms, error taxonomy, audio-quality canaries. The benchmark protocol is thorough; the production monitoring story is absent.
- **Failure behaviour on unhandleable input** — unknown scripts, emoji, very long input, empty input, adversarial input. Part of the contract, and it feeds PERF-13.

### 19.2 What assumption are we making without evidence?

- **That a single model can serve all three languages well.** Plausible, common, unproven for this specific combination. `PS` requires a unified *system*; "one model" is our inference. Phase 2 must treat it as a hypothesis.
- **That Tanglish training data can be acquired at all.** The entire research contribution rests on this, and code-mixed *speech* corpora (as opposed to text) are extremely scarce. If Phase 7 discovers there is no path to data, Phase 8 has nothing to stand on. **Data feasibility should be probed in Phase 0/1, not discovered in Phase 7** — the strongest single objection to the current phase ordering.
- **That "p99 ≤ 500 ms" means TTFA.** Believable, but inferred.
- **That ASR-based WER is meaningful for Tamil and Tanglish.** Addressed in §5.1, worth restating: many TTS reports quietly present Tamil WER as if it were a quality measure. It isn't.
- **That one voice identity is wanted.** `PS` lists "speaker similarity" as a metric — similar to *whom*? A reference voice implies either a target speaker recording or voice cloning, each with different data, consent and licensing consequences (`Q-09`).
- **That the utterance-length distribution in §6.2 resembles production.** It is our construction. If real traffic is 80% short confirmations the latency picture improves; if it's long multi-leg itineraries it worsens.

### 19.3 What requirement is potentially unrealistic?

- **`p99 ≤ 500 ms` interpreted as full end-to-end synthesis** is not achievable for medium/long utterances at 15–20 concurrency on cost-minimized hardware, by any architecture. As TTFA it is demanding but tractable. Must be settled before it becomes a phantom failure.
- **`p99` specifically, at 15–20 concurrency, on cheap hardware.** p99 is dominated by tail effects — batch scheduling, GC, allocator growth, occasional long inputs. Hitting a p99 (not p95) target with minimal headroom is genuinely hard, and the honest resolution is often "buy 20% more headroom", which fights CO-01.
- **"Cost as low as possible" alongside a p99 latency SLO** is an unbounded objective against a hard constraint. Without a cost ceiling or hardware budget this can't be optimized, only argued about (`Q-10`).
- **Speaker consistency across a code-switch boundary at production quality** may be the hardest technical requirement in the document, and it is stated almost in passing.
- **Phase 10's "open source"** may be unachievable depending on the license lineage of whatever gets selected in Phase 2 — which is exactly why redistribution rights must be a Phase 2 selection criterion.

### 19.4 What needs clarification from the problem statement?

| # | Question | Blocking? |
|---|---|---|
| Q-01 | Is `p99 ≤ 500 ms` TTFA or full end-to-end? At what concurrency, and for which utterance-length distribution? | **Yes** |
| Q-02 | Audio delivery contract: sample rate, format, codec, channels. Telephony (8 kHz) or wideband? | **Yes** |
| Q-03 | Which Tamil variety is the target (Chennai colloquial? formal literary? another region? Sri Lankan Tamil?) | Yes, by Phase 1 |
| Q-04 | Is mid-utterance cancellation/barge-in required? | Yes, by Phase 5 |
| Q-05 | Does text arrive complete, or streamed token-by-token from an upstream LLM? | Yes, by Phase 5 |
| Q-06 | What is the real utterance-length and language distribution in production traffic? | No — assumption frozen meanwhile |
| Q-07 | Voice rights: is there a designated speaker, and what consent exists? | Yes, before any recording |
| Q-08 | Should embedded English in Tanglish be Tamil-accented or native-English-like? (C-10) | No — research question for Phase 7 |
| Q-09 | "Speaker similarity" — similar to a specific reference voice, or self-consistency across utterances? | Yes, by Phase 3 |
| Q-10 | Is there a hardware/cost ceiling, and is deployment on owned hardware or rented cloud? | Yes, by Phase 2 |
| Q-11 | Single voice or multiple voices/personas? | By Phase 3 |
| Q-12 | Does the upstream agent provide entity type tags (this is an OTP / this is a booking ID), or must the TTS frontend infer type from raw text? **This substantially changes the difficulty of PN-14.** | Yes, by Phase 1 |

`Q-12` deserves emphasis: if the dialog system can label its own entities, context-aware pronunciation becomes largely a rendering problem. If it can't, it becomes an inference problem with its own latency cost (C-11) and error modes. These are very different Phase 1 projects.

### 19.5 What should NOT be decided in Phase 0?

Model, architecture family, vocoder, acoustic representation, tokenizer/symbol inventory, G2P strategy, whether to romanize or nativize scripts, training data mix, hardware, batching policy, quantization, deployment topology, and the numeric values of any threshold `PS` did not state. Also the *exact* rendering of `open`-determinism normalization cases — those need linguistic evidence, not a Phase 0 opinion.

### 19.6 What decision would be dangerous to lock too early?

**The symbol inventory and script policy.** This is the concrete mechanism by which RULE 9 gets violated. If Phase 3 ships a Tamil model with a Tamil-only phoneme set and an English model with an English-only one, and the frontend decides early that all Tamil is normalized to Tamil script (or all to Latin), then Phase 8 discovers that intra-word code-mixing (`Chennai Central-ல`) has no representation and the fix is a retrain. **Phase 2 must state, in writing, how a mixed-script, mixed-language, intra-word-suffixed utterance would be represented — before any training starts.** That is the operational form of CX-06.

Second: **speaker representation.** A speaker embedding entangled with language identity is very hard to disentangle later, and it is exactly what breaks C-07.

Third: **sample rate / audio contract** — cheap to decide now, expensive after training (R-13).

Fourth: **the normalization output interface.** Whether the frontend emits text, phonemes, or tagged tokens determines what the model can ever condition on. Locking it to plain text may permanently prevent per-token language conditioning.

### 19.7 What should remain experimentally open for Phase 2?

- One unified multilingual model vs. per-language models with a router (a router makes CX-07/no-stitching harder to satisfy, so it carries a burden of proof).
- Autoregressive vs. non-autoregressive vs. diffusion vs. flow-matching decoders — specifically their TTFA-vs-quality profiles under streaming (C-01, C-05).
- Discrete-token vs. continuous-feature intermediate representations.
- Phoneme vs. character vs. byte input, and per-token language tagging.
- Script normalization direction for Tanglish (native-script canonical, Latin canonical, or dual-script native handling) — a genuine research question, not an engineering preference.
- Speaker conditioning mechanism and whether one speaker identity survives all three languages.
- Whether the code-switch boundary needs explicit modelling at all, or emerges from data.
- Adaptation strategy for Phase 8 (full fine-tune / adapters / replay / multi-task).
- Precision and quantization.
- Whether frontend entity disambiguation is rule-based, learned, or supplied upstream (`Q-12`).

---

## 20. Final Phase 0 Checklist

```
SOURCE
[!] G-00  Reconcile against the actual problem-statement document (NOT FOUND — blocking)
[x]       Problem statement captured with provenance note
[x]       Open questions Q-01..Q-12 logged
[ ]       Q-01 (latency metric) answered                          BLOCKING
[ ]       Q-02 (audio/telephony contract) answered                BLOCKING
[ ]       Q-03, Q-04, Q-05, Q-07, Q-09, Q-10, Q-12 routed with due phases

CONTRACT
[x]       84 requirements extracted, ID'd, sourced, M/O-marked, verification named
[x]       12 hard constraints separated from 7 design preferences
[x]       Acceptance criteria written; 21 TBE items explicitly marked, none invented
[ ]       Every requirement assigned a human owner                BLOCKING
[ ]       TBE register: owner + method + due phase for all 21
[x]       Traceability matrix complete — 84/84, zero unassigned
[x]       Conflict analysis: 12 conflicts with resolution paths

EVALUATION
[x]       Objective protocol (O-01..O-06) with Tamil/Tanglish validity caveats
[x]       Human protocol (H-01..H-10): panels, blinding, anchors, traps, sample sizes
[ ]       Rater instructions authored (EN + TA)
[ ]       Anchor set + trap items assembled and frozen
[x]       Eval tooling version-pinning rule (EV-17)

BENCHMARK
[x]       Load model, warm-up, window, repetitions, min-sample-size defined
[x]       Formulas F-1..F-12 defined
[x]       Exclusions and inclusions explicit (frontend INCLUDED; loading EXCLUDED)
[x]       Cold-start protocol separate
[x]       Concurrency definition + 6-condition PASS predicate frozen
[x]       Benchmark corpus composition frozen (assumption flagged, Q-06)

TEST SETS
[x]       Normalization taxonomy N1–N15 + N-AMB defined
[ ]       Normalization cases authored (>=25/category, >=40 N-AMB)
[x]       Golden set structure + coverage requirements for EN / TA / TG-A/B/C
[ ]       Golden items authored to coverage floors
[x]       Freeze/versioning policy defined

PROCESS & GOVERNANCE
[x]       Regression suites RS-0..RS-7, regression definitions, release-blocking rules
[x]       Asymmetric rule protecting Tamil/English against Tanglish regression
[x]       Cost formulas C-0..C-8 + fair-comparison rules
[x]       Environment record schema (hardware/software/model/audio/eval pins)
[x]       Dataset + model card schemas, two-tier approval, lineage rule
[x]       Risk register R-01..R-22 with detection, mitigation, owning phase
[x]       Phase 0 deliverable structure defined and critiqued
[ ]       Acceptance criteria frozen and tagged phase0@v1            BLOCKING
[ ]       Phase 1 entry criteria agreed
```

---

# PHASE 0 FREEZE

## FROZEN — changing any of these invalidates prior results and requires a version bump + re-baseline

1. **The 84 numbered requirements**, their IDs, sources and mandatory/optional status.
2. **The 12 hard constraints** (HC-1…HC-12) and their precedence: HC-11 (quality) and HC-1/HC-2 (self-hosted) outrank HC-8/HC-9 (latency/concurrency), which outrank DP-a (cost).
3. **The acceptance-criteria structure**, including which thresholds are `PS`-given (p99 ≤ 500 ms; concurrency 15–20; 100% exactness on OTP/phone/booking-ID/context-sensitivity) and which are the 21 TBE items.
4. **Metric definitions**: O-01…O-06, H-01…H-10, F-1…F-12, C-0…C-8. Formulas do not change; thresholds may still be set.
5. **The evaluation protocol**: blinding, randomization, anchors, traps, panel composition, per-stratum reporting, mean-with-CI reporting, CMOS for release comparison.
6. **The benchmark protocol**: closed-loop primary with T_think = 3 s, 60 s warm-up discarded, 300 s window, ≥1,000 requests, 3 repetitions, levels {1,5,10,15,20}, coordinated-omission avoidance, and the exclusion/inclusion lists — in particular, **text normalization is inside the latency budget**.
7. **The definition of maximum sustainable concurrency `C*`** and its 6-condition PASS predicate, including latency-slope stationarity and resource headroom.
8. **The benchmark corpus composition** `bench@v1` (35/35/30 language, 40/45/15 length, 30% entity-heavy) — frozen as an assumption pending `Q-06`.
9. **The normalization taxonomy** N1–N15 plus the N-AMB ambiguity suite, and the rule that exact-determinism cases are 100%-or-fail and release-blocking.
10. **The golden test set structure** for EN / TA / TG-A / TG-B / TG-C and their coverage dimensions and floors.
11. **The regression policy**: suites RS-0…RS-7, the stratum-level (never pooled) regression rule, the quality-after-optimization rerun rule, and the asymmetric rule that Tanglish gains may not silently cost Tamil or English.
12. **The cost methodology** and its fair-comparison rules — especially that cost is only ever reported paired with a quality vector, and as a curve rather than a point.
13. **The environment record schema** and the rule that a result without an env record is not a result.
14. **The data/model card schemas**, the two-tier approval process, the most-restrictive-lineage rule, and the CX-03 provenance audit.
15. **The risk register** as a living document — risks may be added or re-scored, never deleted without a recorded resolution.
16. **The traceability discipline**: every future artifact cites requirement IDs; CI fails on an unassigned requirement.

## DELIBERATELY OPEN — must not be decided yet

1. **Model and architecture** (RULES 2–3) — including whether one model or several, and the decoder family.
2. **Acoustic representation, vocoder, tokenizer and symbol/phoneme inventory** — constrained only by CX-06 and the Phase 2 written-representation argument.
3. **Script normalization policy for Tanglish** — native-canonical, Latin-canonical, or dual-script.
4. **G2P strategy** and whether entity disambiguation is rule-based, learned, or upstream-supplied (`Q-12`).
5. **Speaker representation and conditioning mechanism**, and whether one voice serves all three languages.
6. **Training data mix, synthetic-data proportion, and adaptation strategy** for Phase 8.
7. **Hardware, precision, batching policy and deployment topology.**
8. **All 21 TBE thresholds** — to be set by baseline measurement, not by assertion.
9. **Whether embedded English should be Tamil-accented** (`Q-08` / C-10) — an empirical Phase 7 question.
10. **Open-source release scope** — gated on license lineage discovered in Phase 2.
11. **The `open`-determinism normalization renderings** (Indian vs Western number grouping, date order, booking-ID grouping, PIN-code reading, letter-name language) — decided in Phase 1 with recorded rationale.
12. **Exact phase boundaries** — `PS` itself calls the phase list tentative. The only frozen ordering constraint is LR-10 (English+Tamil foundation before Tanglish), plus the recommendation that **Tanglish data feasibility be probed early rather than at Phase 7**.

---

*End of Phase 0 document.*
