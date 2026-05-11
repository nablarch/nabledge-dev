# Expert Review: QA Engineer (Task 17 — subtitle fix)

**Date**: 2026-05-11
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 1 file

## Summary

2 Findings — fixed before commit

## Findings

### Finding 1 (FIXED): subtitle without body not tested

- Violated clause: `.claude/rules/development.md` — "Edge cases: Boundary values, empty inputs..." and non-negotiable constraint "subtitle without body"
- Description: No test for subtitle with no doc-level body. A regression in `subtitle_body` collection for empty list would go undetected.
- Fix applied: Added `test_subtitle_without_body_produces_empty_content` asserting `sections[0].content == ""`

### Finding 2 (FIXED): `test_subtitle_with_subsequent_sections` used loose assertions

- Violated clause: `.claude/rules/development.md` — "Assertions: Clear, specific, meaningful assertions" and "Bug-revealing cases"
- Description: `len(parts.sections) >= 1` didn't verify subsequent sections were preserved. Missing content assertions for both sections.
- Fix applied: Changed to `len(parts.sections) == 2`, added `"前文" in sections[0].content`, `sections[1].title`, `"後文" in sections[1].content`

## Observations

- RST syntax in tests uses short overline/underline delimiters that generate docutils level-2 warnings. Tests pass correctly but cleaner RST without warnings would be a better spec oracle.

## Positive Aspects

- `test_subtitle_only_file_produces_section` directly catches the original failure mode with assertions on title, level, and content.
- `test_no_subtitle_is_unchanged` uses `"—" not in parts.top_title` — correct regression guard form.
- Docstring clearly states the spec being enforced.

## Files Reviewed

- `tools/rbkc/tests/ut/test_rst_ast_visitor.py` (tests)
