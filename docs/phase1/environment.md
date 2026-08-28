# Phase 1 — Local Environment Report

**Date:** 2026-08-29
**Purpose:** Phase 0 §12 reproducibility record for the development machine.
**Method:** measured on this machine via Python (`platform`, `ctypes`,
`shutil.disk_usage`, `torch`). No system configuration was changed; no GPU
driver or CUDA setting was touched.

> **Label for every number produced on this machine: DEVELOPMENT MACHINE
> BASELINE.** Phase 0 HC-9 (15–20 sustainable concurrency) and HC-8 (p99
> latency) **cannot** be validated here and must be benchmarked later on
> appropriate GPU hardware.

---

## 1. Measured hardware

| Field | Measured value | Notes |
|---|---|---|
| OS | Windows 11, build 10.0.26200 (`Windows-11-10.0.26200-SP0`) | |
| Architecture | AMD64 | |
| CPU (reported) | `Intel64 Family 6 Model 154 Stepping 4, GenuineIntel` | Family 6 Model 154 = Alder Lake-P, consistent with the stated **Intel Core i7-1255U** |
| Logical cores | **12** | i7-1255U = 10 physical (2P + 8E) / 12 threads — consistent |
| Physical core split | UNKNOWN (not directly measurable; `wmic` absent on this system) | |
| Total RAM | **15.68 GB** | consistent with stated 16 GB |
| Available RAM at measurement | **2.60 GB** (83 % memory load) | see §4 — this is a live constraint |
| Dedicated NVIDIA GPU | **NONE** | `torch.cuda.is_available() == False` |
| Integrated GPU | Intel Iris Xe (per user statement) | **not independently verified** — `Win32_VideoController` query unavailable, see §5 |
| CUDA runtime | **None** (`torch.version.cuda is None`) | |

## 2. Measured storage — CORRECTION TO THE STATED FIGURE

The Phase 1 brief states "approximately 954 GB total, approximately 494 GB
currently free". That total is correct **only as the sum of two drives**, and
the free space is **not** on the drive holding the project.

| Drive | Total | Used | Free |
|---|---|---|---|
| **C:** (holds the repository) | 463.6 GB | 447.2 GB | **16.4 GB** |
| **D:** | 488.3 GB | 13.1 GB | **475.2 GB** |
| Sum | 951.9 GB | 460.3 GB | 491.6 GB |

**Consequences, which are material to Phase 2:**

1. The project drive **C: has only 16.4 GB free**. A single mid-size TTS
   checkpoint plus its dependencies can consume a meaningful fraction of that.
   Downloading models into the repository is **not viable**.
2. The repository is inside **OneDrive**
   (`C:\Users\hp\OneDrive\Desktop\TTS`; `OneDrive=C:\Users\hp\OneDrive`).
   Weights written into the repo would be uploaded to OneDrive.
3. **All model weights, datasets and generated audio must be stored on D:.**
   `models/README.md` specifies `D:\tts-models` and the `TTS_MODEL_ROOT`
   environment variable. `.gitignore` prevents accidental commits.

## 3. Measured software stack

| Package | Version | Relevance |
|---|---|---|
| Python | **3.13.4** (`C:\Python313\python.exe`) | see §5 risk R-P1 |
| pip | 26.1.2 | |
| torch | **2.11.0+cpu** | **CPU-only build** — no CUDA even if a GPU appeared |
| torchaudio | 2.11.0+cpu | |
| transformers | 4.57.6 | |
| numpy | 2.3.1 | |
| scipy | 1.18.0 | |
| soundfile | 0.13.1 | audio I/O available |
| librosa | 0.11.0 | audio analysis available |
| phonemizer | 3.3.2 | present, but **espeak-ng backend NOT verified** |
| onnxruntime | 1.24.4 | CPU inference path available |
| pytest | 8.4.2 | |
| PyYAML | 6.0.2 | |
| regex | 2026.1.15 | |
| torch threads | 10 | default intra-op threads |

**Not installed** (checked explicitly): `num2words`, `indic_transliteration`,
`espeakng`, `TTS` (Coqui).

Phase 1 deliberately installed **nothing**. The normalization frontend was
implemented with the standard library plus PyYAML (already present), so Phase 1
added zero dependencies and performed zero downloads.

## 4. Live resource constraint

At measurement time only **2.60 GB of 15.68 GB RAM was available** (83 % load).
This is not a hardware limit but a current-usage condition, and it matters:

- A model needing >2.5 GB resident would fail or swap **today** without closing
  other applications.
- Any Phase 1 memory measurement taken in this state would be misleading.
- **Recorded as blocker input, not as a hardware verdict.** Before any local
  inference attempt, free memory should be re-measured on a freshly-booted
  machine.

## 5. Unknowns and unverified items — recorded, not guessed

| Item | Status | Why |
|---|---|---|
| Integrated GPU model / driver version | **UNVERIFIED** | PowerShell failed in this session (`InitialSessionState` type-initializer exception); `wmic` is absent on this Windows build. The Iris Xe claim comes from the user, not from measurement. |
| Physical vs logical core split | **UNKNOWN** | same tooling gap |
| espeak-ng backend availability | **NOT VALIDATED** | `phonemizer` is installed but its native backend was not exercised. Relevant because most open TTS frontends depend on it. |
| OpenVINO / Intel GPU compute path | **NOT INVESTIGATED** | Iris Xe can run inference via OpenVINO/DirectML, but no such runtime is installed and Phase 1 did not install one. |
| Power plan / thermal state | **NOT RECORDED** | Phase 0 §12 asks for thermal context; a laptop under thermal throttling is not comparable to a rack GPU. |

### Risk R-P1 — Python 3.13 compatibility

Python **3.13.4** is newer than the versions many open-source TTS stacks
currently support. Several widely-used TTS packages pin `<3.12` or rely on
compiled extensions that lag new CPython releases. This is **not yet a
demonstrated failure** — nothing has been attempted — but it is a foreseeable
Phase 2 blocker and is why `reproducibility_audit.md` recommends a pinned,
isolated virtual environment rather than the system interpreter.

## 6. Phase 0 §12 environment record — completeness

Phase 0 requires an `env_record.json` alongside every result. The benchmark
harness `scripts/bench_frontend.py` emits an environment block automatically
(`artifacts/frontend_bench.json`). Fields currently emitted: OS, machine,
processor, logical cores, Python, torch, CUDA availability.

Fields from the Phase 0 §12 schema that are **not yet captured**: GPU model,
VRAM, driver, CUDA/cuDNN versions, container digest, `pip_freeze_hash`, model
precision, batch policy, and the entire **audio contract block** (sample rate,
codec, chunk size, loudness target) — the last because Phase 0 Q-02 is
unanswered and there is no audio pipeline to describe.

## 7. Verdict for Phase 1 purposes

| Question | Answer |
|---|---|
| Can this machine develop and test the normalization frontend? | **YES** — done; 104 tests pass in 0.45 s |
| Can it run CPU inference for a small TTS model? | **UNCERTAIN** — plausible, but untested, and currently constrained by 2.6 GB free RAM and 16.4 GB free on C: |
| Can it run GPU inference? | **NO** — no NVIDIA GPU, CPU-only torch build |
| Can it train or fine-tune? | **NO** — explicitly out of scope, and infeasible |
| Can it validate Phase 0 HC-8 (p99 ≤ 500 ms)? | **NO** — must be deferred to GPU hardware |
| Can it validate Phase 0 HC-9 (15–20 concurrency)? | **NO** — must be deferred to GPU hardware |
