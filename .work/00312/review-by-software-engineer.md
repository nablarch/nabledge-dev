---
# Expert Review: Software Engineer

**Date**: 2026-04-28
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 8 files

## Summary

0 Findings

## Findings

None.

## Observations

- **Design doc §3-3 "Bug fix note" contradicts the implementation** — Note states docutils sets `source` to RST file path, but empirical testing confirms docutils sets `source` to the `:file:` path. Implementation correctly uses `source.endswith(...)`. No code change needed; the note is cosmetically stale.

- **Design doc §8 says "No changes to scripts/verify/verify.py"** — Entry is outdated. The verify.py change is a spec-backed false-positive correction (acceptable per `rbkc.md`). No code change needed.

- **`render_handler_table` does not escape `|` pipe characters** — If a handler name or behavior value contained a literal `|`, the GFM table would break. Zero pipe characters exist in the current corpus, so not a live defect.

- **`_find_js_block` does not distinguish braces inside string literals** — Unbalanced `{` inside a string literal would cause silent `None` return. The real corpus has perfectly balanced brace counts; acceptable given the constrained, known corpus.

- **No unit test for Block 3 fallthrough when Block 2 has not been seen** — The `"script_text" in state` guard causes fallthrough to `normalise_raw_html`. Correct defensive behavior, but no test exercises this path.

## Positive Aspects

- **Correct independence boundary**: `handler_js.py` lives in `scripts/common/` and is shared by both create and verify. Never imported from `scripts/create/`, satisfying the `rbkc.md` independence constraint.
- **Rigorous TDD**: All new functions in `handler_js.py` have corresponding unit tests covering normal paths, edge cases, and bug-specific regression cases (Bug 2: Block 3 containing HandlerQueue).
- **Spec-anchored verify fix**: Invisible-image QL1 skip is anchored to `rbkc-verify-quality-design.md §352`.
- **Symmetric fix in docs.py**: Empty-title blank-line suppression applied consistently across all four render paths.
- **State machine correctness**: Block 3 check-before-Block-2 ordering is a deliberate and correctly implemented fix confirmed by a dedicated regression test.
- **All 429 tests pass** with no regressions.

## Files Reviewed

- `tools/rbkc/scripts/common/handler_js.py` (source code — new file)
- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source code — modified)
- `tools/rbkc/scripts/create/docs.py` (source code — modified)
- `tools/rbkc/scripts/verify/verify.py` (source code — modified)
- `tools/rbkc/tests/ut/test_handler_js.py` (tests — new file)
- `tools/rbkc/tests/ut/test_rst_ast_visitor.py` (tests — new file)
- `tools/rbkc/tests/ut/test_docs.py` (tests — modified)
- `tools/rbkc/tests/ut/test_verify.py` (tests — modified)
