# Expert Review: QA Engineer — Session 37 Top-Level Hints

**Date**: 2026-04-22
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: test_run.py, test_verify.py, test_docs.py, run.py, verify.py, rbkc-json-schema-design.md

## Overall Assessment

**Rating**: 4.2/5
**Summary**: Test coverage is strong on the main injection, rendering and three-way-consistency paths, including the `__file__` sentinel happy-path. A few edge cases that would cause silent wrong-output were not yet asserted; the top two were implemented this session.

## Key Gaps

### High Priority

**H1. `__file__` sentinel in the middle of array is not tested**
- Description: `_pop_hints_for_title` must not consume a `__file__`-titled head as a section.
- Decision: **Implement Now** — added `test_file_sentinel_head_does_not_match_section_title` locking the behaviour.

**H2. Stray docs MD top-level block without hints file expectation**
- Description: Verify did not flag a docs MD with a stray `<details>keywords</details>` block when the hints file had no file-level entry and JSON had no top-level hints. Real gap in three-way consistency.
- Decision: **Implement Now** — added RED test `test_fail_stray_docs_md_top_hints_without_hints_file_expectation`, implemented fix in `check_hints_file_consistency` to flag stray top-level blocks in both directions.

### Medium Priority

**M1. Empty-string malformed hints file entry** — deferred (not an observed case; would require deliberately malformed input).
**M2. Same section title as top title combined with sentinel** — deferred (interplay covered by separate tests for each layer).
**M3. Substring-assertion fragility** — acknowledged; current tests still catch regressions.

### Low Priority

**L1. `_pop_top_level_hints` direct unit coverage**
- Decision: **Implement Now** — added `TestPopTopLevelHints` with 5 tests covering empty pending, sentinel head, title-match, sentinel beats any top title, non-match preservation.

**L2. `_parse_docs_md_hints` independent tests** — deferred; indirectly covered via consistency tests.

## Well-Covered Areas

- `_pop_hints_for_title`: happy path, same-title twice, mismatch-leaves-pending, empty pending
- `_convert_and_write`: both sentinel variants, `index[]` with/without `__file__` head, fallback path
- `check_hints_file_consistency` top-level: all-consistent, JSON drift, docs MD drift, missing JSON field, sentinel happy path, sentinel FAIL, no file-level entry expected, stray docs MD block
- Docs rendering: ordering (h1 → keywords → preamble), omitted-when-empty, rendered-when-content-empty

## Changes Applied

- H1: Added `test_file_sentinel_head_does_not_match_section_title` in `TestPopHintsForTitle`.
- H2: Added `test_fail_stray_docs_md_top_hints_without_hints_file_expectation` (RED), then implemented bidirectional docs-MD top-level check in `check_hints_file_consistency` (GREEN).
- L1: Added `TestPopTopLevelHints` class with 5 tests.
