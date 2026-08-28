# Phase 1 — Model Inventory

**Date:** 2026-08-29
**Scope:** every English/Tamil TTS model *currently referenced or implemented*
in this repository.

---

## 1. Result

> **The inventory is EMPTY. Zero TTS models are referenced, implemented,
> configured or downloaded in this repository.**

This is a measured result, not an omission. Evidence:

- `git ls-files` returns exactly one file: `docs/PHASE_0_REQUIREMENTS_FREEZE.md`
- No `.py` source existed before Phase 1
- No `config.json`, `tokenizer.json`, `vocab.*`, `*.model` anywhere in the tree
- No `.pt / .pth / .ckpt / .safetensors / .bin / .onnx` anywhere in the tree
- No `requirements.txt` / `pyproject.toml` naming any TTS package
- `TTS` (Coqui) is **not installed** in the Python environment

Per the Phase 1 instruction ("If information is unavailable: write UNKNOWN.
NEVER invent information"), the per-model table below is therefore filled with
the only honest content available.

## 2. English TTS model

| Field | Value |
|---|---|
| Model name | **NONE PRESENT** |
| Repository / source | N/A — no model referenced |
| Exact model ID | N/A |
| Version / revision | N/A |
| Architecture | N/A |
| Parameter count | N/A |
| Checkpoint size | N/A |
| Tokenizer | N/A |
| Text representation | N/A |
| Phoneme / G2P | N/A |
| Vocoder | N/A |
| Sampling rate | N/A |
| Speaker representation | N/A |
| Language support | N/A |
| Inference framework | N/A |
| Python requirements | N/A |
| CUDA requirements | N/A |
| CPU requirements | N/A |
| RAM requirement | N/A |
| GPU requirement | N/A |
| License | N/A |
| Model card / source URL | N/A |
| Weights already local? | **NO** |
| Local checkpoint path | N/A |
| Runs on current hardware? | **N/A — nothing to run** |

## 3. Tamil TTS model

Identical result. **NONE PRESENT.** Every field above is N/A for the same
reason and on the same evidence.

## 4. Vocoder / G2P / tokenizer components

| Component | Present? | Notes |
|---|---|---|
| Vocoder (any) | **NO** | no code, no weights |
| G2P engine | **NO** | `phonemizer` 3.3.2 is installed as a *library*, but no G2P is configured, no lexicon exists, and the espeak-ng native backend is **NOT VERIFIED** |
| Tokenizer | **NO** | `transformers` 4.57.6 is installed but no tokenizer artifact exists |
| Speaker encoder | **NO** | — |
| ASR (for Phase 0 O-01/O-02 WER) | **NO** | required later for objective evaluation; none present |

## 5. Search performed elsewhere on the machine

The Phase 1 brief asks whether weights are "already downloaded". Checked:

- No `models/`, `checkpoints/` or weights directory existed in the project.
- No Hugging Face cache was found under project control.
- **Not searched:** the user's whole filesystem outside the project. If TTS
  models exist elsewhere on this machine (for example under
  `%USERPROFILE%\.cache\huggingface`), Phase 1 did not locate them and they are
  not registered. If such models exist, report them — see
  `PHASE 1 ACTIONS FOR USER`, action **A-01**.

## 6. What this means for Phase 1 steps

| Phase 1 step | Status |
|---|---|
| Step 3 — inventory existing models | **DONE — result is empty** |
| Step 4 — hardware feasibility per model | **VACUOUS** — no models to classify; see `download_manifest.md` for candidate *classes* instead |
| Step 7 — reproducibility audit | **BLOCKED** — nothing to reproduce |
| Step 9 — English baseline | **BLOCKED — blocker B-01** |
| Step 10 — Tamil baseline | **BLOCKED — blocker B-01** |
| Step 11 — mixed-text audit against existing systems | **BLOCKED** for TTS; performed against the **normalization frontend** instead (see `normalization_audit.md`) |
| Step 13 — quality baseline | **BLOCKED** — no audio can be produced, and no ASR is present to score it |
| Step 14 — architecture reverse-engineering | **BLOCKED** — nothing to reverse-engineer |
| Step 15 — speaker audit | **BLOCKED** — see `speaker_audit.md` |
| Step 18 — training/inference representation mismatch | **PARTIALLY POSSIBLE** — the normalizer's *output* contract is documented; the *model's expectation* is unknown until Phase 2 |

## 7. Classification per Phase 1 Step 4

Since no models exist, the Step 4 classification applies to the *only* concrete
artifact Phase 1 produced:

```
tnorm (normalization frontend, this repository)
------------------------------------------------
Status         : LOCAL_CPU_FEASIBLE
Reason         : pure-Python, standard library + PyYAML, no model weights
Expected VRAM  : none
Measured p99   : 0.84 ms/utterance (DEVELOPMENT MACHINE BASELINE)
Local execution: FEASIBLE - verified, 104 tests pass
```

All TTS model classification is deferred to `download_manifest.md`, which
classifies candidate *classes* by hardware requirement without naming a
selection (Phase 0 RULE 2, Phase 1 "Phase 1 is not model selection").
