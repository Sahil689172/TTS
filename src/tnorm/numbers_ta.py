"""Tamil number verbalization.

STATUS: PRELIMINARY - NOT VALIDATED BY A NATIVE SPEAKER.

This module is written from documented Tamil numeral morphology, but no native
Tamil speaker has reviewed its output as of Phase 1. Per Phase 0 §19 ("do not
fabricate quality"), every form produced here must be treated as a HYPOTHESIS
until validated. `docs/phase1/normalization_audit.md` records this as an open
blocker, and `PHASE 1 ACTIONS FOR USER` requests the validation pass.

Known limitations, all documented rather than hidden:
  L1. Combining (sandhi) forms are implemented for tens and hundreds only.
  L2. Numbers above 9,99,999 use a compositional rule that is plausible but
      unverified.
  L3. Colloquial Chennai speech frequently differs from the literary forms
      below (e.g. time-telling). Phase 0 LR-08/H-09 make this a real quality
      axis, and the choice is deliberately left OPEN.
  L4. Whether Tamil speakers use TAMIL or ENGLISH digit names inside OTPs and
      phone numbers is an open research question flagged in Phase 0 §8 N6.
      Controlled by `digit_language` rather than hard-coded.
"""

from __future__ import annotations

# Digit names, isolated form. Used for digit-by-digit reading.
TA_DIGITS = [
    "பூஜ்யம்",   # 0
    "ஒன்று",     # 1
    "இரண்டு",    # 2
    "மூன்று",    # 3
    "நான்கு",    # 4
    "ஐந்து",     # 5
    "ஆறு",       # 6
    "ஏழு",       # 7
    "எட்டு",     # 8
    "ஒன்பது",    # 9
]

TA_TEENS = {
    10: "பத்து", 11: "பதினொன்று", 12: "பன்னிரண்டு", 13: "பதிமூன்று",
    14: "பதினான்கு", 15: "பதினைந்து", 16: "பதினாறு", 17: "பதினேழு",
    18: "பதினெட்டு", 19: "பத்தொன்பது",
}

# Isolated tens.
TA_TENS = {
    20: "இருபது", 30: "முப்பது", 40: "நாற்பது", 50: "ஐம்பது",
    60: "அறுபது", 70: "எழுபது", 80: "எண்பது", 90: "தொண்ணூறு",
}

# Combining ("sandhi") tens, used when a unit digit follows: 21 -> இருபத்தி ஒன்று
TA_TENS_COMB = {
    20: "இருபத்தி", 30: "முப்பத்தி", 40: "நாற்பத்தி", 50: "ஐம்பத்தி",
    60: "அறுபத்தி", 70: "எழுபத்தி", 80: "எண்பத்தி", 90: "தொண்ணூற்றி",
}

# Isolated hundreds.
TA_HUNDREDS = {
    100: "நூறு", 200: "இருநூறு", 300: "முந்நூறு", 400: "நானூறு",
    500: "ஐந்நூறு", 600: "அறுநூறு", 700: "எழுநூறு", 800: "எண்ணூறு",
    900: "தொள்ளாயிரம்",
}

# Combining hundreds, used when anything follows: 101 -> நூற்றி ஒன்று
TA_HUNDREDS_COMB = {
    100: "நூற்றி", 200: "இருநூற்றி", 300: "முந்நூற்றி", 400: "நானூற்றி",
    500: "ஐந்நூற்றி", 600: "அறுநூற்றி", 700: "எழுநூற்றி", 800: "எண்ணூற்றி",
    900: "தொள்ளாயிரத்தி",
}

TA_THOUSAND = "ஆயிரம்"
TA_THOUSAND_COMB = "ஆயிரத்தி"
TA_LAKH = "லட்சம்"
TA_CRORE = "கோடி"

# Scale words above one lakh are marked uncertain (limitation L2).
UNCERTAIN_ABOVE = 99999


def digit_by_digit(digits: str, *, digit_language: str = "ta") -> str:
    """Read a digit string one digit at a time in Tamil.

    `digit_language`:
      "ta" -> Tamil digit names (பூஜ்யம் ஒன்று ...)
      "en" -> English digit names, which is what many Chennai speakers
              actually use for OTPs and phone numbers.

    Phase 0 §8 N6 flags this choice as OPEN. It is a parameter, not a
    hard-coded assumption, so the Phase 7 A/B study can settle it without a
    code change.
    """
    if digit_language == "en":
        from .numbers_en import digit_by_digit as en_dbd

        return en_dbd(digits)
    return " ".join(TA_DIGITS[int(c)] for c in digits if c.isdigit())


def _below_hundred(n: int) -> str:
    if n < 10:
        return TA_DIGITS[n]
    if n < 20:
        return TA_TEENS[n]
    t, r = divmod(n, 10)
    tens = t * 10
    if r == 0:
        return TA_TENS[tens]
    return TA_TENS_COMB[tens] + " " + TA_DIGITS[r]


def _below_thousand(n: int) -> str:
    if n < 100:
        return _below_hundred(n)
    h, r = divmod(n, 100)
    hundreds = h * 100
    if r == 0:
        return TA_HUNDREDS[hundreds]
    return TA_HUNDREDS_COMB[hundreds] + " " + _below_hundred(r)


def cardinal(n: int) -> str:
    """Spell out a non-negative integer in Tamil.

    Raises no error above the validated range; instead the caller can consult
    `is_uncertain()` to decide whether to emit a pipeline warning.
    """
    if n < 0:
        return "கழித்தல் " + cardinal(-n)
    if n < 1000:
        return _below_thousand(n)

    if n < 100_000:
        th, r = divmod(n, 1000)
        head = _below_thousand(th)
        if r == 0:
            return head + " " + TA_THOUSAND
        return head + " " + TA_THOUSAND_COMB + " " + _below_thousand(r)

    if n < 10_000_000:
        lakh, r = divmod(n, 100_000)
        out = cardinal(lakh) + " " + TA_LAKH
        return out if r == 0 else out + " " + cardinal(r)

    crore, r = divmod(n, 10_000_000)
    out = cardinal(crore) + " " + TA_CRORE
    return out if r == 0 else out + " " + cardinal(r)


def is_uncertain(n: int) -> bool:
    """True when the produced form falls outside the reviewed range (L2)."""
    return abs(n) > UNCERTAIN_ABOVE


def ordinal(n: int) -> str:
    """Tamil ordinal: 1 -> முதலாவது, 3 -> மூன்றாவது.

    PRELIMINARY. The -ஆவது / -ஆம் distinction is context-sensitive
    (attributive vs predicative) and is NOT modelled here. Recorded as an
    open normalization gap.
    """
    if n == 1:
        return "முதலாவது"
    return cardinal(n) + "ஆவது"


def clock_time(hour: int, minute: int, meridiem: str | None = None) -> str:
    """Tamil time reading. PRELIMINARY (limitation L3).

    Canonical literary form is used: 7:30 -> "ஏழு முப்பது".
    The colloquial "ஏழரை" (half past seven) is NOT produced, because choosing
    between registers is exactly the regional-naturalness question Phase 0
    LR-08 / H-09 defers. Recorded as OPEN determinism.
    """
    h12 = hour
    if meridiem is None and hour > 12:
        h12 = hour - 12
    if h12 == 0:
        h12 = 12

    mer_map = {"AM": "காலை", "PM": "மாலை"}
    mer = mer_map.get((meridiem or "").upper().replace(".", ""), "")

    if minute == 0:
        base = f"{_below_hundred(h12)} மணி"
    else:
        base = f"{_below_hundred(h12)} {_below_hundred(minute)}"
    return f"{mer} {base}".strip()
