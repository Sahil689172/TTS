# Phase 1 — Speaker Audit

**Date:** 2026-08-29

---

## 1. Result

> **BLOCKED — no model exists, therefore no speaker representation exists.**

| Question (Phase 1 Step 15) | Answer |
|---|---|
| Fixed speaker? | **N/A — no model** |
| Multi-speaker? | **N/A** |
| Speaker embedding? | **N/A** |
| Reference audio? | **N/A — no audio in the repository** |
| Language-specific speaker? | **N/A** |
| Same speaker across English/Tamil? | **N/A** |
| Future Tanglish compatibility? | **N/A — but see §3** |

Nothing was changed, as instructed.

## 2. Unresolved Phase 0 questions that block this audit

Phase 0 logged two questions that remain unanswered and make the speaker
requirement non-actionable:

- **Q-09** — *"'Speaker similarity' — similar to a specific reference voice, or
  self-consistency across utterances?"*
- **Q-11** — *"Single voice or multiple voices/personas?"*

The two readings imply very different projects:

- **Specific reference voice** → the project needs a recorded speaker, consent
  covering commercial use and redistribution (Phase 0 Q-07 / risk R-21), and
  possibly voice-cloning capability with its own licence restrictions.
- **Self-consistency only** → any stable synthetic identity suffices, and the
  data/consent burden largely disappears.

Phase 1 cannot choose between them and does not.

## 3. What Phase 1 nevertheless establishes for the speaker question

Phase 0 conflict **C-07** (speaker consistency vs multilingual adaptation) and
metric **O-05(ii)** (within-utterance embedding drift across a code-switch
boundary) both require the ability to *segment an utterance at its code-switch
boundaries*.

The Phase 1 frontend produces exactly that segmentation:

```python
r = Normalizer().normalize("உங்கள் pickup location எங்கே?")
r.lang_segments
# [('உங்கள்', Lang.TA), ('pickup location', Lang.EN), ('எங்கே?', Lang.TA)]
```

**Consequence:** once a model exists, O-05(ii) can be computed without new
segmentation work — the boundaries are already known from the text side. This
is a concrete Phase 1 contribution to the hardest speaker requirement, verified
by `tests/test_units.py::TestPipelineContract::test_language_segments_emitted`.

**Caveat:** text-side boundaries are not the same as *acoustic* boundaries. The
audio must still be force-aligned or segmented to compare embeddings on either
side of the switch. The text segmentation tells you where to look; it does not
by itself give you the audio frames.

## 4. Recommendation carried into Phase 2 (a recommendation, not a decision)

Phase 0 §19.6 warns that a speaker embedding entangled with language identity is
"very hard to disentangle later". Phase 2 candidate evaluation should therefore
record, per candidate, **whether speaker and language conditioning are
separable**, and treat non-separability as a significant risk against Phase 0
MR-06 and conflict C-07 — not as an automatic disqualifier, but as a cost that
must be priced into the decision.
