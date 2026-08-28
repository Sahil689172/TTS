"""English number verbalization.

Implemented in-repo rather than via `num2words` so that Phase 1 adds no new
download and the exact spoken forms are frozen under our own tests
(Phase 0 PN-18: every rule traceable to a frozen test case).

Covers Phase 0 §8 categories N1 (numbers), N3 (times), N10 (prices),
N11 (distances) and the digit-by-digit forms required by N4/N5/N6.
"""

from __future__ import annotations

ONES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
]
TENS = [
    "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
    "eighty", "ninety",
]

ORDINAL_SPECIAL = {
    "one": "first", "two": "second", "three": "third", "five": "fifth",
    "eight": "eighth", "nine": "ninth", "twelve": "twelfth",
}

DIGIT_WORDS = ONES[:10]


def digit_by_digit(digits: str, *, zero_as: str = "zero") -> str:
    """Read a digit string one digit at a time.

    This is the EXACT-determinism path required by Phase 0 PN-04 (phone),
    PN-05 (OTP) and PN-06 (booking ID). Leading zeros are preserved by
    construction, which is the N5 `OTP: 0042` trap.
    """
    out = []
    for ch in digits:
        if ch.isdigit():
            out.append(zero_as if ch == "0" else DIGIT_WORDS[int(ch)])
    return " ".join(out)


def _below_thousand(n: int) -> str:
    assert 0 <= n < 1000
    if n < 20:
        return ONES[n]
    if n < 100:
        t, r = divmod(n, 10)
        return TENS[t] + ("-" + ONES[r] if r else "")
    h, r = divmod(n, 100)
    s = ONES[h] + " hundred"
    if r:
        s += " " + _below_thousand(r)
    return s


def cardinal(n: int, *, grouping: str = "indian") -> str:
    """Spell out an integer.

    `grouping` selects the numeric system:
      "indian"  -> ... crore, lakh, thousand   (default; taxi domain is India)
      "western" -> ... billion, million, thousand

    Phase 0 §8 N1 marks Indian-vs-Western grouping as `open` determinism, so
    this is a configurable project decision, not a frozen requirement.
    """
    if n < 0:
        return "minus " + cardinal(-n, grouping=grouping)
    if n < 1000:
        return _below_thousand(n)

    parts: list[str] = []
    if grouping == "indian":
        scales = [(10_000_000, "crore"), (100_000, "lakh"), (1000, "thousand")]
    else:
        scales = [
            (1_000_000_000, "billion"),
            (1_000_000, "million"),
            (1000, "thousand"),
        ]
    rest = n
    for value, name in scales:
        if rest >= value:
            count, rest = divmod(rest, value)
            parts.append(cardinal(count, grouping=grouping) + " " + name)
    if rest:
        parts.append(_below_thousand(rest))
    return " ".join(parts)


def ordinal(n: int, *, grouping: str = "indian") -> str:
    """Spell out an ordinal: 1 -> first, 23 -> twenty-third."""
    words = cardinal(n, grouping=grouping)
    # Only the final word takes the ordinal ending.
    if "-" in words.split()[-1]:
        head, _, tail = words.rpartition("-")
        return head + "-" + _ordinal_word(tail)
    head, _, tail = words.rpartition(" ")
    tail_o = _ordinal_word(tail)
    return (head + " " + tail_o) if head else tail_o


def _ordinal_word(w: str) -> str:
    if w in ORDINAL_SPECIAL:
        return ORDINAL_SPECIAL[w]
    if w.endswith("y"):
        return w[:-1] + "ieth"
    return w + "th"


def decimal(text: str, *, grouping: str = "indian") -> str:
    """Read a decimal number: 2.5 -> 'two point five'.

    The fractional part is read digit-by-digit, which is the standard English
    convention and avoids '2.25' becoming 'two point twenty-five'.
    """
    neg = text.startswith("-")
    text = text.lstrip("+-")
    whole, _, frac = text.partition(".")
    whole = whole.replace(",", "")
    out = cardinal(int(whole or 0), grouping=grouping)
    if frac:
        out += " point " + digit_by_digit(frac)
    return ("minus " + out) if neg else out


def year(n: int) -> str:
    """Read a 4-digit year the way speakers say it: 2026 -> twenty twenty-six.

    Phase 0 §8 N-AMB requires `2026` as a year to differ from `2026` as a
    count, so this is a separate function from `cardinal` by design.
    """
    if not (1000 <= n <= 9999):
        return cardinal(n)
    hi, lo = divmod(n, 100)
    if lo == 0:
        return cardinal(hi) + " hundred"
    if lo < 10:
        # 2005 -> "two thousand five" is the common reading.
        return cardinal(n, grouping="western")
    return cardinal(hi) + " " + _below_thousand(lo)


def clock_time(hour: int, minute: int, meridiem: str | None = None) -> str:
    """Natural English time reading (Phase 0 PN-03 / N3).

    Canonical form chosen for this project (determinism = PREFERRED):
      7:30 PM -> "seven thirty PM"
      7:05    -> "seven oh five"      (the leading-zero trap in N3)
      7:00    -> "seven o'clock"      (bare) / "seven PM" (with meridiem)
      12:00 AM-> "twelve midnight"
      12:00 PM-> "twelve noon"
    """
    h12 = hour
    if meridiem is None and hour > 12:
        h12 = hour - 12
    if h12 == 0:
        h12 = 12

    mer = (meridiem or "").upper().replace(".", "")
    if minute == 0 and mer in ("AM", "PM") and h12 == 12:
        return "twelve midnight" if mer == "AM" else "twelve noon"

    if minute == 0:
        base = ONES[h12] if h12 < 20 else _below_thousand(h12)
        return f"{base} {mer}".strip() if mer else f"{base} o'clock"

    hword = ONES[h12] if h12 < 20 else _below_thousand(h12)
    if minute < 10:
        mword = "oh " + DIGIT_WORDS[minute]
    else:
        mword = _below_thousand(minute)
    return f"{hword} {mword} {mer}".strip()
