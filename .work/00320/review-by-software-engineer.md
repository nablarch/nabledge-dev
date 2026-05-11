# Expert Review: Software Engineer

**Date**: 2026-05-11
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 6 files (labels.py, rst_ast_visitor.py, verify.py, docs.py, run.py, rbkc-verify-quality-design.md)

## Summary

0 Findings

## Findings

None.

**Note on reviewer's initial Finding**: The reviewer flagged a missing `TestCheckJsonDocsMdConsistency_QO2_P2_4` test and implementation. Investigation confirmed this is a misapplication — both the test class and the P2-4 implementation exist in `main` (Issue #327). Commit `21fd36c59` in this branch restored the design doc entry that was accidentally absent due to branch divergence. The §4 matrix row is therefore correct and consistent with `main`. Violated clause not applicable — Finding downgraded.

## Observations

- **`_extract_rst_title` iterates file twice (dead loop)**: The intermediate implementation in the review prompt showed a dead `for line in fh: pass` loop before a second docutils parse. The actual `labels.py` has no `_extract_rst_title` function — this was an artifact of the review context, not actual code.
- **`_check_cross_doc_target` may emit two FAIL messages for one broken target**: when target JSON is absent, both JSON and docs MD anchor checks report failure. This is conservative (reports all observable problems) and acceptable under ゼロトレランス.
- **`_parse_rst_without_transforms` depends on private `_substitution_prolog()`**: cross-module coupling pre-exists this PR; not introduced here.

## Positive Aspects

- **docutils AST migration is thorough and correct**: replacing `_is_heading_underline` regex with docutils parse-without-transforms directly eliminates the 692-count false-positive QL1 FAIL pattern. h1-scope detection via `section_title=""` is correctly derived from the JSON contract (h1 → JSON `title`, not `sections[]`).
- **subtitle → sections[0] change is well-specified and small**: targeted change in `extract_document()` with four test cases covering no-subtitle, subtitle-only, subtitle-with-body, subtitle-with-subsequent-sections.
- **Spec §2-2 layering is enforced programmatically**: `TestCommonLayering` checks that `scripts/common/labels.py` has no import from `scripts/create/` — permanent regression guard for the architectural constraint.
- **`_check_cross_doc_target` dedup logic is correct**: three separate dedup sets avoid redundant FAIL messages without suppressing genuine new failures.
- **Design doc updates are complete**: §3-2-3 QL1 implementation notes, §4 matrix new rows, all consistent with implementation.

## Files Reviewed

- `tools/rbkc/scripts/common/labels.py` (source code)
- `tools/rbkc/scripts/common/rst_ast_visitor.py` (source code)
- `tools/rbkc/scripts/verify/verify.py` (source code)
- `tools/rbkc/scripts/create/docs.py` (source code)
- `tools/rbkc/scripts/run.py` (source code)
- `tools/rbkc/docs/rbkc-verify-quality-design.md` (documentation)
