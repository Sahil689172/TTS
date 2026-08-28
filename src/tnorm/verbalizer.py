"""Entity verbalization: turn detected entities into spoken word sequences.

Fifth stage of the Phase 0 §16 pipeline.

Language routing rule (Phase 0 §8 N14): the reading language follows the
MATRIX language of the utterance, not the script of the digits. "Driver 5
minutes-ல வருவார்" is a Tamil sentence, so 5 is read in Tamil even though the
digit glyph is ASCII.
"""

from __future__ import annotations

import re

from . import numbers_en as en
from . import numbers_ta as ta
from .lexicons import (
    ABBREVIATIONS,
    AMBIGUOUS_ABBREVIATIONS,
    LETTERS,
    LOCATIONS,
    ROAD_CONTEXT,
    VEHICLES,
)
from .types import Entity, EntityType, Lang

# Letter names used when spelling out an acronym or booking ID.
EN_LETTER_NAMES = {c: c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}


def spell_letters(s: str) -> str:
    """Spell a letter run: 'TN' -> 'T N'."""
    return " ".join(c.upper() for c in s if c.isalpha())


def _int_of(s: str) -> int:
    return int(re.sub(r"[^\d-]", "", s) or 0)


def verbalize_entity(e: Entity, matrix: Lang, cfg: "NormConfig") -> str:
    """Render one entity as its spoken form."""
    t = e.type
    txt = e.text
    tamil = matrix in (Lang.TA, Lang.TA_LATIN)

    # ---- EXACT determinism paths (Phase 0 PN-04/05/06) -------------------
    if t == EntityType.OTP:
        digits = re.sub(r"\D", "", txt)
        if tamil:
            return ta.digit_by_digit(digits, digit_language=cfg.ta_digit_language)
        return en.digit_by_digit(digits)

    if t == EntityType.PHONE:
        digits = re.sub(r"\D", "", txt)
        # Keep a country code readable as a unit rather than as ten digits.
        if digits.startswith("91") and len(digits) == 12:
            cc, rest = digits[:2], digits[2:]
            head = (
                ta.digit_by_digit(cc, digit_language=cfg.ta_digit_language)
                if tamil
                else en.digit_by_digit(cc)
            )
            body = (
                ta.digit_by_digit(rest, digit_language=cfg.ta_digit_language)
                if tamil
                else en.digit_by_digit(rest)
            )
            return f"plus {head} {body}" if not tamil else f"பிளஸ் {head} {body}"
        if tamil:
            return ta.digit_by_digit(digits, digit_language=cfg.ta_digit_language)
        return en.digit_by_digit(digits)

    if t == EntityType.BOOKING_ID:
        # Character-by-character: letters spelled, digits read individually.
        out: list[str] = []
        for ch in txt:
            if ch.isalpha():
                out.append(ch.upper())
            elif ch.isdigit():
                out.append(
                    ta.digit_by_digit(ch, digit_language=cfg.ta_digit_language)
                    if tamil
                    else en.digit_by_digit(ch)
                )
            # separators are dropped
        return " ".join(out)

    if t == EntityType.PIN_CODE:
        digits = re.sub(r"\D", "", txt)
        return (
            ta.digit_by_digit(digits, digit_language=cfg.ta_digit_language)
            if tamil
            else en.digit_by_digit(digits)
        )

    # ---- PREFERRED determinism paths -------------------------------------
    if t == EntityType.TIME:
        h = e.meta.get("hour", 0)
        mi = e.meta.get("minute", 0)
        mer = e.meta.get("meridiem")
        return ta.clock_time(h, mi, mer) if tamil else en.clock_time(h, mi, mer)

    if t == EntityType.DATE:
        a, b, y = e.meta.get("a"), e.meta.get("b"), e.meta.get("y")
        # OPEN determinism: day-first assumed (Indian convention).
        day, month = (a, b) if cfg.date_order == "dmy" else (b, a)
        if y is not None and y < 100:
            y += 2000
        months_en = [
            "", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]
        if tamil:
            mname = months_en[month] if 1 <= month <= 12 else str(month)
            return f"{ta.ordinal(day)} {mname} {ta.cardinal(y)}"
        mname = months_en[month] if 1 <= month <= 12 else str(month)
        return f"{en.ordinal(day)} {mname} {en.year(y)}"

    if t == EntityType.PRICE:
        val = e.meta.get("value", "0")
        num = _verbalize_number_str(val, tamil, cfg)
        return f"{num} ரூபாய்" if tamil else f"{num} rupees"

    if t == EntityType.DISTANCE:
        val = e.meta.get("value", "0")
        unit = e.meta.get("unit", "km")
        num = _verbalize_number_str(val, tamil, cfg)
        if unit.startswith("k"):
            uname = "கிலோமீட்டர்" if tamil else "kilometres"
        else:
            uname = "மீட்டர்" if tamil else "metres"
        return f"{num} {uname}"

    if t == EntityType.DURATION:
        val = e.meta.get("value", "0")
        unit = e.meta.get("unit", "min")
        num = _verbalize_number_str(val, tamil, cfg)
        if unit.startswith("h"):
            uname = "மணி நேரம்" if tamil else "hours"
        elif unit.startswith("s"):
            uname = "வினாடி" if tamil else "seconds"
        else:
            uname = "நிமிடம்" if tamil else "minutes"
        return f"{num} {uname}"

    if t == EntityType.ORDINAL:
        v = e.meta.get("value", 0)
        return ta.ordinal(v) if tamil else en.ordinal(v)

    if t == EntityType.DECIMAL:
        return _verbalize_number_str(txt, tamil, cfg)

    if t == EntityType.CARDINAL:
        return _verbalize_number_str(txt, tamil, cfg)

    return txt


def _verbalize_number_str(s: str, tamil: bool, cfg: "NormConfig") -> str:
    s = s.replace(",", "").strip()
    if "." in s:
        if tamil:
            whole, _, frac = s.partition(".")
            return (
                ta.cardinal(int(whole or 0))
                + " புள்ளி "
                + ta.digit_by_digit(frac, digit_language=cfg.ta_digit_language)
            )
        return en.decimal(s, grouping=cfg.grouping)
    try:
        n = int(s)
    except ValueError:
        return s
    return ta.cardinal(n) if tamil else en.cardinal(n, grouping=cfg.grouping)


def verbalize_abbreviation(
    tok: str, prev: str | None, nxt: str | None
) -> str | None:
    """Expand an abbreviation, resolving the ST/DR ambiguity from context.

    Returns None when the token is not a known abbreviation.
    """
    key = tok.upper()

    # "No." is 'number' only when a number actually follows; otherwise it is
    # the ordinary English word "no" and must be left alone.
    if key == "NO":
        if nxt and (nxt[:1].isdigit()):
            return "number"
        return None

    if key in AMBIGUOUS_ABBREVIATIONS:
        table = AMBIGUOUS_ABBREVIATIONS[key]
        prev_l = (prev or "").lower().strip(".,")
        # A road-context word BEFORE the abbreviation makes it trailing:
        # "3rd Cross St." -> street ; "Palm Grove Dr." -> drive
        if prev_l in ROAD_CONTEXT:
            return table["_trailing"]
        # A capitalized proper noun AFTER it makes it leading:
        # "St. Thomas Mount" -> saint ; "Dr. Kumar" -> doctor
        if nxt and nxt[:1].isupper():
            return table["_leading"]
        return table["_default"]

    if key in ABBREVIATIONS:
        v = ABBREVIATIONS[key]
        return spell_letters(tok) if v is LETTERS else v

    if key in VEHICLES:
        v = VEHICLES[key]
        return spell_letters(tok) if v is LETTERS else v

    if key in LOCATIONS:
        v = LOCATIONS[key]
        return spell_letters(tok) if v is LETTERS else v

    return None


class NormConfig:
    """Configuration for open-determinism choices (Phase 0 §8).

    Every field here corresponds to a decision Phase 0 explicitly left OPEN.
    Making them configuration rather than hard-coded behaviour is what allows
    Phase 1 to ship without pre-empting a Phase 2/7 research decision.
    """

    def __init__(
        self,
        *,
        grouping: str = "indian",       # N1: lakh/crore vs million/billion
        date_order: str = "dmy",        # N2: DD/MM vs MM/DD
        ta_digit_language: str = "ta",  # N6: Tamil vs English digit names
        booking_id_grouping: str = "char",  # N6: per-character vs grouped
    ) -> None:
        self.grouping = grouping
        self.date_order = date_order
        self.ta_digit_language = ta_digit_language
        self.booking_id_grouping = booking_id_grouping

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"NormConfig(grouping={self.grouping!r}, "
            f"date_order={self.date_order!r}, "
            f"ta_digit_language={self.ta_digit_language!r})"
        )


DEFAULT_CONFIG = NormConfig()
