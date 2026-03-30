# Notes

## 2026-03-30

### Decision: Prompt-only fix — no code changes needed

The root causes (E-1 through E-5, D-1) are entirely in the prompt design for fix.md and content_check.md.
Phase E and Phase D Python code (phase_e_fix.py, phase_d_content_check.py) correctly pass source content
and findings to the LLM — the problem is the LLM receives insufficient constraints.

### Fix approach for E-1 through E-5

Added a `## Constraints` section at the bottom of fix.md with five explicit rules:

- **E-1** (scope creep): "Modify only sections referenced in findings. Do not change any section with no finding."
- **E-2** (fabrication during omission): "Copy information verbatim from source_evidence passage. Do not paraphrase or expand."
- **E-3** (notation corruption): "Preserve source notation exactly including typos, RST syntax, non-standard formatting."
- **E-4** (adjacent text corruption): "When editing a section, copy all content outside the edited location exactly as-is."
- **E-5** (implicit rule fabrication): "Do not generalize implicit patterns into explicit rules. Only include rules explicitly stated in source."

### Fix approach for D-1

Added severity assignment rules with a "stability rule" to V1 (Omission) and V2 (Fabrication) in content_check.md.

- `critical` requires articulating: "Without this, an AI would incorrectly advise: {specific wrong advice}"
- If that statement cannot be made clearly → assign `minor`

This anchors severity to a concrete, articulable outcome rather than subjective judgment, which should reduce flip-flop across rounds.

### Why this approach

The "stability rule" pattern (requiring explicit articulation of the wrong outcome before assigning critical)
is a standard technique for reducing LLM judgment variability. The LLM must commit to a concrete claim,
which is harder to reverse on a re-run than a vague subjective judgment.

### Tests

All 252 tests pass. Prompt files are not tested directly but prompt changes don't affect unit test coverage
(which tests Python logic). Integration testing would require actual LC runs.
