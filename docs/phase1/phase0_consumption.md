# Phase 1 — Phase 0 Consumption

**Date:** 2026-08-29
**Source of truth:** `docs/PHASE_0_REQUIREMENTS_FREEZE.md` (1,377 lines, 20
sections). Read in full before any Phase 1 implementation decision.
**Phase 0 was not recreated and not modified.** Issues found are recorded in
`repository_audit.md` §5 with proposed corrections, not applied.

---

## 1. What Phase 0 contains (extracted)

| Phase 0 element | Count / content |
|---|---|
| Requirements | **84** across categories A–M (FR, LR, PN, DR, MR, IR, PERF, CC, CO, EV, DP, DL, CX) |
| Hard constraints | **12** (HC-1 … HC-12) |
| Design preferences | 7 (DP-a … DP-g) |
| TBE thresholds (deliberately unset) | **21** |
| Objective metrics | O-01 … O-06 |
| Human metrics | H-01 … H-10 |
| Benchmark formulas | F-1 … F-12 |
| Cost formulas | C-0 … C-8 |
| Normalization categories | N1 … N15 + N-AMB |
| Conflicts | 12 (C-01 … C-12) |
| Risks | 22 (R-01 … R-22) |
| Open questions | 12 (Q-01 … Q-12) |
| Exit gates | G-00 … G-21, of which 5 are blocking |

## 2. Phase 0 requirements Phase 1 ADDRESSED

| Phase 0 req | What Phase 1 did | Evidence |
|---|---|---|
| **PN-01** numbers | English cardinal/ordinal/decimal verbalizer; Tamil cardinal (preliminary) | `numbers_en.py`, `numbers_ta.py`, tests |
| **PN-02** dates | date detection + verbalization | partial — see xfail XF-001 |
| **PN-03** times | natural time reading incl. `7:05` → "seven oh five", midnight/noon | `TestEnglishNumbers`, case N3-* |
| **PN-04** phone → digit-by-digit | implemented, **EXACT** determinism | cases N4-001…003, all pass |
| **PN-05** OTP → digit-by-digit | implemented, leading zeros preserved | cases N5-001…004, all pass |
| **PN-06** booking ID → char/digit | implemented, separators dropped | cases N6-001…003, all pass |
| **PN-07** addresses | `No.`, `St.`, `Dr.` handling | partial; case N7-001/002 |
| **PN-08** abbreviations | lexicon + letter-spelling + ambiguity resolution | `lexicons/`, case N8-* |
| **PN-09** vehicles | vehicle lexicon | `lexicons/`, seed |
| **PN-10** prices | ₹ / Rs. / "rupees" forms | case N10-* |
| **PN-11** distances | km/m with unit naming | case N11-* |
| **PN-13** locations | Chennai-area seed lexicon | `lexicons/` — **seed only** |
| **PN-14** context-sensitivity | **release-blocking requirement implemented and verified** | `test_ambiguity_pairs_render_differently`, 6 pairs |
| **PN-15** Tamil+English mixed | matrix-language routing of numbers | case N14-002 |
| **PN-16** Tamil in Latin script | `TA_LATIN` language class + lexicon | case N15-001 |
| **PN-17** language-neutral engine | one engine serves EN/TA/TG | all suites use one `Normalizer` |
| **PN-18** rule↔test traceability | every case has an id + `phase0_ref` | `normalization_cases.yaml` |
| **LR-04** Tamil script + English inserts | detected, matrix = TA | case N14-001 |
| **LR-05** Tamil in Latin script | detected, matrix = TA_LATIN | case N15-001 |
| **LR-06** Tamil suffix on English token | tokenizer splits stem/suffix keeping both identities | `test_tamil_suffix_on_english_stem` |
| **CX-06 / RULE 9** don't foreclose Tanglish | no phoneme inventory committed; per-token language preserved | `architecture_audit.md` §3, `tanglish_implications.md` §2 |
| **§16** staged architecture | implemented stage-for-stage | `pipeline.py` |
| **§6.6** frontend inside latency budget | frontend latency measured | `baseline_results.md` §4 |
| **§12** environment record | emitted with the benchmark | `artifacts/frontend_bench.json` |
| **§17/§21** automated tests | 104 pass, 4 xfail | `python -m pytest` |
| **§22** git safety | `.gitignore` written by inspection; no weights/secrets committed | `.gitignore` |
| **§23** model storage design | `models/` + manifest schema; weights routed to D: | `models/README.md` |
| **Q-12** upstream entity tags | pipeline accepts `upstream_entities`, marks provenance | `test_upstream_entities_take_priority` |

## 3. Phase 0 requirements Phase 1 could NOT address

| Phase 0 req | Why | Blocker |
|---|---|---|
| FR-01…FR-08 (synthesis, use cases) | no TTS model exists | **B-01** |
| LR-01/02/03 (EN/TA/TG speech) | no model | B-01 |
| MR-01…MR-07 (model requirements) | no model selected — Phase 2 work | by design |
| IR-01…IR-03 (streaming, real-time, optimization) | no model to serve | B-01 |
| PERF-01…PERF-15 (TTFA, p50/95/99, E2E, GPU/VRAM) | no model; no GPU | B-01 + hardware |
| CC-01…CC-05 (concurrency) | no service to load-test | B-01 |
| CO-01…CO-07 (cost) | no hardware baseline, no throughput | B-01 |
| EV-01…EV-06 (objective quality) | no audio, no ASR/speaker/LID models | B-01 |
| EV-07…EV-15 (human quality) | no audio; rater materials not authored (Phase 0 G-05 open) | B-01 |
| DP-01…DP-04 (deployment, audio contract) | nothing deployed; **Q-02 unanswered** | B-01 + Q-02 |
| PN-12 (person names) | no pronunciation lexicon built | deferred |

## 4. Phase 0 conflicts Phase 1 informs

| Conflict | Phase 1 evidence | Effect |
|---|---|---|
| **C-11** latency vs frontend richness | frontend p99 **0.837 ms** = 0.17 % of the 500 ms budget | **de-risked while the frontend stays rule-based**; must be re-measured if a learned disambiguator is added (Q-12) |
| **C-09** naturalness vs entity exactness | exact forms implemented and passing; prosodic naturalness of digit strings untested | unchanged — still a Phase 4 research question |
| **C-07** speaker vs multilingual | text-side code-switch segmentation now available for O-05(ii) | measurement path prepared |
| **C-10** regional naturalness vs English pronunciation | `ta_digit_language` made a config flag rather than a hard-coded choice | kept open for the Phase 7 A/B study |
| **C-12** open source vs licence lineage | espeak-ng GPL-3.0 risk flagged before any dependency was taken | avoided pre-emptively |

## 5. Phase 0 gates that remain OPEN and affect Phase 2

Phase 0 §18 named five items blocking entry to Phase 1. **All five are still
open.** Phase 1 proceeded anyway and records that as a deviation
(`repository_audit.md` I-03).

| Gate | Status | Impact on Phase 2 |
|---|---|---|
| **G-00** source-document reconciliation | **OPEN** — the original problem-statement document was never found | requirement extraction may be incomplete |
| **G-03** every requirement has a named owner | **OPEN** | no accountability routing |
| **G-18** Q-01 latency metric | **OPEN** | Phase 2 would select against an undefined target |
| **G-19** Q-02 audio contract | **OPEN** | **highest-impact** — determines whether candidate evaluation is even valid (R-13, R-16) |
| **G-20** acceptance criteria tagged `phase0@v1` | **OPEN** — `git tag` shows no tags | contract not formally frozen |

Also open: **G-05** (rater instructions, anchor set, trap items),
**G-08/G-09/G-10** (full case/golden/corpus authoring — Phase 1 delivered seeds
short of the Phase 0 §8.2/§9 floors).
