"""Unit tests for the individual normalization stages.

Phase 0 §21 requires automated tests for normalization, script detection,
language detection, entity detection and configuration. Testing each stage
separately means a failure identifies WHICH stage broke, which the end-to-end
case tests cannot do on their own.
"""

from __future__ import annotations

import pytest

from tnorm import (
    EntityType,
    Lang,
    NormConfig,
    Normalizer,
    Script,
    detect_matrix_lang,
    detect_script,
    is_code_mixed,
    is_mixed_script,
    token_lang,
    tokenize,
)
from tnorm.entities import detect_entities
from tnorm.numbers_en import cardinal, clock_time, digit_by_digit, ordinal, year
from tnorm.numbers_ta import cardinal as ta_cardinal
from tnorm.numbers_ta import digit_by_digit as ta_dbd
from tnorm.scripts import tamil_digits_to_ascii


# ---------------------------------------------------------------- scripts
class TestScriptDetection:
    def test_pure_latin(self):
        assert detect_script("Your cab is here") is Script.LATIN

    def test_pure_tamil(self):
        assert detect_script("உங்கள் வண்டி") is Script.TAMIL

    def test_mixed_script(self):
        assert detect_script("உங்கள் pickup location") is Script.MIXED

    def test_digits_do_not_make_text_mixed(self):
        # "Chennai 600040" is Latin text with digits, not mixed-script.
        assert detect_script("Chennai 600040") is Script.LATIN

    def test_is_mixed_script(self):
        assert is_mixed_script("Chennai Central-ல")
        assert not is_mixed_script("Chennai Central")
        assert not is_mixed_script("சென்னை சென்ட்ரல்")

    def test_tamil_digits_converted(self):
        assert tamil_digits_to_ascii("௧௦ நிமிடம்") == "10 நிமிடம்"


# ----------------------------------------------------------------- langid
class TestLanguageDetection:
    def test_tamil_script_token(self):
        assert token_lang("உங்கள்") is Lang.TA

    def test_english_token(self):
        assert token_lang("pickup") is Lang.EN

    def test_romanized_tamil_token(self):
        assert token_lang("pannunga") is Lang.TA_LATIN
        assert token_lang("irukka") is Lang.TA_LATIN

    def test_matrix_language_tamil_with_english_inserts(self):
        toks = ["உங்கள்", "pickup", "location", "எங்கே"]
        assert detect_matrix_lang(toks) is Lang.TA

    def test_matrix_language_latin_tamil(self):
        toks = ["unga", "pickup", "location", "enga"]
        assert detect_matrix_lang(toks) is Lang.TA_LATIN

    def test_matrix_language_pure_english(self):
        toks = ["Your", "cab", "will", "arrive", "soon"]
        assert detect_matrix_lang(toks) is Lang.EN

    def test_code_mixed_detection(self):
        assert is_code_mixed(["உங்கள்", "pickup", "location"])
        assert not is_code_mixed(["Your", "cab", "is", "here"])


# -------------------------------------------------------------- tokenizer
class TestTokenizer:
    def test_tamil_suffix_on_english_stem(self):
        toks = tokenize("Chennai Central-ல")
        suffixed = [t for t in toks if t.suffix]
        assert len(suffixed) == 1
        assert suffixed[0].text == "Central"
        assert suffixed[0].suffix == "ல"
        # The stem must keep its ENGLISH identity - this is the property that
        # keeps intra-word code-mixing representable (Phase 0 §19.6).
        assert suffixed[0].lang is Lang.EN

    def test_latin_tamil_suffix(self):
        toks = tokenize("booking-ah cancel pannunga")
        suffixed = [t for t in toks if t.suffix]
        assert suffixed and suffixed[0].text == "booking"
        assert suffixed[0].suffix == "ah"

    def test_plain_hyphen_not_treated_as_suffix(self):
        toks = tokenize("pick-up point")
        assert not any(t.suffix for t in toks)

    def test_punctuation_preserved(self):
        toks = tokenize("Hello, world!")
        assert any(t.script is Script.PUNCT for t in toks)


# --------------------------------------------------------------- entities
class TestEntityDetection:
    def test_otp_requires_trigger(self):
        ents = detect_entities("Your OTP is 4821.")
        assert EntityType.OTP in [e.type for e in ents]

    def test_bare_number_is_not_otp(self):
        ents = detect_entities("The fare is 4821 rupees.")
        assert EntityType.OTP not in [e.type for e in ents]

    def test_phone_detected_structurally(self):
        ents = detect_entities("Call 9876543210 now.")
        assert EntityType.PHONE in [e.type for e in ents]

    def test_booking_id_detected(self):
        ents = detect_entities("Booking TN45AB1234 confirmed.")
        assert EntityType.BOOKING_ID in [e.type for e in ents]

    def test_time_detected(self):
        ents = detect_entities("Arriving at 7:30 PM.")
        assert EntityType.TIME in [e.type for e in ents]

    def test_entities_do_not_overlap(self):
        ents = detect_entities("Booking TN45AB1234 fare Rs. 250 at 7:30 PM")
        spans = sorted((e.span.start, e.span.end) for e in ents)
        for (s1, e1), (s2, _) in zip(spans, spans[1:]):
            assert e1 <= s2, f"overlapping entity spans: {spans}"

    def test_upstream_entities_take_priority(self):
        """Phase 0 Q-12: dialog-system labels override inference."""
        from tnorm.types import Determinism, Entity, Span

        upstream = [
            Entity(
                type=EntityType.OTP,
                text="4821",
                span=Span(12, 16),
                lang=Lang.EN,
                determinism=Determinism.EXACT,
                provenance="upstream",
            )
        ]
        ents = detect_entities("The fare is 4821 rupees.", upstream=upstream)
        otp = [e for e in ents if e.type is EntityType.OTP]
        assert otp and otp[0].provenance == "upstream"


# ------------------------------------------------------------ numbers: EN
class TestEnglishNumbers:
    @pytest.mark.parametrize(
        "n,expected",
        [
            (0, "zero"), (7, "seven"), (13, "thirteen"), (21, "twenty-one"),
            (100, "one hundred"), (250, "two hundred fifty"),
            (1234, "one thousand two hundred thirty-four"),
        ],
    )
    def test_cardinal(self, n, expected):
        assert cardinal(n) == expected

    def test_indian_grouping(self):
        assert cardinal(100000, grouping="indian") == "one lakh"

    def test_western_grouping(self):
        assert cardinal(1000000, grouping="western") == "one million"

    @pytest.mark.parametrize(
        "n,expected",
        [(1, "first"), (2, "second"), (3, "third"), (5, "fifth"),
         (20, "twentieth"), (23, "twenty-third")],
    )
    def test_ordinal(self, n, expected):
        assert ordinal(n) == expected

    def test_digit_by_digit_preserves_leading_zeros(self):
        assert digit_by_digit("0042") == "zero zero four two"

    def test_year_reading(self):
        assert year(2026) == "twenty twenty-six"

    def test_clock_leading_zero_minute(self):
        assert clock_time(7, 5) == "seven oh five"

    def test_clock_midnight_and_noon(self):
        assert clock_time(12, 0, "AM") == "twelve midnight"
        assert clock_time(12, 0, "PM") == "twelve noon"


# ------------------------------------------------------------ numbers: TA
class TestTamilNumbers:
    """PRELIMINARY - forms are unvalidated by a native speaker.

    These tests pin CURRENT BEHAVIOUR so that changes are detected. They do
    NOT assert linguistic correctness, which has not been established.
    """

    def test_digits(self):
        assert ta_dbd("40") == "நான்கு பூஜ்யம்"

    def test_digit_language_switch_to_english(self):
        assert ta_dbd("4821", digit_language="en") == "four eight two one"

    def test_small_cardinal(self):
        assert ta_cardinal(10) == "பத்து"
        assert ta_cardinal(5) == "ஐந்து"

    def test_compound_uses_combining_form(self):
        assert ta_cardinal(21).startswith("இருபத்தி")


# ----------------------------------------------------------------- config
class TestConfiguration:
    def test_grouping_config_changes_output(self):
        n_in = Normalizer(NormConfig(grouping="indian"))
        n_we = Normalizer(NormConfig(grouping="western"))
        a = n_in.normalize("We served 100000 rides.").spoken
        b = n_we.normalize("We served 100000 rides.").spoken
        assert "lakh" in a
        assert "thousand" in b
        assert a != b

    def test_ta_digit_language_config(self):
        n_ta = Normalizer(NormConfig(ta_digit_language="ta"))
        n_en = Normalizer(NormConfig(ta_digit_language="en"))
        a = n_ta.normalize("உங்கள் OTP 4821.").spoken
        b = n_en.normalize("உங்கள் OTP 4821.").spoken
        assert a != b
        assert "four eight two one" in b


# --------------------------------------------------------------- pipeline
class TestPipelineContract:
    def test_result_carries_all_stages(self):
        r = Normalizer().normalize("Your OTP is 4821.")
        assert r.raw and r.spoken
        assert r.tokens
        assert r.entities
        assert r.matrix_lang is not Lang.UNKNOWN

    def test_language_segments_emitted(self):
        """Language segmentation must survive to the output (RULE 9)."""
        r = Normalizer().normalize("உங்கள் pickup location எங்கே?")
        assert r.lang_segments
        langs = {lg for _, lg in r.lang_segments}
        assert Lang.TA in langs and Lang.EN in langs

    def test_empty_input(self):
        r = Normalizer().normalize("")
        assert r.spoken == ""

    def test_idempotent_on_plain_text(self):
        n = Normalizer()
        text = "Your cab is arriving."
        once = n.normalize(text).spoken
        twice = n.normalize(once).spoken
        assert once == twice
