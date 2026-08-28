"""Domain lexicons for the taxi/transportation voice agent.

Phase 0 categories N8 (abbreviations), N9 (vehicles), N13 (locations).

These are deliberately small, hand-auditable dictionaries rather than learned
resources. Phase 0 §8 N13 flags a curated Chennai-area location lexicon as a
Phase 1 deliverable; what exists here is a SEED, explicitly incomplete, and
its coverage gap is recorded in docs/phase1/normalization_audit.md.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# N8 - Abbreviations
# Value is the spoken form. LETTERS means "spell out the letters".
# --------------------------------------------------------------------------
LETTERS = "__LETTERS__"

ABBREVIATIONS: dict[str, str] = {
    "OTP": LETTERS,
    "ETA": LETTERS,
    "AC": LETTERS,
    "A/C": LETTERS,
    "SUV": LETTERS,
    "GPS": LETTERS,
    "ID": LETTERS,
    "XL": LETTERS,
    "PNR": LETTERS,
    "OMR": LETTERS,
    "ECR": LETTERS,
    "KM": "kilometres",
    "KMS": "kilometres",
    "HR": "hours",
    "MIN": "minutes",
    "MINS": "minutes",
    "RS": "rupees",
    "RS.": "rupees",
    "INR": "rupees",
    "NO.": "number",
    "NR.": "near",
    "APT": "apartment",
    "EXTN": "extension",
    "RD": "road",
    "RD.": "road",
    "AVE": "avenue",
    "MT": "mount",
}

# Abbreviations whose expansion depends on context (Phase 0 §8 N8/N-AMB).
# Each maps to {context_hint: expansion}. `_default` is used when no hint
# matches. These are the release-blocking ambiguity traps.
AMBIGUOUS_ABBREVIATIONS: dict[str, dict[str, str]] = {
    "ST": {
        # "St. Thomas Mount" -> Saint ; "3rd Cross St." -> Street
        "_leading": "saint",    # abbreviation precedes a proper noun
        "_trailing": "street",  # abbreviation follows a road name
        "_default": "street",
    },
    "ST.": {"_leading": "saint", "_trailing": "street", "_default": "street"},
    "DR": {
        # "Dr. Kumar" -> Doctor ; "Palm Grove Dr." -> Drive
        "_leading": "doctor",
        "_trailing": "drive",
        "_default": "doctor",
    },
    "DR.": {"_leading": "doctor", "_trailing": "drive", "_default": "doctor"},
}

# --------------------------------------------------------------------------
# N9 - Vehicle types. Brand names are left as-is for the acoustic model;
# only abbreviations and letter-forms are expanded.
# --------------------------------------------------------------------------
VEHICLES: dict[str, str] = {
    "SUV": LETTERS,
    "XL": LETTERS,
    "AC": LETTERS,
    "SEDAN": "sedan",
    "MINI": "mini",
    "AUTO": "auto",
    "BIKE": "bike",
    "PRIME": "prime",
}

VEHICLE_BRANDS: set[str] = {
    "innova", "etios", "dzire", "swift", "xylo", "ertiga", "amaze",
    "indica", "tiago", "aura", "wagonr",
}

# --------------------------------------------------------------------------
# N13 - Chennai-area location seed lexicon.
# `spoken` overrides the surface form where the written form misleads.
# --------------------------------------------------------------------------
LOCATIONS: dict[str, str] = {
    # "T. Nagar" is written with an initial but spoken as the letter name.
    "T. NAGAR": "T Nagar",
    "T.NAGAR": "T Nagar",
    "OMR": LETTERS,
    "ECR": LETTERS,
    "CHENNAI CENTRAL": "Chennai Central",
    "KOYAMBEDU": "Koyambedu",
    "VELACHERY": "Velachery",
    "GUINDY": "Guindy",
    "ADYAR": "Adyar",
    "TAMBARAM": "Tambaram",
    "EGMORE": "Egmore",
    "ANNA NAGAR": "Anna Nagar",
    "MYLAPORE": "Mylapore",
    "SAIDAPET": "Saidapet",
    "PORUR": "Porur",
    "SHOLINGANALLUR": "Sholinganallur",
}

# Words that mark the preceding/following token as a road-name context, used
# to disambiguate ST / DR.
ROAD_CONTEXT: set[str] = {
    "cross", "main", "road", "rd", "street", "avenue", "lane", "nagar",
    "colony", "extension", "extn", "salai", "grove", "park",
}
