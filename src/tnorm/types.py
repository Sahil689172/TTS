"""Core data types for the tnorm normalization pipeline.

Phase 1 foundation. Traces to Phase 0 requirements PN-01..PN-18.

Design note (Phase 0 Q-12): the pipeline accepts OPTIONAL upstream entity tags.
When the dialog system can label its own entities we use those labels; when it
cannot we fall back to inference from raw text. Both paths are supported so the
Phase 2 decision on Q-12 does not require re-architecting the frontend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Script(str, Enum):
    """Unicode script of a text span."""

    TAMIL = "tamil"
    LATIN = "latin"
    DIGIT = "digit"
    PUNCT = "punct"
    SPACE = "space"
    OTHER = "other"
    MIXED = "mixed"


class Lang(str, Enum):
    """Language identity of a text span.

    TA_LATIN is Tamil written in Latin characters (Phase 0 LR-05, PN-16).
    It is deliberately distinct from EN: the characters are Latin but the
    language is Tamil, and conflating the two is the single most common
    Tanglish frontend bug.
    """

    EN = "en"
    TA = "ta"
    TA_LATIN = "ta-latn"
    UNKNOWN = "unknown"


class EntityType(str, Enum):
    """Normalizable entity categories.

    These map 1:1 onto the Phase 0 §8 normalization test categories.
    """

    OTP = "otp"                  # PN-05, N5  - exact determinism
    PHONE = "phone"              # PN-04, N4  - exact determinism
    BOOKING_ID = "booking_id"    # PN-06, N6  - exact determinism
    PIN_CODE = "pin_code"        # N7
    TIME = "time"                # PN-03, N3
    DATE = "date"                # PN-02, N2
    PRICE = "price"              # PN-10, N10
    DISTANCE = "distance"        # PN-11, N11
    DURATION = "duration"        # N3
    ORDINAL = "ordinal"          # N1
    DECIMAL = "decimal"          # N1
    CARDINAL = "cardinal"        # PN-01, N1
    ABBREVIATION = "abbreviation"  # PN-08, N8
    VEHICLE = "vehicle"          # PN-09, N9
    LOCATION = "location"        # PN-13, N13
    ADDRESS_NUM = "address_num"  # PN-07, N7
    PLAIN = "plain"              # no normalization needed


class Determinism(str, Enum):
    """How firmly the spoken form is fixed.

    EXACT    - Phase 0 specifies the output verbatim; any deviation is a
               release-blocking failure (PN-04, PN-05, PN-06, PN-14).
    PREFERRED- we chose a canonical form; alternatives are acceptable.
    OPEN     - Phase 0 explicitly defers the decision to Phase 1/2 with a
               recorded rationale. Rendering may change without being a
               regression.
    """

    EXACT = "exact"
    PREFERRED = "preferred"
    OPEN = "open"


@dataclass
class Span:
    """A character range over the original input string."""

    start: int
    end: int

    def slice(self, text: str) -> str:
        return text[self.start : self.end]


@dataclass
class Token:
    """A single token with script and language identity attached.

    `lang` is carried per-token so that downstream stages (and, later, the
    acoustic model) can condition on language at token granularity. Phase 0
    §19.6 flags dropping this as the decision most likely to make Tanglish
    impossible later, so it is preserved from the very first stage.
    """

    text: str
    span: Span
    script: Script
    lang: Lang = Lang.UNKNOWN
    # Tamil grammatical suffix attached to an English token, e.g. the
    # "-ல" in "Chennai Central-ல" (Phase 0 LR-06, N15).
    suffix: Optional[str] = None
    suffix_script: Optional[Script] = None

    @property
    def has_tamil_suffix(self) -> bool:
        return self.suffix is not None


@dataclass
class Entity:
    """A detected entity spanning one or more tokens."""

    type: EntityType
    text: str
    span: Span
    lang: Lang
    determinism: Determinism = Determinism.PREFERRED
    # Where the type came from: "upstream" (Q-12 tagged) or "inferred".
    provenance: str = "inferred"
    # Free-form detector metadata (digit count, matched trigger word, ...).
    meta: dict = field(default_factory=dict)


@dataclass
class NormalizationResult:
    """Full pipeline output.

    `spoken` is the TTS-ready string. Everything else exists so failures are
    diagnosable and so §17 tests can assert on intermediate stages rather than
    only the final string.
    """

    raw: str
    spoken: str
    tokens: list[Token] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    matrix_lang: Lang = Lang.UNKNOWN
    is_code_mixed: bool = False
    # Per-segment (text, lang) pairs for downstream language conditioning.
    lang_segments: list[tuple[str, Lang]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def entity_types(self) -> list[EntityType]:
        return [e.type for e in self.entities]
