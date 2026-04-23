# Expert Review: QA Engineer — Phase 22-B-16a (a469b0c8b)

**Date**: 2026-04-23
**Reviewer**: AI Agent as QA Engineer (bias-avoidance subagent)
**Target**: Phase 22-B-16a test coverage + horizontal class completeness

## Summary

**2 Findings — not shippable.** (All addressed in fix commit 7841dd5cb.)

## Findings

### F1 — UNRESOLVED sentinel bleeds through `inline_reference` (refname path) and `_resolve_title_inline`

- **Violated clause** (`.claude/rules/review-feedback.md` §Horizontal check):
  *"Fix the whole class in one pass — the flagged instance + every
  horizontal match. Do not defer horizontal matches to 'next time'."*
  Also `rbkc-verify-quality-design.md` §3-2-2 zero-exception:
  *"silent に text を返す fallback は禁止"*.
- **Description**: `labels.py` returns `UNRESOLVED = "__RBKC_UNRESOLVED_LABEL__"`
  (truthy non-empty str) for orphan labels. The 22-B-16a fix updated three
  consumers but missed two:
  1. `rst_ast_visitor.inline_reference` (refname path): `if resolved:`
     accepted the sentinel string as truthy.
  2. `verify._resolve_title_inline`: `label_map.get(raw, raw)` returned
     the sentinel verbatim. Same at refid branch.
- **Fix** (applied in 7841dd5cb): treat `UNRESOLVED` as `None` at every
  `label_map.get()` call. inline_reference raises
  UnresolvedReferenceError; _resolve_title_inline falls back to raw.
  2 regression-guard tests added.

### F2 — `TestLabelMapStrict` is a single-case test, not a class

- **Violated clause** (`.claude/rules/development.md` §Test Writing: Required
  Coverage): *"A test suite that only covers the happy path is incomplete."*
- **Description**: Missing edges — orphan at EOF, stacked orphans, stacked
  mixed resolved+orphan, directive after label, overline-only without title.
- **Fix** (applied in 7841dd5cb): Added 4 parameterised edge cases covering
  EOF-orphan / stacked orphans / mixed resolved+new orphan / explicit
  UNRESOLVED assertion. Plus 2 regression guards for F1.

## Observations

- `_HEADING_RE = r'^(#{2,6})\s+(.+)$'` handles level 5/6 gracefully
- Duplicate-title-at-different-levels handling correct via `used_idx`
- `no_knowledge_content: true` short-circuits before level check
- Spot-check of auto-inserted `level: 2`: no accidental rewrites

## Positive Aspects

- All six QO1 level cases (16–21) from prior QA review present, each
  asserting against hand-authored docs MD (no circular pinning of docs.py)
- `test_fail_rst_ref_unknown_label_is_dangling` is clean inversion with
  spec clause quoted in docstring
- `labels.UNRESOLVED` documented with spec citation, non-ambiguous sentinel

## Files Reviewed

- `tools/rbkc/tests/ut/test_verify.py`
- `tools/rbkc/scripts/verify/verify.py`
- `tools/rbkc/scripts/common/labels.py`
- `tools/rbkc/scripts/common/rst_ast_visitor.py`
