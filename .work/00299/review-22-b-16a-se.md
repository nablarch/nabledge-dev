# Expert Review: Software Engineer — Phase 22-B-16a (a469b0c8b)

**Date**: 2026-04-23
**Reviewer**: AI Agent as Software Engineer (bias-avoidance subagent)
**Target**: Phase 22-B-16a implementation

## Summary

**0 Findings**

## Findings

None. The implementation conforms to `rbkc-json-schema-design.md §2-2`,
`rbkc-verify-quality-design.md §3-3 QO1`, and §3-2-2 zero-exception as cited
in the commit.

## Observations

1. **Function-scope `UNRESOLVED` imports** — `verify.py` and
   `rst_ast_visitor.py` import `UNRESOLVED` inside function bodies. No
   circular-import risk. Non-blocking.
2. **Extra-heading detection limited to H2** — `verify.py` only flags orphan
   docs-MD H2 titles. If RBKC emits a stray `###`/`####` not in JSON, QO1
   would not catch it. JSON→docs direction fully covered by missing/level
   loop. Worth considering for a future pass.
3. **Sentinel string robustness** — `"__RBKC_UNRESOLVED_LABEL__"` is
   collision-free. A dataclass sentinel would be type-safer for 22-B-16b.
4. **Test class organisation** — 22-B-16a additions are spread across three
   locations; a shared banner would aid future readers.

## Positive Aspects

- Promoted-section level propagation correct (verified: subsections of a
  promoted top section walked with level=2)
- Duplicate-title level matching via `used_idx` works correctly (verified
  two "概要" at levels 2/3)
- Fenced code blocks correctly excluded before heading scan
- Silent-skip horizontal class addressed at the three genuine sites
- xlsx level omission is spec-correct (P1 exception in §3-3)
- 293 unit tests + v6 verify FAIL 0 (353 files) confirms TDD GREEN step

## Files Reviewed

- `tools/rbkc/scripts/common/labels.py`
- `tools/rbkc/scripts/common/rst_ast_visitor.py`
- `tools/rbkc/scripts/common/md_ast_visitor.py`
- `tools/rbkc/scripts/create/docs.py`
- `tools/rbkc/scripts/run.py`
- `tools/rbkc/scripts/verify/verify.py`
- `tools/rbkc/tests/ut/test_verify.py`
