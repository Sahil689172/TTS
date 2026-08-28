# Phase 1 — Requirements for Phase 2 Model Selection

**Date:** 2026-08-29
**Scope:** Phase 1 Step 20. **No model is chosen here** (Phase 0 RULE 2).

Each item is labelled:
**[P0]** Phase 0 requirement · **[P1F]** Phase 1 finding (evidence-based) ·
**[ER]** engineering recommendation (judgement, not evidence).

---

## 1. Mandatory screening criteria — a candidate failing any of these is out

| # | Criterion | Label | Trace / evidence |
|---|---|---|---|
| S-01 | Self-hostable; no hosted TTS API in the generation path | **[P0]** | HC-1, HC-2, CX-01…CX-03 |
| S-02 | Licence permits **commercial** use | **[P0]** | HC-10; taxi contact centre is commercial |
| S-03 | Licence permits **derivative models** | **[P0]** | §13.1 "the field most often overlooked"; Stage 2 requires adaptation |
| S-04 | Licence permits **redistribution** of weights, or the release scope is consciously narrowed | **[P0]** | DL-07 + conflict C-12 |
| S-05 | Tokenizer/symbol inventory can represent **Tamil and Latin script simultaneously** | **[P0]+[P1F]** | CX-06; frontend emits mixed-script text (`normalization_audit.md` §6) |
| S-06 | Streaming inference is supported or implementable | **[P0]** | IR-01, HC-7 |
| S-07 | Tamil is supported, or is reachable by adaptation from a documented base | **[P0]** | HC-4 |

## 2. Evidence-driven criteria arising specifically from Phase 1

| # | Criterion | Label | Why — Phase 1 evidence |
|---|---|---|---|
| E-01 | **Record the model's native sample rate** and whether it survives the delivery path | **[P0]+[P1F]** | Phase 0 Q-02 unanswered; R-13/R-16. Until Q-02 is answered, a candidate's quality at 8 kHz is unknown, and MOS at 24 kHz may be meaningless |
| E-02 | **Language conditioning mechanism** must be documented per candidate | **[P1F]** | the frontend emits `lang_segments`; a model that cannot consume it discards the main Tanglish input signal |
| E-03 | **Speaker/language separability** must be documented | **[P0]+[P1F]** | C-07, MR-06; `speaker_audit.md` §4 |
| E-04 | **Input representation** (grapheme / phoneme / byte / subword) must be documented | **[P1F]** | frontend deliberately emits text, not phonemes (`architecture_audit.md` §3); the G2P decision rides on this |
| E-05 | **CPU inference feasibility** must be tested, not assumed | **[P1F]** | dev machine has no NVIDIA GPU, CPU-only torch, and had **2.6 GB RAM free**; a CPU path preserves local iteration |
| E-06 | **Python 3.13 compatibility** must be checked early | **[P1F]** | system interpreter is 3.13.4; many TTS stacks lag (risk R-P1, `environment.md` §5) |
| E-07 | **Peak RAM and VRAM** must be recorded per candidate | **[P0]** | PERF-11/12; §7 headroom clause |
| E-08 | Prefer candidates whose **G2P is not GPL-encumbered**, or accept the copyleft consciously | **[ER]** | espeak-ng is GPL-3.0 and would propagate into a DL-07 open-source release (`download_manifest.md` §5) |

## 3. Measurement obligations Phase 2 inherits

| # | Obligation | Label | Note |
|---|---|---|---|
| M-01 | Benchmark on **GPU hardware**, not this laptop | **[P0]+[P1F]** | HC-8/HC-9 cannot be validated locally (`environment.md` §7) |
| M-02 | Frontend latency must be **included** in every end-to-end measurement | **[P0]** | §6.6 |
| M-03 | Re-measure the frontend if a **learned** disambiguator is introduced | **[P1F]** | currently 0.84 ms p99 = 0.17 % of budget; a model-based frontend would change this by orders of magnitude |
| M-04 | Pin ASR / speaker-encoder / LID versions **at first use** | **[P0]** | EV-17; swapping later invalidates all history |
| M-05 | Report every metric **per language stratum**, never pooled | **[P0]** | §5.0; pooling hides Tamil/Tanglish regressions behind English gains |
| M-06 | Treat Tamil/Tanglish ASR-WER as a **relative tripwire only** | **[P0]** | §5.1 |

## 4. Comparison matrix Phase 2 must fill (one row per candidate)

```
name | model_id | revision | licence | commercial? | derivative? | redistribute?
architecture | AR/NAR | params | ckpt size
input repr | tokenizer script coverage | G2P dependency | G2P licence
language conditioning? | speaker conditioning | speaker/lang separable?
native sample rate | streaming? | batching?
CPU feasible? | CPU RAM peak | GPU VRAM peak | py3.13 ok?
EN quality | TA quality | mixed-script input accepted?
```

Every cell unknown at selection time must read **UNKNOWN**, not be inferred.

## 5. Open Phase 0 questions that gate Phase 2

Phase 2 should **not** begin candidate downloads until these are answered:

| Q | Question | Why it gates Phase 2 |
|---|---|---|
| **Q-01** | Is p99 ≤ 500 ms TTFA or end-to-end? | it is the target being selected *against*; the two readings admit different architectures (Phase 0 §19.3 judges full-E2E unachievable) |
| **Q-02** | Audio contract — telephony 8 kHz or wideband? | determines whether a candidate's native sample rate is appropriate; R-16 makes this the largest silent risk |
| **Q-10** | Hardware/cost ceiling; owned vs rented GPU | bounds which model sizes are admissible at all |
| **Q-12** | Does the dialog system supply entity tags? | decides whether the frontend stays rule-based (0.84 ms) or needs inference (C-11) |
| Q-03 | Target Tamil variety/region | affects data and rater panel selection |
| Q-09 / Q-11 | Speaker: reference voice or self-consistency; one voice or several | changes the data, consent and cloning requirements entirely |

## 6. What Phase 2 should investigate experimentally

**[ER]** — recommendations, deliberately not decisions:

1. **One unified multilingual model vs per-language models + router.** Phase 0
   DP-b leaves this open; note a router makes CX-07 (no stitching) harder to
   satisfy and carries a burden of proof.
2. **Script normalization direction for Tanglish** — native-script canonical,
   Latin canonical, or dual-script. Phase 1 kept both representable; Phase 2
   should test which the model handles better rather than assuming.
3. **Whether `lang_segments` measurably improves code-switch quality**, or
   whether it emerges from data alone.
4. **CPU-only viability at low concurrency**, as a cost floor for Phase 0 CO-01.
5. **Acoustic realisation of a stranded Tamil suffix** (`Central` + `ல`) — an
   open representation question surfaced by Phase 1.

## 7. Explicitly NOT decided by Phase 1

Model, architecture family, vocoder, tokenizer, symbol inventory, G2P strategy,
script canonicalisation direction, speaker representation, training data mix,
hardware, precision, batching policy — all remain open per Phase 0 RULES 2–3 and
the PHASE 0 FREEZE "deliberately open" list.
