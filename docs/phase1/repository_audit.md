# Phase 1 — Repository Audit

**Date:** 2026-08-29
**Method:** `git status`, `git ls-files`, `git log`, full filesystem walk of the
working tree excluding `.git`. No files were modified during the audit.

---

## 1. Headline finding

> **The repository contained no TTS implementation of any kind before Phase 1.**
> It contained exactly **one tracked file**: the Phase 0 contract document.

This directly contradicts the Phase 1 task premise, which assumes "existing
English/Tamil systems" to audit, reproduce, benchmark and reverse-engineer.
Recorded formally in §5 below and in `phase1_exit_report.md` as **finding
F-01**.

## 2. Git state at the start of Phase 1

```
branch          : main
upstream        : origin/main (up to date)
working tree    : clean
remote          : https://github.com/Sahil689172/TTS.git
commits         : 1
  f2ae0b8  docs added for project
tracked files   : 1
```

Complete tracked-file listing (verbatim, not a sample):

```
docs/PHASE_0_REQUIREMENTS_FREEZE.md
```

Complete working-tree listing (excluding `.git`):

```
.
./docs
./docs/PHASE_0_REQUIREMENTS_FREEZE.md
```

Repository size on disk: **223 KB** (the Phase 0 document plus git metadata).

## 3. Search results for expected Phase 1 artifacts

Every item below was searched for by content and by path pattern. "Absent"
means **zero** matches in the working tree, not "few".

| Expected artifact (Phase 1 Step 1) | Present? | Evidence |
|---|---|---|
| Phase 0 documents | **YES** (1 file) | `docs/PHASE_0_REQUIREMENTS_FREEZE.md`, 1,377 lines |
| English TTS code | **ABSENT** | no `.py` files existed in the tree |
| Tamil TTS code | **ABSENT** | as above |
| Model configuration | **ABSENT** | no `config.json`, no model YAML |
| Checkpoints / weights | **ABSENT** | no `.pt/.pth/.ckpt/.safetensors/.bin` |
| Tokenizers | **ABSENT** | no `tokenizer.json`, `vocab.*`, `*.model` |
| G2P / phoneme systems | **ABSENT** | no lexicon or G2P module |
| Vocoders | **ABSENT** | no vocoder code or weights |
| Preprocessing code | **ABSENT** | none |
| Datasets | **ABSENT** | no `data/`, no manifests, no audio |
| Inference scripts | **ABSENT** | none |
| Benchmark scripts | **ABSENT** | none |
| Test suites | **ABSENT** | no `tests/`, no `pytest.ini`/`tox.ini` |
| Environment files | **ABSENT** | no `environment.yml`, `.env`, Dockerfile |
| `requirements.txt` | **ABSENT** | — |
| `pyproject.toml` / `setup.py` | **ABSENT** | — |
| `README.md` (root) | **ABSENT** | repo had no root README |
| Architecture documentation | **ABSENT** | none beyond Phase 0 |
| CI configuration | **ABSENT** | no `.github/`, no workflow files |
| `.gitignore` | **ABSENT** | none existed before Phase 1 |

## 4. Phase 0 documentation structure — actual vs proposed

Phase 0 §17 proposed a `docs/00_source … 07_process` tree with machine-readable
`data/*.yaml` sources and CI validation scripts.

**What actually exists** is a single consolidated document,
`docs/PHASE_0_REQUIREMENTS_FREEZE.md`, containing all 20 Phase 0 sections.

This is **not a defect**. The single document carries the full contract: 84
requirements, 12 hard constraints, 21 TBE items, the evaluation and benchmark
protocols, the §8 normalization taxonomy, the §14 traceability matrix, the §16
risk register and the PHASE 0 FREEZE block. Phase 1 consumes it as the source
of truth exactly as written.

The consequence to note is that the machine-readable artifacts Phase 0 §17
called for (`requirements.yaml`, `tbe_register.yaml`, `risk_register.yaml`) and
the CI validators (`validate_traceability.py`, `check_no_thirdparty_tts.py`) **do
not exist**. They are not Phase 1 deliverables, so Phase 1 does not create them,
but their absence means the "CI fails on an unassigned requirement" guarantee in
the PHASE 0 FREEZE is currently **unenforced**. Logged as issue **I-02** below.

## 5. Contradictions and issues found

Per the Phase 1 instruction, these are documented and **not silently changed**.

### F-01 / I-01 — Phase 1 premise assumes systems that do not exist

- **Affected document:** the Phase 1 task specification (not a Phase 0 doc).
- **Issue:** Phase 1 Steps 3, 4, 7, 9, 10, 11, 12, 13, 14, 15 and 18 all
  presuppose "the existing English/Tamil TTS system(s)". No such system exists
  in this repository, and no model weights are present anywhere on the machine
  under project control.
- **Effect:** those steps cannot produce evidence. They are reported as
  **BLOCKED — nothing to audit**, not as passed and not as failed.
- **Proposed correction (NOT applied):** either (a) the user supplies the
  repository/branch that actually contains the English/Tamil implementation, or
  (b) Phase 1's scope is formally amended to "greenfield foundation" —
  environment, normalization frontend, frozen test sets and Phase 2 evidence —
  which is what this Phase 1 actually delivered.
- **Decision required from user.** See `PHASE 1 ACTIONS FOR USER`, action A-01.

### I-02 — Phase 0 §17 deliverable tree not realised

- **Affected document:** `docs/PHASE_0_REQUIREMENTS_FREEZE.md` §17, and the
  PHASE 0 FREEZE item 16 ("CI fails on an unassigned requirement").
- **Issue:** the proposed `docs/` sub-tree, the machine-readable registers and
  the three CI validator scripts were never created. Phase 0's own exit gate
  G-16 is satisfied by the prose matrix, but the automated enforcement is not.
- **Proposed correction (NOT applied):** create `data/requirements.yaml`,
  `data/tbe_register.yaml`, `data/risk_register.yaml` and the validators as a
  Phase 1.5 / Phase 2 chore. Not done here because it is outside the Phase 1
  objective and would amount to redoing Phase 0.

### I-03 — Phase 0 blocking exit gates are still open

- **Affected document:** `PHASE_0_REQUIREMENTS_FREEZE.md` §18.
- **Issue:** Phase 0 declared five items blocking to enter Phase 1:
  **G-00** (source-document reconciliation), **G-03** (every requirement has a
  named owner), **G-18** (Q-01 latency metric answered), **G-19** (Q-02 audio /
  telephony contract answered), **G-20** (acceptance criteria tagged
  `phase0@v1`). None of the five is satisfied. `git tag` shows no tags.
- **Effect:** Phase 1 has proceeded with Phase 0's blocking gates open. This is
  a **process deviation**, recorded rather than hidden.
- **Proposed correction (NOT applied):** answer Q-01 and Q-02 and assign
  requirement owners before Phase 2 model selection, because both directly
  constrain Phase 2 (Q-01 sets the latency target being selected against; Q-02
  determines whether candidates are evaluated at 8 kHz or wideband).
- See `PHASE 1 ACTIONS FOR USER`, actions A-02 and A-03.

### I-04 — repository is inside a OneDrive-synced folder

- **Affected document:** none (new finding).
- **Issue:** the checkout is at `C:\Users\hp\OneDrive\Desktop\TTS`. Any model
  weights, datasets or generated audio written inside the repository would be
  uploaded to OneDrive, and the project drive has only **16.4 GB free**.
- **Proposed correction (APPLIED, non-destructive):** `.gitignore` excludes
  weights/audio, and `models/README.md` directs all weight storage to
  `D:\tts-models` (~475 GB free, outside OneDrive). No files were moved.

## 6. What Phase 1 created

All paths below are new. Nothing pre-existing was modified or deleted; the only
pre-existing file, `docs/PHASE_0_REQUIREMENTS_FREEZE.md`, is **untouched**.

```
.gitignore                                   new
pytest.ini                                   new
src/tnorm/                                   new  (normalization frontend)
  __init__.py  types.py  scripts.py  langid.py  tokenizer.py
  entities.py  numbers_en.py  numbers_ta.py  verbalizer.py  pipeline.py
  lexicons/__init__.py
tests/                                       new
  test_units.py  test_normalization_cases.py
data/testsets/                               new
  normalization_cases.yaml  golden_seed.yaml
scripts/bench_frontend.py                    new
models/README.md  models/manifest.yaml       new
docs/phase1/*.md                             new
artifacts/frontend_bench.json                new (gitignored)
```

## 7. Audit conclusion

The repository is **greenfield apart from the Phase 0 contract**. There is no
prior TTS implementation to audit, reproduce, benchmark or reverse-engineer.
Phase 1 therefore delivered the work that *was* possible without inventing
evidence: environment characterisation, the normalization foundation with
tests, frozen test-set structure, a download manifest gated on user approval,
and evidence-based Phase 2 requirements.
