# Expert Review: QA Engineer — Task 25

**Date**: 2026-05-13
**Reviewer**: AI Agent as QA Engineer
**Files Reviewed**: 4 files (labels.py, rst_ast_visitor.py, test_labels_doc_map.py, test_rst_ast_visitor.py)

## Summary

0 Findings (2 Findings fixed before save)

## Findings

### Finding 1 (Fixed): Docstring contradicts implementation for plain-text case

Same as SE Finding 1 — fixed in labels.py and test_labels_doc_map.py.

### Finding 2 (Fixed): Missing h1-scope suppression test

**Violated clause**: `.claude/rules/development.md` — "Every test class must include: Bug-revealing cases: Input that exercises each specific failure mode."

The guard at `labels.py` lines 377–388 suppresses `para_title` for `in_h1_scope=True`. Without a test, removing this guard would pass all existing tests. Added `test_h1_scope_bold_paragraph_falls_back_to_h1` to `TestParagraphAnchorTitleResolution` asserting `v.section_title == ""` for h1-scoped bold-paragraph anchor.

## Observations

- `TestParagraphAnchorSyntheticSection` covers bold-only and bold-start at visitor level but not italic-only. Italic is covered at labels layer (`TestParagraphAnchorTitleResolution`). Not a clause violation.
- `_is_skippable` inline duplication between `_next_section_for_node` and `_paragraph_anchor_title`. Minor DRY deviation, no clause violation.

## Positive Aspects

- All 9 new tests (including added h1-scope test) pass; 544 total tests pass
- Tests use descriptive docstrings citing real-world RST examples
- Negative case (`test_plain_paragraph_anchor_does_not_create_subsection`) correctly validates exclusion
- `_walk_section` boundary detection correctly handles skippable nodes between target and paragraph

## Files Reviewed

- `tools/rbkc/scripts/common/labels.py` (source code)
- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source code)
- `tools/rbkc/tests/ut/test_labels_doc_map.py` (tests)
- `tools/rbkc/tests/ut/test_rst_ast_visitor.py` (tests)
