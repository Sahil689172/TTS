"""Per-token language identification.

Second stage of the Phase 0 §16 pipeline. Three-way decision:
    EN        - English
    TA        - Tamil in Tamil script
    TA_LATIN  - Tamil written in Latin script (Phase 0 LR-05, PN-16)

Tamil-script tokens are decidable from Unicode alone. The hard case, and the
one that matters for Tanglish, is separating EN from TA_LATIN inside a Latin
string: "unga pickup location enga" is four Latin tokens of which two are
Tamil and two are English.

METHOD: closed-lexicon lookup plus orthographic cues. This is deliberately NOT
a learned model (Phase 0 §16: "Do NOT build a large ML normalization model").
It is a foundation with a measured error rate, not a solved problem - see
`docs/phase1/normalization_audit.md` for the measured accuracy and the
known failure modes.
"""

from __future__ import annotations

import re

from .scripts import Script, char_script, has_latin, has_tamil
from .types import Lang

# Romanized Tamil function words and high-frequency taxi-domain verbs.
# Closed class: these are the words that actually carry the matrix language in
# Chennai code-mixed speech. Kept small and auditable on purpose.
TA_LATIN_LEXICON: set[str] = {
    # pronouns / determiners
    "naan", "naa", "nee", "neenga", "unga", "ungal", "unga", "avaru", "avar",
    "avanga", "adhu", "idhu", "andha", "indha", "enna", "yaaru", "yaar",
    "engey", "enga", "engae", "eppo", "eppadi", "edhu", "namma", "nammaloda",
    "en", "un", "avan", "aval", "naanga", "ungaluku", "ungalukku",
    # verbs (colloquial spoken forms)
    "irukku", "irukka", "irukku", "iruku", "iruka", "varum", "varuvaar",
    "varuvar", "vandhu", "vandhutu", "vanga", "vaanga", "poganum", "ponum",
    "pannunga", "panunga", "pannu", "pannalam", "sollunga", "solunga",
    "pesunga", "pesalam", "kudunga", "kudu", "parunga", "paarunga",
    "wait", "mudiyum", "mudiyathu", "venum", "vendam", "aagum", "aachu",
    "irundhu", "irundha", "poitu", "poidalam", "kelunga",
    # postpositions / particles / connectives
    "kitta", "kooda", "mele", "keezha", "pakkam", "pathi", "varaikkum",
    "appuram", "aprom", "mattum", "mudhal", "romba", "konjam", "seekiram",
    "ippo", "innum", "already", "illa", "illai", "aama", "aamaa", "sari",
    "seri", "ok", "thaan", "than", "dhaan", "ah", "aa", "la", "le", "la",
    # taxi domain
    "vandi", "car", "auto", "vandiya", "driver", "ooru", "veedu", "kadai",
    "rusu", "kaasu", "panam", "neram", "vazhi", "theriyuma", "theriyum",
}

# Words that are unambiguously English in this domain and must never be
# mistaken for romanized Tamil even though they look short/vowel-heavy.
EN_STRONG: set[str] = {
    "a", "an", "the", "is", "are", "was", "were", "will", "be", "been",
    "your", "you", "our", "we", "i", "he", "she", "it", "they", "this",
    "that", "and", "or", "but", "if", "in", "on", "at", "to", "for", "of",
    "with", "from", "by", "please", "thank", "thanks", "sorry", "hello",
    "cab", "taxi", "ride", "driver", "pickup", "drop", "location", "booking",
    "cancel", "cancelled", "confirm", "confirmed", "arrive", "arriving",
    "minutes", "minute", "min", "mins", "hour", "hours", "fare", "price",
    "otp", "phone", "number", "id", "address", "time", "date", "today",
    "tomorrow", "now", "soon", "way", "trip", "customer", "support",
    "sedan", "suv", "auto", "mini", "prime", "bike", "central", "airport",
    "station", "road", "street", "nagar", "waiting", "charge", "toll",
    "surge", "distance", "km", "kilometre", "kilometer", "rupees",
}

# Orthographic cues for romanized Tamil. Each is a weak signal; they are only
# consulted when the lexicons do not decide.
_TA_LATIN_PATTERNS = [
    re.compile(r"(zh)", re.I),            # 'zh' transcribes ழ, rare in English
    re.compile(r"(ngal|nga|ngk)$", re.I),  # -nga imperative/honorific ending
    re.compile(r"(kk|tt|pp|chch)", re.I),  # geminates common in Tamil
    re.compile(r"(aa|ee|oo|ai|au)", re.I),  # long-vowel digraphs
    re.compile(r"(udhu|adhu|idhu|odhu)$", re.I),
]


def _latin_token_lang(tok: str) -> Lang:
    """Classify a single Latin-script token."""
    low = tok.lower().strip("'-.")
    if not low:
        return Lang.UNKNOWN
    if low in EN_STRONG:
        return Lang.EN
    if low in TA_LATIN_LEXICON:
        return Lang.TA_LATIN
    score = sum(1 for p in _TA_LATIN_PATTERNS if p.search(low))
    if score >= 2:
        return Lang.TA_LATIN
    return Lang.EN


def token_lang(tok: str) -> Lang:
    """Language of a single token, from script plus lexicon."""
    if has_tamil(tok):
        return Lang.TA
    if has_latin(tok):
        return _latin_token_lang(tok)
    return Lang.UNKNOWN


def detect_matrix_lang(tokens: list[str]) -> Lang:
    """The matrix (host) language of an utterance.

    Definition used: the language contributing the most *content-bearing*
    tokens, with Tamil-script presence acting as a strong prior. Phase 0 §8 N14
    requires the number-reading language to follow the matrix language, so this
    function has direct downstream consequences and is tested separately.
    """
    langs = [token_lang(t) for t in tokens if any(c.isalpha() for c in t)]
    if not langs:
        return Lang.UNKNOWN
    n_ta = sum(1 for x in langs if x == Lang.TA)
    n_talatin = sum(1 for x in langs if x == Lang.TA_LATIN)
    n_en = sum(1 for x in langs if x == Lang.EN)

    # Any Tamil-script content makes Tamil the matrix unless English strictly
    # dominates: "உங்கள் pickup location எங்கே?" is a Tamil sentence with
    # English inserts, not an English sentence.
    if n_ta > 0 and n_ta + n_talatin >= 1 and n_en <= (n_ta + n_talatin) + 1:
        return Lang.TA
    if n_ta > 0:
        return Lang.TA
    if n_talatin > n_en:
        return Lang.TA_LATIN
    if n_talatin > 0 and n_en > 0:
        # Latin-script code-mix with English majority: still Tamil matrix if
        # the Tamil tokens are function words carrying the clause structure.
        return Lang.TA_LATIN
    return Lang.EN


def is_code_mixed(tokens: list[str]) -> bool:
    """True when an utterance mixes Tamil (either script) with English."""
    langs = {token_lang(t) for t in tokens if any(c.isalpha() for c in t)}
    has_ta = bool(langs & {Lang.TA, Lang.TA_LATIN})
    return has_ta and (Lang.EN in langs)
