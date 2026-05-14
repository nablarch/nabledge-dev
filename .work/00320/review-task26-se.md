# Expert Review: Software Engineer — Task 26

**Date**: 2026-05-14
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 4 files

## Summary

1 Finding — fixed before commit

## Findings

1. **`_paragraph_anchor_title` docstring stale and misleading**
   - Violated clause: `.claude/rules/expert-review.md` §Software Engineer review focus — "Maintainability: Documentation" / "Code Quality: Readability"
   - Description: Docstring stated "plain text (no inline markup) → `None` … only explicit bold/italic markup signals intentional heading use" but the new `nodes.Text` branch adds a third recognized plain-text pattern (letter/digit+paren). A reader trusting the docstring would conclude the new branch is dead code.
   - Fix: Updated docstring to list Rule 6 explicitly, replacing the "plain text → None" line with accurate enumeration including the letter/digit+paren case.
   - Status: Fixed in `e95823f2d`

## Observations

- `import re as _re` placement inside loop branch is fine — Python caches imports, consistent with other lazy imports in this file.
- `r'^[a-zA-Z0-9]\) '` scope is correct — bare `e) text` without backslash parses as `enumerated_list`, not `paragraph`, so never reaches this branch.
- No h1-scope test for letter+paren, but guard is in caller (`not in_h1_scope`), existing bold h1-scope test already covers the path.

## Positive Aspects

- Single source of truth maintained: `_walk_section` delegates to `_paragraph_anchor_title` via existing import — Rule 6 implemented in exactly one place.
- False-positive risk is zero by construction: bare `letter)` parses as `enumerated_list`, blocked at `isinstance(sib, _nodes.paragraph)` gate.
- Spec document (§3-2-2 Rule 6) updated in same change.
- All 548 unit tests pass.

## Files Reviewed

- `scripts/common/labels.py` (source code)
- `tests/ut/test_labels_doc_map.py` (test)
- `tests/ut/test_rst_ast_visitor.py` (test)
- `docs/rbkc-verify-quality-design.md` (documentation)
