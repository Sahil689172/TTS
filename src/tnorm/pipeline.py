"""Normalization pipeline orchestrator.

Implements the Phase 0 §16 staged architecture end to end:

    raw text
      -> script detection
      -> language detection
      -> tokenization
      -> entity detection
      -> normalization / verbalization
      -> pronunciation representation
      -> TTS-ready representation

The pipeline emits a `NormalizationResult` carrying every intermediate stage,
not just the final string, so that §17 tests can assert on the stage that
actually failed rather than only on the end-to-end output.

IMPORTANT (Phase 0 §18, training/inference mismatch): the final stage emits
NORMALIZED TEXT with per-segment language tags. It deliberately does NOT emit
phonemes, because no model has been selected (Phase 0 RULE 2) and the required
symbol inventory is therefore unknown. `to_tagged_segments()` exposes the
language segmentation so a Phase 2/3 model that can condition on language can
consume it without re-deriving it.
"""

from __future__ import annotations

import re

from .entities import detect_entities
from .langid import detect_matrix_lang, is_code_mixed, token_lang
from .scripts import detect_script, is_mixed_script, tamil_digits_to_ascii
from .tokenizer import token_texts, tokenize
from .types import (
    Determinism,
    Entity,
    EntityType,
    Lang,
    NormalizationResult,
    Script,
    Span,
    Token,
)
from .verbalizer import (
    DEFAULT_CONFIG,
    NormConfig,
    verbalize_abbreviation,
    verbalize_entity,
)


class Normalizer:
    """Text normalization frontend for the taxi voice agent."""

    def __init__(self, config: NormConfig | None = None) -> None:
        self.cfg = config or DEFAULT_CONFIG

    # -- public API --------------------------------------------------------

    def normalize(
        self,
        text: str,
        *,
        lang: Lang | None = None,
        upstream_entities: list[Entity] | None = None,
    ) -> NormalizationResult:
        """Normalize `text` into a TTS-ready spoken string.

        `lang` overrides matrix-language detection when the caller already
        knows it. `upstream_entities` supplies dialog-system entity labels
        (Phase 0 Q-12); when given, they take priority over inference.
        """
        warnings: list[str] = []
        raw = text

        # Stage 1-2: normalize Tamil digits, detect script.
        work = tamil_digits_to_ascii(text)
        script = detect_script(work)

        # Stage 3: tokenize (splits Tamil suffixes off English stems).
        tokens = tokenize(work)
        words = token_texts(tokens)

        # Stage 2b: matrix language.
        matrix = lang or detect_matrix_lang(words)
        mixed = is_code_mixed(words)
        if matrix == Lang.UNKNOWN:
            matrix = Lang.EN
            warnings.append(
                "matrix language undetermined; defaulted to EN"
            )

        # Stage 4: entity detection.
        entities = detect_entities(
            work, lang=matrix, upstream=upstream_entities
        )

        # Stage 5: verbalization over the character stream.
        spoken = self._render(work, tokens, entities, matrix, warnings)

        # Stage 6: language segmentation for downstream conditioning.
        segments = self._segment_langs(spoken, matrix)

        return NormalizationResult(
            raw=raw,
            spoken=spoken,
            tokens=tokens,
            entities=entities,
            matrix_lang=matrix,
            is_code_mixed=mixed,
            lang_segments=segments,
            warnings=warnings,
        )

    # -- internals ---------------------------------------------------------

    def _render(
        self,
        text: str,
        tokens: list[Token],
        entities: list[Entity],
        matrix: Lang,
        warnings: list[str],
    ) -> str:
        """Rebuild the string with entities and abbreviations replaced."""
        # Map entity spans for fast lookup.
        ent_by_start = {e.span.start: e for e in entities}
        ent_ends = {e.span.start: e.span.end for e in entities}

        out: list[str] = []
        i = 0
        n = len(text)
        # Word list for abbreviation context.
        word_tokens = [t for t in tokens if t.script != Script.PUNCT]

        while i < n:
            if i in ent_by_start:
                e = ent_by_start[i]
                out.append(verbalize_entity(e, matrix, self.cfg))
                if e.type == EntityType.CARDINAL:
                    try:
                        from .numbers_ta import is_uncertain

                        if matrix in (Lang.TA, Lang.TA_LATIN) and is_uncertain(
                            int(re.sub(r"\D", "", e.text) or 0)
                        ):
                            warnings.append(
                                f"Tamil cardinal '{e.text}' exceeds the "
                                f"reviewed range; form is UNVALIDATED"
                            )
                    except ValueError:
                        pass
                i = ent_ends[i]
                continue

            ch = text[i]
            # Word run?
            m = re.match(r"[^\W\d_]+", text[i:], re.UNICODE)
            if m:
                word = m.group(0)
                idx = next(
                    (
                        k
                        for k, t in enumerate(word_tokens)
                        if t.span.start == i
                    ),
                    None,
                )
                prev_w = word_tokens[idx - 1].text if idx not in (None, 0) else None
                nxt_w = (
                    word_tokens[idx + 1].text
                    if idx is not None and idx + 1 < len(word_tokens)
                    else None
                )
                expanded = verbalize_abbreviation(word, prev_w, nxt_w)
                out.append(expanded if expanded is not None else word)

                # An abbreviation's trailing period belongs to the
                # abbreviation, not to the sentence - unless it IS the end of
                # the sentence. "St. Thomas" -> "saint Thomas" (period
                # dropped); "3rd Cross St." -> "third Cross street." (kept).
                if expanded is not None:
                    j = i + len(word)
                    if j < n and text[j] == ".":
                        rest = text[j + 1 :].lstrip()
                        if rest:
                            i = j + 1
                            continue

                # Re-attach a Tamil suffix that the tokenizer split off, so
                # the spoken form keeps the morphology: "Central-ல" reads as
                # "Central" + "ல" rather than losing the case marker.
                tok = word_tokens[idx] if idx is not None else None
                if tok is not None and tok.suffix:
                    # Emit the suffix as a separate whitespace-delimited unit.
                    # Concatenating it ("Centralல") would create a
                    # mixed-script word that no monolingual tokenizer can
                    # represent - exactly the failure Phase 0 §19.6 warns
                    # about. How a stranded suffix should be ACOUSTICALLY
                    # realized is an open Phase 2 question, recorded in
                    # docs/phase1/tanglish_implications.md.
                    out.append(" " + tok.suffix)
                    # Skip the raw suffix text in the source stream.
                    j = i + len(word)
                    while j < n and (text[j] == "-" or not text[j].isspace()):
                        if text[j].isspace():
                            break
                        j += 1
                    i = j
                    continue

                i += len(word)
                continue

            # A hyphen directly binding a Tamil suffix to a preceding token
            # ("5 minutes-ல") is a morphological joiner, not punctuation.
            if ch == "-" and i + 1 < n and detect_script(text[i + 1]) == Script.TAMIL:
                out.append(" ")
                i += 1
                continue

            out.append(ch)
            i += 1

        result = "".join(out)
        # Collapse whitespace and tidy spacing before punctuation.
        result = re.sub(r"\s+", " ", result)
        result = re.sub(r"\s+([,.!?;:])", r"\1", result)
        return result.strip()

    def _segment_langs(
        self, spoken: str, matrix: Lang
    ) -> list[tuple[str, Lang]]:
        """Group the spoken string into contiguous same-language segments.

        This is the artifact a language-conditioned acoustic model would
        consume. Producing it in Phase 1 costs nothing and preserves the
        option; discarding it would be the RULE 9 mistake Phase 0 §19.6 warns
        about.
        """
        segments: list[tuple[str, Lang]] = []
        cur: list[str] = []
        cur_lang: Lang | None = None
        for word in spoken.split():
            wl = token_lang(word)
            if wl == Lang.UNKNOWN:
                wl = cur_lang or matrix
            if cur_lang is None or wl == cur_lang:
                cur.append(word)
                cur_lang = wl
            else:
                segments.append((" ".join(cur), cur_lang))
                cur, cur_lang = [word], wl
        if cur and cur_lang is not None:
            segments.append((" ".join(cur), cur_lang))
        return segments


def normalize(text: str, **kw) -> str:
    """Convenience wrapper returning only the spoken string."""
    return Normalizer().normalize(text, **kw).spoken
