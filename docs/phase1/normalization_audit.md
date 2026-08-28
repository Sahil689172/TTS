# Phase 1 — Normalization Foundation & Test Audit

**Date:** 2026-08-29
**Covers:** Phase 1 Steps 16, 17, 18 and the mixed-text audit from Step 11.
**Implements:** Phase 0 PN-01 … PN-18, §8 test taxonomy, §16 staged architecture.

---

## 1. What was built

A modular, rule-based, zero-dependency normalization frontend at `src/tnorm/`,
following the Phase 0 §16 stage order exactly.

| Module | Stage | Phase 0 trace |
|---|---|---|
| `scripts.py` | script detection, Tamil-digit folding | §16, §8 N1 |
| `langid.py` | per-token language ID + matrix language | §16, LR-04/05, §8 N14 |
| `tokenizer.py` | tokenization + Tamil-suffix splitting | LR-06, §8 N15 |
| `entities.py` | context-sensitive entity detection | PN-01…PN-14 |
| `numbers_en.py` | English verbalization | PN-01, PN-03 |
| `numbers_ta.py` | Tamil verbalization | PN-01, PN-03 |
| `verbalizer.py` | entity → speech, abbreviation expansion | PN-08, PN-09, PN-13 |
| `lexicons/` | abbreviations, vehicles, Chennai locations | §8 N8, N9, N13 |
| `pipeline.py` | orchestration, output contract | §16 |

**No ML model was built** (Phase 0 §16 explicitly forbids it). **No dependency
was added** — the runtime uses only the Python standard library.

## 2. Test results (measured, 2026-08-29)

```
$ python -m pytest
104 passed, 4 xfailed in 0.45s
```

| Suite | Content | Result |
|---|---|---|
| `test_units.py` | script / langid / tokenizer / entities / numbers / config / pipeline contract | **all pass** |
| `test_normalization_cases.py` | data-driven over `normalization_cases.yaml` | **all pass; 4 xfail** |
| `test_exact_determinism_cases_all_pass` | Phase 0 §4.5 release-blocking gate | **PASS** |
| `test_ambiguity_pairs_render_differently` | Phase 0 PN-14 minimal pairs | **PASS** (6 pairs) |

### 2.1 The release-blocking requirement demonstrably works

Phase 0 PN-14 requires the *same string* to render differently by context.
Verified, measured output:

| Input | Output |
|---|---|
| `Your OTP is 4821.` | `Your O T P is four eight two one.` |
| `The fare is 4821 rupees.` | `The fare is four thousand eight hundred twenty-one rupees.` |
| `Your booking ID is TN45AB1234.` | `Your booking I D is T N four five A B one two three four.` |
| `Your phone number is 9876543210.` | `... nine eight seven six five four three two one zero.` |
| `OTP: 0042` | `O T P: zero zero four two` (leading zeros preserved) |
| `St. Thomas Mount` | `saint Thomas Mount` |
| `3rd Cross St.` | `third Cross street.` |
| `Dr. Kumar is waiting.` | `doctor Kumar is waiting.` |
| `Palm Grove Dr.` | `Palm Grove drive.` |
| `No. 12, 3rd Cross St` | `number twelve, third Cross street` |
| `No, that is wrong.` | `No, that is wrong.` (negative control — not "number") |
| `Your cab will arrive at 7:05.` | `... seven oh five.` |

### 2.2 Mixed-language handling (Phase 1 Step 11, against the frontend)

| Input | Output | Matrix | Code-mixed |
|---|---|---|---|
| `உங்கள் pickup location எங்கே?` | unchanged (no entities) | **ta** | yes |
| `unga pickup location enga?` | unchanged | **ta-latn** | yes |
| `Chennai Central-ல இருக்கா?` | `Chennai Central ல இருக்கா?` | **ta** | yes |
| `Driver இன்னும் 5 minutes-ல வருவார்.` | `Driver இன்னும் ஐந்து நிமிடம் ல வருவார்.` | **ta** | yes |
| `உங்கள் OTP 4821.` | `உங்கள் O T P நான்கு எட்டு இரண்டு ஒன்று.` | **ta** | yes |

The fourth row demonstrates the Phase 0 §8 N14 rule that **number reading
follows the matrix language, not the digit's script**: `5` inside a Tamil
sentence reads as `ஐந்து`, not "five".

## 3. Bugs found and fixed during Phase 1

Recorded because they are the kind of defect the frozen test set exists to
catch:

| # | Bug | Fix |
|---|---|---|
| B1 | Time regex consumed the sentence-final period (`7:30 PM.` → meridiem swallowed `.`) | meridiem matched as `PM` or `P.M.` only, never `PM.` |
| B2 | `St. Thomas Mount` → `saint. Thomas Mount` (stray abbreviation period) | period dropped after an expanded abbreviation unless it ends the sentence |
| B3 | `No. 12` not expanded to `number` | context rule: `No` → `number` only when a digit follows; bare `No` untouched |
| B4 | `Central-ல` → `Centralல` (mixed-script word created) | suffix emitted as a separate whitespace-delimited unit |
| B5 | Tokenizer never saw `Central-ל` as one unit (hyphen consumed as punctuation first) | suffix detection moved to **chunk level**, before sub-word regex |

B5 is the most significant: the original design could not have implemented
LR-06 at all.

## 4. Known failures and gaps — NOT hidden

Four cases are marked `xfail` in the frozen set with explicit reasons:

| ID | Category | Gap |
|---|---|---|
| XF-001 | date | English date phrasing emits `<ordinal> <Month> <year>` without "of"; canonical form not finalised (OPEN determinism) |
| XF-002 | number | Indian comma grouping `1,50,000` parses, but the lakh/thousand composition wording is unverified |
| XF-003 | Tamil number | Tamil price/number forms are **UNVALIDATED by a native speaker** |
| XF-004 | PIN code | bare 6-digit after a city name not recognised as a PIN code; needs location-lexicon lookup |

### 4.1 Coverage shortfall against Phase 0 §8.2 — OPEN GAP

Phase 0 §8.2 requires **≥25 cases per category** and **≥40 in N-AMB**, with
≥30 % Tamil-context and ≥20 % Tanglish-context.

**Actual:** 46 cases total; 12 in the ambiguity suite (6 pairs); most categories
have 2–5 cases.

> **This does not meet the Phase 0 §8.2 floor and is recorded as an open Phase 1
> exit gap.** The *structure*, *schema* and *determinism labelling* are in
> place; only case **count** is short. Authoring to the full floor is
> mechanical but must be done by, or reviewed by, a Tamil speaker.

### 4.2 Tamil verbalization is UNVALIDATED — the most important caveat

`numbers_ta.py` carries an explicit status banner: **PRELIMINARY, NOT VALIDATED
BY A NATIVE SPEAKER.** Documented limitations:

- **L1** — sandhi/combining forms implemented for tens and hundreds only.
- **L2** — numbers above 9,99,999 use a plausible but unverified composition;
  the pipeline emits a runtime **warning** for these.
- **L3** — colloquial Chennai speech differs from the literary forms used
  (e.g. `ஏழரை` vs `ஏழு முப்பது` for 7:30). Deliberately OPEN — this is exactly
  the Phase 0 LR-08 / H-09 regional-naturalness question.
- **L4** — whether Tamil speakers use **Tamil or English digit names** inside
  OTPs and phone numbers is an open research question (Phase 0 §8 N6). It is a
  **config flag** (`ta_digit_language`), not a hard-coded assumption.

No Tamil output is asserted as *correct* anywhere in the test suite. Tamil
tests pin **current behaviour** so changes are detected; they do not claim
linguistic validity. See `PHASE 1 ACTIONS FOR USER`, action **A-04**.

### 4.3 Language identification is a lexicon, not a solved problem

`langid.py` separates EN from TA_LATIN using a closed lexicon (~120 romanized
Tamil forms, ~80 strong-English forms) plus five orthographic cues. **No
accuracy figure is reported, because no labelled TA-Latin evaluation set
exists.** Known failure modes:

- Romanized Tamil outside the lexicon with no orthographic cue defaults to EN.
- Spelling variation (`enga`/`engae`/`engey`, `pannunga`/`panunga`) is only
  partly covered.
- Genuine ambiguities (`car`, `auto`, `driver`, `ok`) are Tamil *and* English;
  currently resolved by lexicon precedence, not by context.

This is a **measured limitation, not a claim of adequacy**. Phase 0 §5.1's
warning about Latin-script Tanglish having no canonical orthography applies
directly here.

## 5. Configuration = Phase 0 OPEN decisions

Every Phase 0 `open`-determinism decision is a `NormConfig` field rather than
hard-coded behaviour, so Phase 2/7 can settle them without a code change:

| Field | Phase 0 ref | Default | Alternatives |
|---|---|---|---|
| `grouping` | §8 N1 | `indian` (lakh/crore) | `western` |
| `date_order` | §8 N2 | `dmy` | `mdy` |
| `ta_digit_language` | §8 N6 | `ta` | `en` |
| `booking_id_grouping` | §8 N6 | `char` | grouped (not implemented) |

Verified by `TestConfiguration` that changing these changes the output.

## 6. Training/inference representation audit (Phase 1 Step 18)

| Side | Representation |
|---|---|
| **Normalizer output** | normalized orthographic text (mixed script preserved) + per-segment `(text, lang)` tags + typed entities |
| **Model expectation** | **UNKNOWN — no model exists** |

**Mismatch cannot yet be measured.** What Phase 1 can state:

1. The frontend deliberately does **not** emit phonemes (see
   `architecture_audit.md` §3), so no symbol inventory has been committed to —
   protecting Phase 0 CX-06 / RULE 9.
2. The output **retains mixed script**. A model whose tokenizer covers only one
   script will fail on this output. That is a **selection criterion for Phase 2**,
   not a frontend defect.
3. `lang_segments` is emitted but **nothing consumes it yet**. If the Phase 2
   model cannot condition on language, this signal is discarded and the
   Tanglish risk rises sharply.
4. Phase 0 conflict **C-11** (latency budget vs frontend richness) is measured
   and currently **not a concern**: frontend p99 is **0.84 ms** (see
   `baseline_results.md`), roughly 0.17 % of the 500 ms budget.

## 7. Honest summary

**Works and is verified:** the staged architecture; context-sensitive entity
detection including all Phase 0 exact-determinism categories; the ambiguity
minimal pairs; English verbalization; Tamil-suffix splitting on English stems;
matrix-language routing of numbers; language segmentation for downstream
conditioning; zero-dependency reproducibility.

**Does not work / not established:** Tamil verbalization correctness
(unvalidated); TA-Latin language ID accuracy (unmeasured); Phase 0 §8.2 case
counts (not met); date phrasing; PIN-code detection without a trigger;
address parsing beyond `No.`/`St.`/`Dr.`; person-name pronunciation (untouched
— Phase 0 PN-12 is effectively deferred); any phonetic representation.
