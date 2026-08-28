"""Data-driven normalization tests against the frozen Phase 0 §8 case set.

Every case in data/testsets/normalization_cases.yaml becomes a test. Cases
marked `xfail: true` document known gaps; they are reported as expected
failures rather than being deleted, per Phase 0 §17 ("do not hide failures").
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

from tnorm import Lang, Normalizer

CASES_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "data"
    / "testsets"
    / "normalization_cases.yaml"
)


def load_cases() -> list[dict]:
    with CASES_PATH.open(encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    return doc["cases"]


CASES = load_cases()


def _ids(cases):
    return [c["id"] for c in cases]


@pytest.fixture(scope="module")
def norm() -> Normalizer:
    return Normalizer()


@pytest.mark.parametrize("case", CASES, ids=_ids(CASES))
def test_normalization_case(case: dict, norm: Normalizer) -> None:
    if case.get("xfail"):
        pytest.xfail(case.get("xfail_reason", "known gap"))

    result = norm.normalize(case["input"])

    if "expect_contains" in case:
        assert case["expect_contains"] in result.spoken, (
            f"\n  case      : {case['id']}\n"
            f"  input     : {case['input']!r}\n"
            f"  expected  : {case['expect_contains']!r} in output\n"
            f"  actual    : {result.spoken!r}"
        )

    if "expect_not_contains" in case:
        assert case["expect_not_contains"] not in result.spoken, (
            f"\n  case      : {case['id']}\n"
            f"  input     : {case['input']!r}\n"
            f"  forbidden : {case['expect_not_contains']!r}\n"
            f"  actual    : {result.spoken!r}"
        )

    if "expect_matrix" in case:
        assert result.matrix_lang.value == case["expect_matrix"], (
            f"case {case['id']}: matrix language "
            f"{result.matrix_lang.value} != {case['expect_matrix']}"
        )

    if "expect_code_mixed" in case:
        assert result.is_code_mixed is case["expect_code_mixed"], (
            f"case {case['id']}: code_mixed "
            f"{result.is_code_mixed} != {case['expect_code_mixed']}"
        )

    if "expect_suffix_on" in case:
        stems = [t.text for t in result.tokens if t.suffix]
        assert case["expect_suffix_on"] in stems, (
            f"case {case['id']}: expected a Tamil suffix attached to "
            f"{case['expect_suffix_on']!r}; tokens with suffixes: {stems}"
        )


def test_exact_determinism_cases_all_pass() -> None:
    """Release-blocking gate: every EXACT-determinism case must pass.

    Phase 0 §4.5 makes exact-determinism failures release-blocking. This test
    asserts that gate as a single check so it is visible in CI output.
    """
    n = Normalizer()
    failures: list[str] = []
    for case in CASES:
        if case.get("xfail") or case.get("determinism") != "exact":
            continue
        r = n.normalize(case["input"])
        if "expect_contains" in case and case["expect_contains"] not in r.spoken:
            failures.append(
                f"{case['id']}: {case['input']!r} -> {r.spoken!r} "
                f"(missing {case['expect_contains']!r})"
            )
        if (
            "expect_not_contains" in case
            and case["expect_not_contains"] in r.spoken
        ):
            failures.append(
                f"{case['id']}: {case['input']!r} -> {r.spoken!r} "
                f"(forbidden {case['expect_not_contains']!r})"
            )
    assert not failures, "EXACT-determinism failures:\n" + "\n".join(failures)


def test_ambiguity_pairs_render_differently() -> None:
    """Phase 0 PN-14: paired cases must NOT produce the same rendering."""
    n = Normalizer()
    pairs: dict[str, list[dict]] = {}
    for c in CASES:
        if "pair" in c and not c.get("xfail"):
            pairs.setdefault(c["pair"], []).append(c)

    assert pairs, "no ambiguity pairs found in the frozen case set"

    for pair_id, members in pairs.items():
        assert len(members) == 2, f"pair {pair_id} must have exactly 2 members"
        a, b = (n.normalize(m["input"]).spoken for m in members)
        assert a != b, (
            f"ambiguity pair {pair_id} rendered identically: {a!r}\n"
            f"  A: {members[0]['input']!r}\n"
            f"  B: {members[1]['input']!r}"
        )
