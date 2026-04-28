# Post-mortem: Handler Docs Raw HTML in nabledge-1.x

**Related Issue**: #312
**Date**: 2026-04-28
**Severity**: High

## Incident Summary

nabledge-1.x handler knowledge files omitted the ハンドラ処理概要 (handler processing overview) table entirely, and rendered invisible spacer images as Markdown image tags at the top of docs. Affected all v1.2/v1.3/v1.4 handler docs (49–55 files per version). v5 and v6 were unaffected because they use a different doc structure with no `:file:` + `.. raw:: html` combination.

## Timeline

**2026-04-25** — Issue #312 opened; `visit_raw` identified as the conversion entry point.  
**2026-04-25** — Prototype: 3-block state machine implemented for `visit_raw`; `handler_js.py` added.  
**2026-04-25** — Prototype review found 3 bugs (invisible images, empty table, duplicate heading) + design extension (class/type columns).  
**2026-04-25** — Bug 1/2/3 and extension implemented; prototype re-run confirmed fixes.  
**2026-04-25** — verify run found 132 false-positive QL1 FAILs for v1.4 (invisible image not excluded in verify).  
**2026-04-28** — verify.py fixed (TDD); all 5 versions verified OK (0 FAILs).

## Root Cause Analysis

### Immediate Cause

Three independent defects combined to make handler docs incorrect:

1. **Bug 1 — Invisible images rendered**: `visit_image` in the converter lacked a `:height: 0` / `:width: 0` guard. `link.rst` (included by every handler RST) injects `handler_structure_bg.png` / `handler_bg.png` as CSS-loaded invisible spacers with these dimensions. The converter emitted them as Markdown `![...]()` tags at the top of every handler doc.

2. **Bug 2 — Handler table empty**: The Block 3 detection in `visit_raw` used `node.source` to match the `:file:` path. But `node.source` holds the RST file path, not the `:file:` attribute value — so Block 3 was never detected and the table JS was never processed.

3. **Bug 3 — Leading blank lines**: `docs.py` emits `""` as the first line when `title` is empty. Before Bug 1 was fixed, the invisible image MD occupied that position and masked the blank. After Bug 1 fix the leading blank was exposed.

4. **verify false positives**: `verify.py` QL1 image check lacked the same `height=0`/`width=0` skip that the converter had, causing 132 false-positive FAILs after the RBKC fix.

### Contributing Factors

- The 3-block structure in handler RST files (`raw::html` + `:file:` reference) is unique to v1.x; v5/v6 use a different doc structure with no such pattern. This meant the bugs went undetected during v5/v6 development.
- No existing unit test covered the `:file:`-based Block 3 detection path.

### Systemic Issues

- `verify.py` image skip logic was not kept in sync with `rst_ast_visitor.py` visit_image skip logic. Both make the same suppression decision but were implemented independently.

## Resolution

### Approach Chosen

TDD for each fix: write a failing test, then implement the minimum fix to make it pass.

### Changes Made

- `rst_ast_visitor.py:visit_image` — added `height=0` / `width=0` guard (Bug 1)
- `rst_ast_visitor.py:visit_raw` — changed Block 3 detection from `node.source` match to "first raw node after Block 2" positional logic (Bug 2)  
- `docs.py` — suppressed leading empty line when title is empty (Bug 3)
- `verify.py` — added matching `height=0` / `width=0` skip to QL1 image check (verify false positive)
- `handler_js.py` — new module to parse `Handler.js` for class name, package, argument/return types
- `rbkc-verify-quality-design.md` §346 — added exclusion condition note for invisible images

### Why This Approach

The positional Block 3 detection (after Block 2) is more robust than source-path matching because the RST node tree does not carry `:file:` attribute values through docutils.

### Alternatives Considered

1. **Parse `:file:` from raw HTML text**: Would require fragile regex on raw HTML content. Rejected — positional logic is simpler and equally correct given the fixed 3-block structure.

## Horizontal Check

**Method**: Searched for `.. raw:: html` + `:file:` in all 5 versions of official Nablarch docs.  
**Checked**: All `.rst` files under `.lw/nab-official/` for both directives.

**Key Findings**:
- v1.2: 49 files with `:file:` + `.. raw:: html` ✅ (all now fixed)
- v1.3: 50 files with `:file:` + `.. raw:: html` ✅ (all now fixed)
- v1.4: 55 files with `:file:` + `.. raw:: html` ✅ (all now fixed)
- v5: 0 files with this combination ✅ (no exposure)
- v6: 0 files with this combination ✅ (no exposure)

The bug was structurally confined to v1.x handler docs.

## Prevention Measures

1. **verify sync rule** — When `visit_image` suppression logic changes, the same condition must be mirrored in `verify.py` QL1 image check. Added comment cross-referencing both locations.
2. **Unit test coverage** — 2 new tests for invisible image skip in verify; existing tests for converter visit_image cover the RBKC side.
3. **Post-mortem** — This document.

## Lessons Learned

### What Went Well

- TDD approach caught the verify false-positive as a distinct problem, not a spec relaxation.
- Horizontal check confirmed the bug was v1.x-only before declaring done.

### What Could Improve

- `verify.py` and `rst_ast_visitor.py` image suppression logic should be co-located or share a helper to prevent drift.

### Technical Insights

- docutils `node.source` on a `raw` node returns the RST file path, not directive attributes. Positional detection (relative to sibling nodes) is the correct approach for this 3-block pattern.
- `link.rst` invisible spacer images are a CSS background-image loading trick; they carry no content and must be excluded everywhere content is extracted or verified.

### Process Improvements

- When fixing a converter bug that suppresses output, immediately check whether verify has a corresponding check that would false-positive on the same suppressed output.
