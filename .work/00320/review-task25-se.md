# Expert Review: Software Engineer — Task 25

**Date**: 2026-05-13
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 4 files (labels.py, rst_ast_visitor.py, test_labels_doc_map.py, test_rst_ast_visitor.py)

## Summary

0 Findings (1 Finding fixed before save)

## Findings

### Finding 1 (Fixed): Docstring contradicts implementation for plain-text case

**Violated clause**: ゼロトレランス quality standard — quality is binary: correct or not correct

`_paragraph_anchor_title` docstring stated `- plain text: no inline markup → full paragraph text`
but implementation returned `None` for plain text. Same mismatch in `TestParagraphAnchorTitleResolution` class docstring.

**Fix applied**: Updated `_paragraph_anchor_title` docstring to:
```
- plain text (no inline markup) → ``None`` (caller falls back to enclosing section;
  only explicit bold/italic markup signals intentional heading use)
```
Updated test class docstring entry from `→ plain text (plain)` to `→ enclosing section (excluded — ...)`.

## Observations

- **O1** (Fixed as part of review): Multi-level climb in `_next_section_for_node` (lines 219, 228) only checked `isinstance(sib, _nodes.target)` for climb continuation, not the full `_is_skippable` set. Extended to use `_is_skippable` for symmetry with direct-sibling scan.
- **O2**: `_is_skippable` closure is defined inside `_next_section_for_node` but also reimplemented inline in `_paragraph_anchor_title`. Minor DRY deviation, no clause violation.
- **O3**: Cross-module private-symbol import (`from .labels import _paragraph_anchor_title`). Sanctioned by Non-Negotiable Constraints.
- **O4**: Synthetic sections emitted after RST subsections in `parts.sections`. Order-independent for verify's set-based title lookup.

## Positive Aspects

- `_is_skippable` helper extraction is clean and now applied consistently across all 4 call sites
- h1-scope guard in `para_title` computation is precisely specified with correct rationale
- `_walk_section` correctly handles "target followed by skippable nodes then paragraph" pattern
- Test structure for `TestParagraphAnchorSyntheticSection` uses 3-level RST hierarchy to avoid DocTitle promotion collapsing h2 body

## Files Reviewed

- `tools/rbkc/scripts/common/labels.py` (source code)
- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source code)
- `tools/rbkc/tests/ut/test_labels_doc_map.py` (tests)
- `tools/rbkc/tests/ut/test_rst_ast_visitor.py` (tests)
