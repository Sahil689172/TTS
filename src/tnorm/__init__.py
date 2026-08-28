"""tnorm - text normalization frontend for Tamil / English / Tanglish TTS.

Phase 1 foundation. Implements the staged architecture specified in
Phase 0 §16 and is tested against the frozen case set from Phase 0 §8.

Public API:
    Normalizer, normalize, NormConfig, Lang, EntityType
"""

from .langid import detect_matrix_lang, is_code_mixed, token_lang
from .pipeline import Normalizer, normalize
from .scripts import detect_script, is_mixed_script
from .tokenizer import tokenize
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
from .verbalizer import DEFAULT_CONFIG, NormConfig

__version__ = "0.1.0"

__all__ = [
    "Normalizer", "normalize", "NormConfig", "DEFAULT_CONFIG",
    "Lang", "Script", "EntityType", "Determinism",
    "Entity", "Token", "Span", "NormalizationResult",
    "tokenize", "detect_script", "is_mixed_script",
    "detect_matrix_lang", "is_code_mixed", "token_lang",
]
