"""Context-sensitive entity detection.

Fourth stage of the Phase 0 §16 pipeline, and the stage that carries the
release-blocking requirement PN-14: *the same digit string must be rendered
differently depending on context*.

    "Your OTP is 4821"        -> four eight two one
    "The fare is 4821 rupees" -> four thousand eight hundred twenty-one

Detection is therefore driven by CONTEXT TRIGGERS (nearby keywords, in English
or Tamil) combined with STRUCTURAL cues (digit count, character pattern), never
by the digit string alone.

Phase 0 Q-12: an upstream dialog system may already know that a value is an
OTP. `detect_entities(..., upstream=...)` accepts those labels and marks them
`provenance="upstream"`, bypassing inference. Inference is the fallback, not
the only path.
"""

from __future__ import annotations

import re

from .types import Determinism, Entity, EntityType, Lang, Span

# --------------------------------------------------------------------------
# Context trigger vocabularies. English + Tamil + romanized Tamil, because a
# trigger may appear in any of the three (Phase 0 LR-04/LR-05).
# --------------------------------------------------------------------------

TRIGGERS: dict[EntityType, set[str]] = {
    EntityType.OTP: {
        "otp", "o.t.p", "code", "verification", "pin",
        "ஓடிபி", "கடவுச்சொல்", "குறியீடு",
    },
    EntityType.PHONE: {
        "phone", "mobile", "number", "contact", "call", "whatsapp",
        "தொலைபேசி", "மொபைல்", "நம்பர்", "எண்",
    },
    EntityType.BOOKING_ID: {
        "booking", "id", "reference", "ref", "trip", "ticket", "pnr",
        "புக்கிங்", "ஐடி", "குறிப்பு",
    },
    EntityType.PRICE: {
        "fare", "price", "cost", "amount", "charge", "pay", "rupees", "rs",
        "கட்டணம்", "விலை", "ரூபாய்", "பணம்",
    },
    EntityType.PIN_CODE: {"pincode", "pin code", "postal", "zip"},
}

# How far (in tokens) a trigger may sit from the value it labels.
TRIGGER_WINDOW = 4

# --------------------------------------------------------------------------
# Structural patterns
# --------------------------------------------------------------------------

# Booking ID: mixed letters+digits, e.g. TN45AB1234, BK-2026-0093.
RE_BOOKING_ID = re.compile(
    r"\b(?=[A-Z0-9-]{5,})(?=.*[A-Z])(?=.*\d)[A-Z]+[A-Z0-9-]*\b"
)
# Indian mobile: optional +91, 10 digits, optional internal spacing.
RE_PHONE = re.compile(
    r"(?:\+?91[\s-]?)?\b\d{5}[\s-]?\d{5}\b|\b\d{10}\b"
)
# Meridiem is matched as either "PM" or "P.M." but never "PM." with a
# sentence-final period, which would swallow the sentence punctuation.
RE_TIME = re.compile(
    r"\b(\d{1,2}):(\d{2})(?:\s*([APap]\.[Mm]\.|[APap][Mm]))?"
)
RE_DATE_NUM = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b")
RE_PRICE = re.compile(
    r"(?:₹|Rs\.?|INR)\s*(\d[\d,]*(?:\.\d+)?)|(\d[\d,]*(?:\.\d+)?)\s*(?:rupees|rupee)",
    re.I,
)
RE_DISTANCE = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(km|kms|kilometre[s]?|kilometer[s]?|m|metre[s]?|meter[s]?)\b",
    re.I,
)
RE_DURATION = re.compile(
    r"\b(\d+)\s*(min|mins|minute[s]?|hr|hrs|hour[s]?|sec|secs|second[s]?)\b",
    re.I,
)
RE_ORDINAL = re.compile(r"\b(\d+)(st|nd|rd|th)\b", re.I)
RE_DECIMAL = re.compile(r"\b\d+\.\d+\b")
RE_PIN = re.compile(r"\b[1-9]\d{5}\b")
RE_INT = re.compile(r"\b\d[\d,]*\b")


def _window_text(text: str, span: Span, window_chars: int = 40) -> str:
    lo = max(0, span.start - window_chars)
    return text[lo : span.start].lower()


def _has_trigger(text: str, span: Span, etype: EntityType) -> str | None:
    """Return the matched trigger word if one precedes this span."""
    ctx = _window_text(text, span)
    words = re.findall(r"[\w.஀-௿]+", ctx)
    recent = words[-TRIGGER_WINDOW:]
    for w in recent:
        if w in TRIGGERS.get(etype, set()):
            return w
    # Multi-word triggers.
    joined = " ".join(recent)
    for t in TRIGGERS.get(etype, set()):
        if " " in t and t in joined:
            return t
    return None


def _overlaps(span: Span, taken: list[Span]) -> bool:
    return any(not (span.end <= s.start or span.start >= s.end) for s in taken)


def detect_entities(
    text: str,
    *,
    lang: Lang = Lang.EN,
    upstream: list[Entity] | None = None,
) -> list[Entity]:
    """Detect normalizable entities in priority order.

    Priority matters: a 10-digit run is a phone number, not a cardinal, and a
    4-digit run after the word "OTP" is an OTP, not a year. Detectors run
    most-specific first and claim their character spans, so later detectors
    cannot re-claim them.
    """
    entities: list[Entity] = []
    taken: list[Span] = []

    # 0. Upstream-tagged entities win outright (Phase 0 Q-12).
    for e in upstream or []:
        entities.append(e)
        taken.append(e.span)

    def claim(
        span: Span,
        etype: EntityType,
        determinism: Determinism,
        **meta,
    ) -> None:
        if _overlaps(span, taken):
            return
        entities.append(
            Entity(
                type=etype,
                text=span.slice(text),
                span=span,
                lang=lang,
                determinism=determinism,
                provenance="inferred",
                meta=meta,
            )
        )
        taken.append(span)

    # 1. OTP - trigger-gated, EXACT. Any digit run of 4-8 after an OTP trigger.
    for m in re.finditer(r"\b\d{4,8}\b", text):
        span = Span(*m.span())
        trig = _has_trigger(text, span, EntityType.OTP)
        if trig:
            claim(span, EntityType.OTP, Determinism.EXACT, trigger=trig,
                  digits=len(m.group(0)))

    # 2. Phone - structural (10 digits / +91) OR trigger-gated, EXACT.
    for m in RE_PHONE.finditer(text):
        span = Span(*m.span())
        digits = re.sub(r"\D", "", m.group(0))
        trig = _has_trigger(text, span, EntityType.PHONE)
        if len(digits) >= 10 or trig:
            claim(span, EntityType.PHONE, Determinism.EXACT,
                  trigger=trig, digits=len(digits))

    # 3. Booking ID - structural alphanumeric mix, EXACT.
    for m in RE_BOOKING_ID.finditer(text):
        tok = m.group(0)
        if not (re.search(r"[A-Z]", tok) and re.search(r"\d", tok)):
            continue
        span = Span(*m.span())
        trig = _has_trigger(text, span, EntityType.BOOKING_ID)
        claim(span, EntityType.BOOKING_ID, Determinism.EXACT, trigger=trig)

    # 4. Time.
    for m in RE_TIME.finditer(text):
        h, mi = int(m.group(1)), int(m.group(2))
        if h <= 23 and mi <= 59:
            claim(Span(*m.span()), EntityType.TIME, Determinism.PREFERRED,
                  hour=h, minute=mi, meridiem=m.group(3))

    # 5. Date.
    for m in RE_DATE_NUM.finditer(text):
        claim(Span(*m.span()), EntityType.DATE, Determinism.OPEN,
              a=int(m.group(1)), b=int(m.group(2)), y=int(m.group(3)))

    # 6. Price.
    for m in RE_PRICE.finditer(text):
        val = m.group(1) or m.group(2)
        claim(Span(*m.span()), EntityType.PRICE, Determinism.PREFERRED,
              value=val)

    # 7. Distance.
    for m in RE_DISTANCE.finditer(text):
        claim(Span(*m.span()), EntityType.DISTANCE, Determinism.PREFERRED,
              value=m.group(1), unit=m.group(2).lower())

    # 8. Duration.
    for m in RE_DURATION.finditer(text):
        claim(Span(*m.span()), EntityType.DURATION, Determinism.PREFERRED,
              value=m.group(1), unit=m.group(2).lower())

    # 9. Ordinal.
    for m in RE_ORDINAL.finditer(text):
        claim(Span(*m.span()), EntityType.ORDINAL, Determinism.PREFERRED,
              value=int(m.group(1)))

    # 10. PIN code - trigger-gated only. A bare 6-digit number is NOT assumed
    #     to be a PIN code; Phase 0 N-AMB requires 600040 to be readable as a
    #     quantity when no address context is present.
    for m in RE_PIN.finditer(text):
        span = Span(*m.span())
        if _has_trigger(text, span, EntityType.PIN_CODE):
            claim(span, EntityType.PIN_CODE, Determinism.PREFERRED)

    # 11. Decimal.
    for m in RE_DECIMAL.finditer(text):
        claim(Span(*m.span()), EntityType.DECIMAL, Determinism.PREFERRED,
              value=m.group(0))

    # 12. Cardinal - the fallback for any remaining digit run.
    for m in RE_INT.finditer(text):
        claim(Span(*m.span()), EntityType.CARDINAL, Determinism.PREFERRED,
              value=m.group(0))

    entities.sort(key=lambda e: e.span.start)
    return entities
