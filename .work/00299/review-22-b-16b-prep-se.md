# Expert Review: Software Engineer — Phase 22-B-16b-prep

**Date**: 2026-04-23
**Reviewer**: AI Agent as Software Engineer
**Files Reviewed**: 4 files

- `tools/rbkc/scripts/common/file_id.py` (new)
- `tools/rbkc/scripts/create/classify.py` (modified — delegates to common)
- `tools/rbkc/scripts/create/scan.py` (modified — delegates to common)
- `tools/rbkc/tests/ut/test_file_id.py` (new — 15 tests)

## Summary

1 Finding — not shippable

## Findings

Each Finding quotes the specific spec / rule / standard clause it violates.
All Findings are non-negotiable fix items under ゼロトレランス.

### 1. `test_longer_pattern_wins_over_shorter` does not actually test "longer pattern wins"

- **Violated clause**: `.claude/rules/development.md` §"Test Writing: Required Coverage" —
  > "Bug-revealing cases: Input that exercises each specific failure mode (wrong output, missed detection, false alarm). If a bug can occur, write a test that catches it."

  Also `.claude/rules/rbkc.md` §"Test coverage policy" — verify-side oracle must be derivable from spec, not tautological.

- **Description**: The test at `tests/ut/test_file_id.py:42-53` claims to verify the "longest pattern wins" rule. It picks path
  `.../batch/nablarch_batch/overview.rst` and asserts `fc.category == "nablarch-batch"` and
  `fc.file_id == "nablarch-batch-overview"`.

  The v6 mapping file has three patterns that match this path:
  - `application_framework/application_framework/batch/nablarch_batch` → `processing-pattern / nablarch-batch`
  - `application_framework/application_framework/batch/` → `processing-pattern / nablarch-batch`
  - (not matched: `batch/jsr352`, `batch/jBatchHandler`)

  **Both candidate patterns produce the same `type` and `category`**, and the filename stem `overview` is invariant, so the derived `file_id` is `nablarch-batch-overview` regardless of which pattern wins. Reversing the sort order in `_match_rst` (breaking "longest wins") would not fail this test. The test is tautological and provides zero regression coverage for the longest-pattern-wins rule — which is the only rule the test claims to check.

  Verified empirically:
  ```
  $ python -c "...simulate reversed sort on this input..."
  Shortest-first wins: category=nablarch-batch, type=processing-pattern
  ```
  → identical output to longest-first.

  This matters because Phase 22-B-16b-main will consume `derive_file_id` from verify-side. If a future refactor breaks pattern ordering, the test suite will silently green.

- **Fix**: Replace the input with a path that distinguishes the two rules. Two valid choices in the v6 mapping:

  **Option A** (differing category): use `batch/jsr352/*.rst` — shorter match `batch/` gives `nablarch-batch`, longer match `batch/jsr352` gives `jakarta-batch`. Asserting `fc.category == "jakarta-batch"` proves longer wins.

  **Option B** (differing type): use `batch/jBatchHandler/*.rst` — shorter match `batch/` gives `processing-pattern`, longer match `batch/jBatchHandler` gives `component`. Assert `fc.type == "component"`.

  Either choice makes the test non-tautological. Also add `fc.type` to the assertions (the current test only asserts `category` and `file_id`).

## Observations

Non-blocking notes that do not violate any clause.

- **`format` shadows the Python builtin** at `file_id.py:158` (`def derive_file_id(..., format: str, ...)`). This is consistent with the existing `SourceFile.format` / `FileInfo.format` convention in `scan.py` and `classify.py`, so keeping it is reasonable. If you want to tighten, rename to `fmt` to match `_generate_id`'s parameter name (which uses `fmt`).
- **Typo in the re-export comment** at `test_file_id.py:189`: "create/__init__-ish places" — these aren't `__init__` re-exports, they are `from ... import X as _X` in `scan.py` / `classify.py`. Wording only.
- **`FileClass` vs `FileInfo` naming**: the new type is `FileClass` in `common/file_id.py`, the existing type in `create/classify.py` is `FileInfo`. The two carry overlapping fields (source_path, format, type, category, file_id). Whether to unify in 22-B-16b-main is a design-time call; noting it here only so you don't paint yourself into a corner. `FileInfo` adds `output_path` / `sheet_name` which are output-layer concerns — keeping them separate is defensible under the stated split "naming vs output-path concerns".
- **`_match_rst` re-sorts on every call** (line 145). For verify-side usage the cost is trivial (patterns per version ≤ ~40). If verify-side ends up calling `derive_file_id` in a hot loop, hoist the sort to `load_mappings` as a second key. Not required now.
- **Test fixture paths point to files that do not all physically exist** (e.g. `libraries/universal_dao.rst` — the real file is `libraries/database/universal_dao.rst`; xlsx test uses `v6/Nablarch機能のセキュリティ対応表.xlsx` but the real file is under `Sample_Project/設計書/`). This is fine because `derive_file_id` is purely string-based and never touches the filesystem. Flagging it only so nobody later "fixes" the paths under the mistaken belief they must be real — if the tests were ever rewritten to read the file, they would break.

## Positive Aspects

- **Clean separation of concerns**: `common/file_id.py` holds the naming spec (pure transformation of mapping rules), while `create/classify.py` keeps the output-layer concerns (xlsx sheet expansion, collision disambiguation). This is exactly the right boundary for 22-B-16b-main to consume from verify.
- **Re-exports via `import X as _X`** in `scan.py` / `classify.py` preserve the existing internal import surface with zero call-site changes beyond the two moved modules. Good minimization of blast radius.
- **`@dataclass(frozen=True)`** on `FileClass` — immutability is right for a value type shared across create/verify.
- **Defensive re-sort in `_match_rst`** — `derive_file_id` is correct regardless of input mapping order, which is the right contract for a shared API.
- **MD5 bit-identity verified** on the full v6 output (`5c652df3469c222be03dacad4b65727e`) plus `verify 6` FAIL=0 plus 325/325 unit tests green. Behavioral invariance is empirically confirmed.
- **Spec-aligned placement**: `rbkc-converter-design.md` §1 explicitly endorses `scripts/common/` as the shared layer for create/verify common code ("両者とも `scripts/common/` 配下の共通モジュール経由で公式パーサを呼び"). The refactor follows that rule.
- **Docstring on `_generate_id`** explicitly states what the function does NOT do (no filesystem, no collision resolution). This is the right level of documentation for a function that will be called from two sides.
- **No silent skips introduced** — `derive_file_id` returns `None` explicitly; `classify_sources` continues its existing skip-on-None behaviour unchanged.

## Files Reviewed

- `tools/rbkc/scripts/common/file_id.py` (new — source code)
- `tools/rbkc/scripts/create/classify.py` (modified — source code)
- `tools/rbkc/scripts/create/scan.py` (modified — source code)
- `tools/rbkc/tests/ut/test_file_id.py` (new — tests)
