# QO3 Review: docs MD 存在確認 (1:1 file existence)

**Reviewer**: QA Engineer
**Scope**: RST / MD / Excel
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-3 — "JSON に対応する docs MD が存在しない"

---

## 1. 実装の有無 ✅

- Location: `tools/rbkc/scripts/verify/verify.py:110-148` `check_docs_coverage(knowledge_dir, docs_dir)`
- Walks JSON: `verify.py:130` `for json_path in sorted(kdir.rglob("*.json")):`
- Computes expected MD path (1:1, `.json` → `.md`, preserves relative directory): `verify.py:131-132`
- Emits `[QO3] docs MD missing for JSON: expected {rel} ...` when MD file absent: `verify.py:133-136`
- README existence precondition: `verify.py:124-127`
- README page-count coherence supplement (not the authoritative QO3 check): `verify.py:138-147`

Verdict: ✅ Implementation exists and aligns with the §3-3 spec (per-file 1:1 existence check).

## 2. ユニットテストのカバレッジ

Location: `tools/rbkc/tests/ut/test_verify.py:198-248` `TestCheckDocsCoverage`.

| Required case | Covered? | Test |
|---|---|---|
| JSON with matching docs MD → PASS | ✅ | `test_pass_each_json_has_docs_md` (line 217) |
| JSON without matching docs MD → FAIL (QO3) | ✅ | `test_fail_json_without_matching_docs_md` (line 226) |
| no_knowledge JSON still requires docs MD | ✅ | `test_pass_no_knowledge_json_still_requires_docs_md` (line 235) |
| README missing → FAIL | ✅ | `test_fail_readme_missing` (line 244) |
| Nested directory (category-level preservation) | ⚠️ Partial | `test_pass_each_json_has_docs_md` uses `about/nablarch/a.json` (2 levels), but there is no negative test asserting that `a.md` at the wrong (flat) location FAILs — the 1:1 relative-path requirement is only implicitly tested |
| File name with CJK | ❌ Missing | no test uses Japanese/CJK filenames; encoding/Path handling untested |
| Empty knowledge dir | ❌ Missing | no test for `kdir` with zero JSON files (the loop simply yields no issues — a dedicated test would pin down behavior) |

Additional untested behaviors:
- README page-count mismatch FAIL (`verify.py:146`) has no unit test.
- Format scope (RST / MD / Excel): since the check is format-agnostic (walks `*.json`), format-specific tests are not required — ✅.

Verdict: ⚠️ Core spec coverage is adequate, but edge cases (nested-dir mismatch, CJK names, empty dir, README count mismatch) are not exercised. Given Nabledge's zero-tolerance standard, these gaps are a concern.

## 3. v6 verify 実行結果 ✅

Commands run from `/home/tie303177/work/nabledge/work2/tools/rbkc`:

```
$ bash rbkc.sh verify 6 2>&1 | grep -c "^FAIL"
0

$ bash rbkc.sh verify 6 2>&1 | tail -3
All files verified OK

$ python3 -m pytest tests/ 2>&1 | tail -3
tests/ut/test_xlsx_converters.py ......                                  [100%]
============================= 138 passed in 4.09s ==============================

$ python3 -m pytest tests/ut/test_verify.py::TestCheckDocsCoverage -v
4 passed
```

Verdict: ✅ v6 verify 0 FAIL and all 138 unit tests pass.

## 4. 総合判定: ⚠️ Pass with recommended improvements

- Implementation: ✅ correct and spec-aligned.
- Test coverage: ⚠️ happy/sad path covered for the 4 required cases; edge cases underspecified.
- Runtime: ✅ verify clean, tests green.

Given the zero-tolerance standard, the edge-case gaps should be closed before this is considered final.

## 5. 改善案 (proposed fixes)

**[Medium] Missing test: nested-dir path preservation negative case**
- Description: When `a.json` lives at `cat/sub/a.json` but `a.md` exists only at top-level `a.md`, QO3 must FAIL. Current suite does not assert this.
- Proposed fix: add `test_fail_md_at_wrong_relative_path` — write `kdir/cat/sub/a.json` and `ddir/a.md`, assert QO3 issue emitted.

**[Medium] Missing test: CJK filename**
- Description: Nablarch docs contain Japanese identifiers; Path encoding bugs would silently bypass QO3 for CJK filenames.
- Proposed fix: add `test_pass_cjk_filename` and `test_fail_cjk_filename_missing_md` using e.g. `概要.json` / `概要.md`.

**[Low] Missing test: empty knowledge dir**
- Description: Pin behavior when `kdir` has no JSON (should pass silently provided README exists).
- Proposed fix: add `test_pass_empty_knowledge_dir`.

**[Low] Missing test: README page-count mismatch**
- Description: `verify.py:143-147` emits `[QO3] README.md count mismatch` but no unit test locks the contract.
- Proposed fix: add `test_fail_readme_count_mismatch` — write 2 MDs but `0ページ` in README, assert QO3 emitted.

**[Low] Consider per-check IDs**
- Description: Both the 1:1 check and the README count check share the `[QO3]` tag. Tag the README count check as e.g. `[QO3-count]` for faster triage. (Out of scope if the design spec mandates a single ID.)
