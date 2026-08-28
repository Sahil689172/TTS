# Local model store

Model **weights are never committed to Git** (Phase 0 §23, `.gitignore`).
Only `manifest.yaml`, `README.md` and small JSON/YAML config files are tracked.

## Status as of Phase 1

**No models are present.** This directory is empty by design. Phase 1 is an
audit phase and performed no large downloads (Phase 0 Step 5/6: audit before
download, stop for approval).

See `docs/phase1/download_manifest.md` for what would be downloaded, why, and
which items require explicit user approval.

## CRITICAL: where weights must be stored on this machine

The project checkout lives on **C:**, which has only ~16 GB free and is inside
a **OneDrive-synced** folder. Storing multi-GB model weights here would (a)
risk filling the system drive and (b) push weights into OneDrive sync.

Weights must therefore be stored on **D:** (~475 GB free, not OneDrive-synced):

```
D:\tts-models\
├── english\
├── tamil\
└── candidates\
```

Point tooling at that location with an environment variable:

```
setx TTS_MODEL_ROOT "D:\tts-models"
```

`manifest.yaml` records logical model entries; `local_path` entries reference
`$TTS_MODEL_ROOT`, never an absolute path inside the repository.
