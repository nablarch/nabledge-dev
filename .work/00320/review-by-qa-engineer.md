# Expert Review: QA Engineer

**Date**: 2026-05-07
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 3 files (Task 10 changes)

## Summary

0 Findings (after fix applied)

## Findings (original — all fixed)

### Finding 1: Display-text `:ref:` form skips cross-doc target validation

**Violated clause**: Spec §3-2-3 table row `inline role=ref`: "同上 (label 側から解決)" — the same four-check cross-doc validation applies to all `inline role=ref` nodes regardless of bare vs display-text form. No exception is made for display-text refs.

**Description**: The cross-doc validation block was inside `if not display and label not in seen_labels:`. When `:ref:`Custom Text <label>`` is used, `display` is non-empty, so the entire cross-doc block was skipped. A dangling cross-doc reference written as `:ref:`Custom Text <gone-label>`` produced no `[QL1] :ref: cross-doc` FAIL even when the target JSON did not exist.

**Fix applied**:
- Promoted the cross-doc check logic into a nested helper `_check_crossdoc_target(tgt)` within `check_source_links()`.
- Added a new path after the display-text JSON check that resolves the label from `label_map` and calls `_check_crossdoc_target()` for display-text refs (deduped by `seen_crossdoc_labels`).
- Bare-label path continues to call `_check_crossdoc_target()` via the same helper.
- Added test `test_fail_crossdoc_ref_display_text_form_json_missing` — confirmed RED before fix, GREEN after.

## Observations

- The `_section_titles_from_json` docstring first line says "(lowercased for matching)" but the function returns titles as-is. The function body is correct; the comment is misleading. No behavioral impact.
- `_section_titles_from_json` catches `Exception` broadly and returns empty set on parse failure, which produces a "section_title not found" FAIL rather than "JSON parse error" FAIL. No false negative — ゼロトレランス is maintained.
- The thin wrapper functions `_heading_slugs()` and `_json_section_slugs()` inside `check_ql1_link_targets()` could be inlined to reduce indirection, but this has no behavioral impact.
- The six original tests plus the new display-text test provide complete coverage of all four FAIL modes and two PASS modes.

## Positive Aspects

- The helper function design (`_check_crossdoc_target`) correctly shares the cross-doc logic between bare-label and display-text paths, eliminating the risk of future drift.
- The `seen_crossdoc_labels` set prevents double-reporting when the same label appears in both bare and display-text forms in the same source file.
- All test assertions are spec-derived, not implementation-derived.
- 313/313 tests pass.

## Files Reviewed

- `tools/rbkc/scripts/verify/verify.py` (source code)
- `tools/rbkc/tests/ut/test_verify.py` (tests)
- `tools/rbkc/scripts/run.py` (plumbing)
