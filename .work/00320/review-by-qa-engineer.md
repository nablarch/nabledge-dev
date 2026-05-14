# Expert Review: QA Engineer

**Date**: 2026-05-11
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 4 test files (test_docs.py, test_labels_doc_map.py, test_rst_ast_visitor.py, test_verify.py)

## Summary

0 Findings

## Findings

None.

## Observations

- **`test_pass_local_label_no_file_id_skips_cross_doc_check` assertion could be tighter**: `assert not any("missing-page" in i for i in issues)` would pass even if unrelated issues exist. `assert issues == []` would be equally correct and more precise. Not a spec violation.
- **No test for malformed target JSON**: `_section_titles_from_json` silently returns `set()` on `ValueError`. FAIL-on-corrupt behavior is correct under ゼロトレランス and indirectly covered by `test_fail_section_title_not_in_target_json`. A dedicated test would be explicit but is not required by current spec clauses.
- **No test for ATX heading with closing markers**: `_heading_slugs_from_md` regex strips optional closing `##`. Appears correct but untested.
- **`TestScanRstLabelsDocutilsAST` exercises `build_label_map` (public API)** rather than `_scan_rst_labels` directly. Functionally sound — public entry point is the correct test target.

## Positive Aspects

- **Test isolation is excellent**: all new tests use `tmp_path` and construct minimal file trees without real-repo dependencies.
- **Oracle is spec-pinned**: assertions are derived from spec §3-2-3 and documented RST/docutils semantics, not from implementation output — no circular tests.
- **Dedup correctness is explicitly tested**: `test_dedup_same_label_in_multiple_sections_reported_once` and `test_fail_different_labels_same_file_id_different_section_titles` pin both sides of the dedup invariant.
- **Bug-revealing cases are present**: `test_h1_direct_label_gives_empty_section_title` and `test_jsp_comment_arrow_does_not_corrupt_section_title` directly reproduce the two pre-fix failure modes (692-count QL1 FAILs and section_title corruption).
- **Both display-text and bare-label `:ref:` forms are tested** for JSON and docs MD sides.
- **Backward compatibility is tested**: `TestBuildLabelMapBackwardCompat` confirms the old single-dir API still works correctly with the new `LabelTarget` type.
- **All 515 unit tests pass** with no regressions.

## Files Reviewed

- `tools/rbkc/tests/ut/test_docs.py` (test)
- `tools/rbkc/tests/ut/test_labels_doc_map.py` (test)
- `tools/rbkc/tests/ut/test_rst_ast_visitor.py` (test)
- `tools/rbkc/tests/ut/test_verify.py` (test)

---

# Expert Review: QA Engineer (Task 27)

**Date**: 2026-05-14
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 1 file (test_labels_doc_map.py)

## Summary

1 Finding fixed (branch 8 coverage added during review)

## Findings

1. **Branch 8 of `_entry_parent_xparen_title` had no test coverage** (fixed)
   - Violated clause: `.claude/rules/development.md` — "Bug-revealing cases: Input that exercises each specific failure mode"
   - X) paragraph present but no preceding target was not tested
   - Fix: Added `test_entry_parent_label_xparen_without_target_falls_back_to_enclosing_section`

## Observations

- `idx < 2` guard (fewer than 2 preceding siblings) untested in isolation — behaviorally equivalent to other None-returning branches.

## Positive Aspects

- Test 1 modeled on real production RST structure from 04_ObjectSave.rst.
- Both fields (`title` and `section_title`) verified in positive test.
- Meaningful failure messages in all assertions.
