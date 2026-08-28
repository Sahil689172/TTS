"""Unicode script detection.

Phase 1 foundation, first stage of the Phase 0 §16 pipeline:
    raw text -> SCRIPT DETECTION -> language detection -> ...

Deliberately rule-based and dependency-free: script identity is a decidable
property of Unicode code points, not something that needs a model.
"""

from __future__ import annotations

import unicodedata

from .types import Script

# Tamil block: U+0B80..U+0BFF (includes Tamil digits U+0BE6..U+0BEF and
# Tamil numerals/symbols U+0BF0..U+0BFA).
TAMIL_RANGE = (0x0B80, 0x0BFF)
TAMIL_DIGIT_RANGE = (0x0BE6, 0x0BEF)

# Tamil numeral signs for ten/hundred/thousand.
TAMIL_NUM_SIGNS = {0x0BF0: 10, 0x0BF1: 100, 0x0BF2: 1000}


def char_script(ch: str) -> Script:
    """Classify a single character."""
    if ch.isspace():
        return Script.SPACE
    cp = ord(ch)
    if TAMIL_RANGE[0] <= cp <= TAMIL_RANGE[1]:
        return Script.TAMIL
    if ch.isdigit() and cp < 0x0080:
        return Script.DIGIT
    if TAMIL_DIGIT_RANGE[0] <= cp <= TAMIL_DIGIT_RANGE[1]:
        return Script.TAMIL
    if ("a" <= ch <= "z") or ("A" <= ch <= "Z"):
        return Script.LATIN
    cat = unicodedata.category(ch)
    if cat.startswith("P") or cat.startswith("S"):
        return Script.PUNCT
    if cat.startswith("N"):
        return Script.DIGIT
    if cat.startswith("L"):
        # Some other letter script (Devanagari, Arabic, CJK, ...).
        return Script.OTHER
    return Script.OTHER


def detect_script(text: str) -> Script:
    """Classify a whole string.

    Returns MIXED when the string contains more than one *letter* script.
    Digits and punctuation never make a string MIXED on their own, because
    "Chennai 600040" is Latin text with digits, not a mixed-script string.
    """
    letter_scripts = set()
    for ch in text:
        s = char_script(ch)
        if s in (Script.TAMIL, Script.LATIN, Script.OTHER):
            letter_scripts.add(s)
    if len(letter_scripts) > 1:
        return Script.MIXED
    if len(letter_scripts) == 1:
        return next(iter(letter_scripts))
    # No letters at all.
    if any(char_script(c) == Script.DIGIT for c in text):
        return Script.DIGIT
    if text.strip() == "":
        return Script.SPACE
    return Script.PUNCT


def has_tamil(text: str) -> bool:
    return any(char_script(c) == Script.TAMIL for c in text)


def has_latin(text: str) -> bool:
    return any(char_script(c) == Script.LATIN for c in text)


def is_mixed_script(text: str) -> bool:
    """True when the string mixes Tamil and Latin letters.

    This is the structural signal for Phase 0 LR-04 / LR-06 (Tamil-script
    matrix with Latin English inserts, and Tamil suffixes on English tokens).
    """
    return has_tamil(text) and has_latin(text)


def tamil_digit_value(ch: str) -> int | None:
    """Value of a Tamil digit character U+0BE6..U+0BEF, else None."""
    cp = ord(ch)
    if TAMIL_DIGIT_RANGE[0] <= cp <= TAMIL_DIGIT_RANGE[1]:
        return cp - TAMIL_DIGIT_RANGE[0]
    return None


def tamil_digits_to_ascii(text: str) -> str:
    """Map Tamil digits to ASCII digits, leaving everything else untouched.

    Phase 0 §8 N1 requires that Tamil-digit input reads identically to the
    ASCII form. Normalizing early keeps every downstream detector simple.
    """
    out = []
    for ch in text:
        v = tamil_digit_value(ch)
        out.append(str(v) if v is not None else ch)
    return "".join(out)
