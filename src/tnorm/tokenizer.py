"""Tokenization with script segmentation and Tamil-suffix splitting.

Third stage of the Phase 0 §16 pipeline.

The distinctive requirement here is Phase 0 LR-06 / §8 N15: a Tamil grammatical
suffix attached to an English token, as in "Chennai Central-ல", "5 minutes-ல"
or "booking-ah". A naive whitespace tokenizer produces the single token
"Central-ல", which is neither English nor Tamil and which no monolingual
tokenizer can represent. Splitting it here - while RETAINING the link between
stem and suffix on the Token object - is what keeps intra-word code-mixing
representable downstream.

Suffix detection runs at CHUNK level, before sub-word regex tokenization,
because the hyphen would otherwise be consumed as punctuation and the
stem/suffix relationship lost.
"""

from __future__ import annotations

import re

from .langid import token_lang
from .scripts import Script, char_script, detect_script, has_latin, has_tamil
from .types import Lang, Span, Token

# Romanized Tamil suffixes that attach to English stems ("booking-ah").
# Only applied after an explicit hyphen: splitting unhyphenated Latin words on
# these endings would shred ordinary English ("area" -> "are" + "a").
LATIN_TAMIL_SUFFIXES = {
    "kku", "ukku", "kitta", "oda", "ode", "ila", "il", "la", "le", "ah",
    "aa", "a", "um", "yum", "ku",
}

_WORD_RE = re.compile(
    r"""
    (?P<num>\d[\d,]*\.?\d*)          # numeric run (commas/decimal kept)
    | (?P<word>[^\W\d_]+)            # letter run (any script)
    | (?P<punct>[^\s\w]|_)           # single punctuation/symbol
    """,
    re.VERBOSE | re.UNICODE,
)

_LEAD_PUNCT = re.compile(r"^[^\w஀-௿]+")
_TRAIL_PUNCT = re.compile(r"[^\w஀-௿]+$")


def _peel(core: str) -> tuple[str, str, str]:
    """Split a chunk into (leading punct, core, trailing punct)."""
    lead = _LEAD_PUNCT.match(core)
    lead_s = lead.group(0) if lead else ""
    rest = core[len(lead_s) :]
    trail = _TRAIL_PUNCT.search(rest)
    trail_s = trail.group(0) if trail else ""
    if trail_s:
        rest = rest[: -len(trail_s)]
    return lead_s, rest, trail_s


def _detect_suffix(core: str) -> tuple[str, str | None, Script | None]:
    """Detect an English/numeric stem carrying a Tamil suffix.

    Handles four shapes:
        Central-ல      hyphen + Tamil-script suffix
        Centralல       no hyphen + Tamil-script suffix
        10-ல           digits + hyphen + Tamil-script suffix
        booking-ah     hyphen + romanized Tamil suffix

    Returns (stem, suffix, suffix_script). suffix is None when no split applies.
    """
    if not core:
        return core, None, None

    # Hyphenated forms.
    if "-" in core:
        stem, _, tail = core.rpartition("-")
        if stem and tail:
            if has_tamil(tail) and not has_tamil(stem):
                return stem, tail, Script.TAMIL
            if tail.lower() in LATIN_TAMIL_SUFFIXES and has_latin(stem):
                return stem, tail, Script.LATIN

    # Unhyphenated Latin-stem + Tamil-suffix ("Centralல").
    if has_latin(core) and has_tamil(core):
        for i, ch in enumerate(core):
            if char_script(ch) == Script.TAMIL:
                stem, suffix = core[:i], core[i:]
                if stem and not has_tamil(stem):
                    return stem, suffix, Script.TAMIL
                break

    # Digits + Tamil suffix without hyphen ("10ல").
    if core[0].isdigit() and has_tamil(core):
        for i, ch in enumerate(core):
            if char_script(ch) == Script.TAMIL:
                return core[:i], core[i:], Script.TAMIL

    return core, None, None


def tokenize(text: str) -> list[Token]:
    """Tokenize into script- and language-tagged tokens."""
    tokens: list[Token] = []

    for m in re.finditer(r"\S+", text):
        chunk = m.group(0)
        base = m.start()
        lead, core, trail = _peel(chunk)
        core_off = base + len(lead)

        if lead:
            for j, ch in enumerate(lead):
                tokens.append(
                    Token(ch, Span(base + j, base + j + 1), Script.PUNCT)
                )

        if core:
            stem, suffix, suf_script = _detect_suffix(core)
            if suffix is not None:
                tokens.append(
                    Token(
                        text=stem,
                        span=Span(core_off, core_off + len(stem)),
                        script=detect_script(stem),
                        lang=token_lang(stem),
                        suffix=suffix,
                        suffix_script=suf_script,
                    )
                )
            else:
                for sub in _WORD_RE.finditer(core):
                    piece = sub.group(0)
                    s = core_off + sub.start()
                    e = core_off + sub.end()
                    if sub.lastgroup == "punct":
                        tokens.append(Token(piece, Span(s, e), Script.PUNCT))
                    elif sub.lastgroup == "num":
                        tokens.append(Token(piece, Span(s, e), Script.DIGIT))
                    else:
                        tokens.append(
                            Token(
                                text=piece,
                                span=Span(s, e),
                                script=detect_script(piece),
                                lang=token_lang(piece),
                            )
                        )

        if trail:
            toff = core_off + len(core)
            for j, ch in enumerate(trail):
                tokens.append(Token(ch, Span(toff + j, toff + j + 1), Script.PUNCT))

    return tokens


def token_texts(tokens: list[Token]) -> list[str]:
    """Surface strings of word-like tokens (punctuation excluded)."""
    return [t.text for t in tokens if t.script != Script.PUNCT]
