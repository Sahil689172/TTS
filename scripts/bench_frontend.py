"""Normalization-frontend latency benchmark.

SCOPE: this benchmarks the TEXT NORMALIZATION FRONTEND ONLY. No TTS model
exists in this repository (see docs/phase1/model_inventory.md), so no acoustic
or end-to-end latency can be measured in Phase 1.

WHY THIS MATTERS ANYWAY: Phase 0 §6.6 states that frontend processing is
INSIDE the user-perceived latency budget and must never be excluded from
measurement, and Phase 0 conflict C-11 flags the frontend as a real consumer
of the ~500 ms p99 budget. Establishing the frontend's cost now sets the
sub-budget that Phase 2 model selection must plan around.

All results are labelled DEVELOPMENT MACHINE BASELINE. The machine has no
dedicated NVIDIA GPU and cannot represent production performance
(Phase 0 §12 environment record required alongside any number).

Usage:
    python scripts/bench_frontend.py --out artifacts/frontend_bench.json
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import platform
import statistics
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from tnorm import Normalizer  # noqa: E402

# Workload mirrors the Phase 0 §6.2 benchmark corpus composition:
#   language  EN 35% / TA 35% / TG 30%
#   entity-heavy 30%
CORPUS: list[tuple[str, str, bool]] = [
    # (text, language_label, entity_heavy)
    ("Your cab will arrive in 10 minutes.", "en", False),
    ("Your driver is on the way.", "en", False),
    ("Your booking is confirmed.", "en", False),
    ("Your OTP is 4821 and your booking ID is TN45AB1234.", "en", True),
    ("Your phone number is 9876543210 and the fare is Rs. 250.", "en", True),
    ("Your cab will arrive at 7:30 PM at No. 12, 3rd Cross St.", "en", True),
    ("The driver will reach the pickup point shortly, please wait near the "
     "main gate and keep your phone reachable.", "en", False),
    ("உங்கள் வண்டி வந்துவிட்டது.", "ta", False),
    ("உங்கள் பயணம் உறுதி செய்யப்பட்டது.", "ta", False),
    ("ஓட்டுநர் வழியில் இருக்கிறார்.", "ta", False),
    ("உங்கள் OTP 4821, கட்டணம் 250 ரூபாய்.", "ta", True),
    ("உங்கள் வண்டி 7:30 மணிக்கு வரும்.", "ta", True),
    ("உங்கள் pickup location எங்கே?", "tg", False),
    ("unga pickup location enga?", "tg", False),
    ("Chennai Central-ல இருக்கா?", "tg", False),
    ("Driver இன்னும் 5 minutes-ல வருவார்.", "tg", True),
    ("Booking-ah cancel pannunga, OTP 4821 venum.", "tg", True),
    ("உங்கள் ride 2.5 km தூரத்தில் இருக்கு.", "tg", True),
]


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile on the raw sample (Phase 0 F-6)."""
    if not values:
        return float("nan")
    s = sorted(values)
    k = max(1, int(round(p / 100.0 * len(s))))
    return s[min(k, len(s)) - 1]


def env_record() -> dict:
    """Phase 0 §12 environment record (subset measurable here)."""
    rec = {
        "os": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_logical_cores": os.cpu_count(),
        "python": platform.python_version(),
        "gpu_cuda_available": False,
        "note": "DEVELOPMENT MACHINE BASELINE - no dedicated NVIDIA GPU",
    }
    try:
        import torch

        rec["torch"] = torch.__version__
        rec["gpu_cuda_available"] = bool(torch.cuda.is_available())
    except Exception:
        rec["torch"] = "not installed"
    return rec


def run(warmup: int, iterations: int) -> dict:
    norm = Normalizer()

    # Warm-up, discarded (Phase 0 §6.2 / PERF-14).
    for _ in range(warmup):
        for text, _, _ in CORPUS:
            norm.normalize(text)

    per_case: dict[str, list[float]] = {}
    all_lat: list[float] = []
    errors = 0

    t_start = time.perf_counter()
    for _ in range(iterations):
        for text, lang, heavy in CORPUS:
            key = f"{lang}|{'heavy' if heavy else 'plain'}"
            t0 = time.perf_counter()
            try:
                norm.normalize(text)
            except Exception:
                errors += 1
                continue
            dt = (time.perf_counter() - t0) * 1000.0
            per_case.setdefault(key, []).append(dt)
            all_lat.append(dt)
    wall = time.perf_counter() - t_start

    n = len(all_lat)
    result = {
        "label": "DEVELOPMENT MACHINE BASELINE",
        "scope": "TEXT NORMALIZATION FRONTEND ONLY - no TTS model involved",
        "environment": env_record(),
        "workload": {
            "corpus_size": len(CORPUS),
            "iterations": iterations,
            "warmup_iterations": warmup,
            "total_requests": n,
        },
        "latency_ms": {
            "n": n,
            "mean": round(statistics.fmean(all_lat), 4) if n else None,
            "p50": round(percentile(all_lat, 50), 4),
            "p95": round(percentile(all_lat, 95), 4),
            "p99": round(percentile(all_lat, 99), 4),
            "max": round(max(all_lat), 4) if n else None,
        },
        "throughput_rps": round(n / wall, 1) if wall else None,
        "error_rate": round(errors / max(1, n + errors), 6),
        "by_stratum_ms": {
            k: {
                "n": len(v),
                "p50": round(percentile(v, 50), 4),
                "p95": round(percentile(v, 95), 4),
                "p99": round(percentile(v, 99), 4),
            }
            for k, v in sorted(per_case.items())
        },
        "caveats": [
            "Single-process, single-thread. No concurrency sweep is reported "
            "because Phase 0 concurrency is defined over a TTS SERVICE, which "
            "does not exist yet.",
            "These numbers are NOT a Phase 0 §6 benchmark result. They are a "
            "frontend sub-budget measurement only.",
            "p99 from this sample size is indicative, not a Phase 0-grade p99 "
            "(Phase 0 §6.2 requires n>=1000 per level and 3 repetitions).",
        ],
    }
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--iterations", type=int, default=200)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    res = run(args.warmup, args.iterations)
    print(json.dumps(res, indent=2, ensure_ascii=False))

    if args.out:
        p = pathlib.Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(res, indent=2, ensure_ascii=False), "utf-8")
        print(f"\nwritten: {p}", file=sys.stderr)


if __name__ == "__main__":
    main()
