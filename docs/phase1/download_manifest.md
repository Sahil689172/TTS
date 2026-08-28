# Phase 1 — Download Manifest

**Date:** 2026-08-29
**Rule observed:** Phase 1 Step 5/6 — *audit before download*, and *stop for
approval* on anything large, gated, license-restricted or GPU-dependent.

---

## 1. Downloads performed during Phase 1

> **NONE. Zero bytes of model weights or datasets were downloaded.**
> Zero packages were installed.

The normalization frontend was built using only the Python standard library
plus PyYAML, which was already present. This was a deliberate choice so that
Phase 1 added no supply-chain surface and no disk pressure to a drive with
16.4 GB free.

## 2. Why nothing was downloaded

1. **The audit found no existing system**, so there was no "make the existing
   implementation run" case that Step 6 permits normal installation for.
2. **Phase 1 is not model selection** (explicit in both Phase 0 RULE 2 and the
   Phase 1 brief). Downloading candidate models now would prejudge Phase 2.
3. **Disk reality:** the project drive C: has 16.4 GB free and is
   OneDrive-synced (see `environment.md` §2).
4. **Phase 0 Q-01 and Q-02 are unanswered.** Q-02 in particular (telephony
   8 kHz vs wideband) changes which candidates are even sensible, because a
   model's native sample rate determines whether its quality survives the
   delivery path (Phase 0 risk R-13/R-16). Downloading before Q-02 is answered
   risks evaluating the wrong thing.

## 3. Manifest — items that WOULD be required, by purpose

Nothing below has been downloaded. Each row states what the item is *for*, so
Phase 2 can approve selectively rather than all at once.

Legend — **REQUIRED**: Phase 2 cannot proceed without an item of this class.
**OPTIONAL**: useful, deferrable. **NOT REQUIRED FOR PHASE 1**: explicitly out
of scope now.

| # | Item (class, not a selection) | Purpose | Source | Exact ID | Revision | Approx size | License | Required HW | Disk | Needed for Phase 1? | Skippable? | Storage location |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D-1 | **espeak-ng** (system binary) | G2P backend that `phonemizer` needs; also the fallback intelligibility check | OS package / GitHub release | `espeak-ng` | UNKNOWN | ~10–30 MB | GPL-3.0 — **copyleft; see §5** | CPU | <50 MB | **NO** — not needed for the rule-based normalizer | **YES, skip now** | system install |
| D-2 | **Multilingual TTS candidate A** (supports Tamil) | Phase 2 candidate evaluation | Hugging Face | **UNDECIDED — Phase 2** | UNKNOWN | 0.5–3 GB typical | UNKNOWN | GPU preferred; CPU uncertain | ~5 GB | **NO** | **YES** | `D:\tts-models\candidates\` |
| D-3 | **English-only TTS candidate** | English baseline | Hugging Face | **UNDECIDED — Phase 2** | UNKNOWN | 0.1–2 GB | UNKNOWN | CPU feasible for small models | ~3 GB | **NO** | **YES** | `D:\tts-models\english\` |
| D-4 | **Tamil TTS / multilingual checkpoint** | Tamil baseline | Hugging Face / IndicTTS-family | **UNDECIDED — Phase 2** | UNKNOWN | UNKNOWN | UNKNOWN — **many Indic corpora are non-commercial** | UNKNOWN | ~5 GB | **NO** | **YES** | `D:\tts-models\tamil\` |
| D-5 | **ASR model (English)** | Phase 0 O-01/O-02 WER/CER scoring | Hugging Face | **UNDECIDED** | UNKNOWN | 0.1–3 GB | UNKNOWN | CPU feasible (slow) | ~3 GB | **NO** — nothing to transcribe yet | **YES** | `D:\tts-models\eval\` |
| D-6 | **ASR model (Tamil)** | Tamil WER — **with the Phase 0 §5.1 caveat that Tamil ASR-WER is only a relative tripwire** | Hugging Face | **UNDECIDED** | UNKNOWN | UNKNOWN | UNKNOWN | CPU feasible (slow) | ~3 GB | **NO** | **YES** | `D:\tts-models\eval\` |
| D-7 | **Speaker encoder** | Phase 0 O-05 speaker similarity, incl. cross-code-switch drift | Hugging Face | **UNDECIDED** | UNKNOWN | ~50–500 MB | UNKNOWN | CPU feasible | ~1 GB | **NO** | **YES** | `D:\tts-models\eval\` |
| D-8 | **Spoken LID model** | Phase 0 O-06 code-switch language-ID consistency | Hugging Face | **UNDECIDED** | UNKNOWN | UNKNOWN | UNKNOWN | CPU feasible | ~1 GB | **NO** | **YES** | `D:\tts-models\eval\` |
| D-9 | **Tamil speech corpus** | Phase 0 DR-01 | UNKNOWN | **UNDECIDED** | UNKNOWN | 1–50 GB | **UNKNOWN — commercial use is the key question** | n/a | up to 50 GB | **NO** | **YES** | `D:\tts-datasets\` |
| D-10 | **Tanglish speech corpus** | Phase 0 DR-02 — the project's highest-risk data dependency (risk R-02) | **likely does not exist off-the-shelf** | N/A | N/A | UNKNOWN | UNKNOWN | n/a | UNKNOWN | **NO** | **YES** | `D:\tts-datasets\` |
| D-11 | `num2words` (pip) | number verbalization | PyPI | `num2words` | latest | <1 MB | LGPL-2.1 | CPU | negligible | **NO — deliberately avoided** | **YES — already replaced** | n/a |
| D-12 | `indic-transliteration` (pip) | Latin↔Tamil transliteration | PyPI | `indic-transliteration` | latest | ~5 MB | MIT | CPU | negligible | **OPTIONAL** — would improve TA-Latin handling | **YES for now** | venv |

## 4. Items requiring explicit user approval before download

Per Step 6, the following are flagged **DOWNLOAD APPROVAL REQUIRED** and were
not fetched:

- **D-2, D-3, D-4** — TTS model weights. Large, license-unknown, and their
  choice *is* the Phase 2 decision.
- **D-5 … D-8** — evaluation models. Large; and pinning them is a Phase 0
  EV-17 commitment (swapping them later invalidates all historical metrics), so
  they should be chosen deliberately, not casually.
- **D-9, D-10** — datasets. Potentially tens of GB, and the licence question
  (commercial use, redistribution, derivative models) is a Phase 0 HC-10 legal
  gate, not a convenience.

**Approval is not requested in Phase 1**, because Phase 1 does not need any of
them. They are listed so Phase 2 begins with a costed, licence-aware shopping
list rather than ad-hoc downloads.

## 5. Licence warnings recorded now (Phase 0 CX-04 / HC-10)

- **espeak-ng is GPL-3.0.** If it ends up inside the shipped speech-generation
  path, its copyleft terms propagate to the distributed system. Phase 0 DL-07
  commits the project to an open-source release, so this may be acceptable —
  but it is a decision, not a detail, and must be made consciously in Phase 2.
- **Indic speech corpora frequently carry non-commercial or research-only
  terms.** A taxi contact-centre is a commercial deployment. Phase 0 §13.3's
  two-tier `research_only` / `production_approved` split exists precisely for
  this, and every dataset must be classified before use.
- **`derivative_model_allowed` is the field most often overlooked** (Phase 0
  §13.1). A model trained on a research-only corpus may itself be
  undistributable, which would break DL-07.

## 6. Storage design (applies to every future download)

```
D:\tts-models\          <- TTS_MODEL_ROOT, ~475 GB free, NOT OneDrive-synced
├── english\
├── tamil\
├── candidates\
└── eval\               <- ASR, speaker encoder, LID (Phase 0 EV-17 pins)

D:\tts-datasets\        <- corpora
```

Never inside the repository: C: has 16.4 GB free and is OneDrive-synced.
`.gitignore` enforces the Git side; `models/manifest.yaml` records what was
fetched, from where, at which revision, under which licence, and at which
approval tier.

## 7. Bandwidth/disk budget if everything above were approved

| Group | Approx disk |
|---|---|
| TTS candidates (D-2..D-4) | ~13 GB |
| Evaluation models (D-5..D-8) | ~8 GB |
| Datasets (D-9, D-10) | up to 50 GB+ (**UNKNOWN**) |
| **Total** | **~21 GB + datasets** |

All of this fits comfortably on **D:** and none of it fits safely on **C:**.
