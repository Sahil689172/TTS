# Phase 1 — Reproducibility Audit

**Date:** 2026-08-29
**Question:** can each existing TTS implementation be reproduced?

---

## 1. Result

> **No TTS implementation exists in this repository, so there is nothing to
> reproduce.** See `repository_audit.md` and `model_inventory.md`.

Per the Phase 1 instruction — *"If something is missing: DO NOT silently guess a
version. Document the blocker."* — the table below records blockers, not
guesses.

## 2. Reproducibility record for the *existing* TTS system

| Field | Status |
|---|---|
| Python version | **N/A — no implementation** |
| PyTorch version | **N/A** |
| Transformers version | **N/A** |
| CUDA version | **N/A** (machine has none; torch is a CPU-only build) |
| OS | Windows 11 build 10.0.26200 (recorded, but nothing depends on it yet) |
| System dependencies | **UNKNOWN** — none declared anywhere |
| Model weights | **ABSENT** |
| Tokenizer | **ABSENT** |
| Configuration | **ABSENT** |
| Environment variables | **NONE DECLARED** |
| Package versions | **NOT PINNED** — no `requirements.txt`, no lockfile, no `pyproject.toml` |
| External downloads | **NONE PERFORMED** |

**Blocker B-02: the repository has no dependency declaration of any kind.**
Even the packages that *are* installed (torch 2.11.0+cpu, transformers 4.57.6,
…) exist only in the ambient system interpreter. Nothing records that they are
required, and nothing pins them.

## 3. Reproducibility of what Phase 1 DID build

The `tnorm` normalization frontend is reproducible, and deliberately so:

| Field | Value |
|---|---|
| Source | `src/tnorm/` (11 modules, all in-repo, no vendored binaries) |
| Runtime dependencies | **Python standard library only** |
| Test dependencies | `pytest`, `PyYAML` (both already present) |
| Model weights | **none — rule-based by design** (Phase 0 §16: "Do NOT build a large ML normalization model") |
| External downloads | **none** |
| Frozen test data | `data/testsets/normalization_cases.yaml` (`norm@v0.1`) |
| Test command | `python -m pytest` |
| Measured result | **104 passed, 4 xfailed in 0.45 s** |
| Determinism | no randomness, no network access, no clock dependence in the normalization path |

The single substantive Phase 1 artifact can therefore be re-run identically by
anyone with a Python 3.x interpreter — the reproducibility property Phase 0
EV-16 asks for.

## 4. Gaps that must be closed before Phase 2

| # | Gap | Why it matters | Recommended fix |
|---|---|---|---|
| G-R1 | No dependency pinning | Phase 0 §12 requires `pip_freeze_hash` and a stored lockfile alongside every result | add `pyproject.toml` + lockfile; use an isolated venv |
| G-R2 | System interpreter is Python **3.13.4** | Many TTS stacks do not yet support 3.13 (risk R-P1 in `environment.md`); using the system interpreter also risks polluting it | dedicated venv; be prepared to pin an older Python for model work |
| G-R3 | No `env_record.json` for anything but the frontend benchmark | Phase 0 §12: "a result without an env record is not a result" | extend the harness once a model exists |
| G-R4 | Evaluation models not pinned | Phase 0 EV-17: swapping ASR/speaker/LID invalidates all historical metrics | pin at first use; record in `models/manifest.yaml` |
| G-R5 | espeak-ng backend unverified | `phonemizer` is installed but its native backend was never exercised | verify before any G2P-dependent decision |
