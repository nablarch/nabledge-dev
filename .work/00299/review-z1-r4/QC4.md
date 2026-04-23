# QA Review: QC4 配置正確性 (Round 4, independent)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance: spec is authoritative; v6 PASS + narrow-green tests are weak evidence on their own)
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 (削除手順 → 手順 2) + §2-3 セクション順序保存契約

## Summary

QC4 implementation is spec-conformant on both RST and MD paths, with clean QC2/QC3/QC4 three-way classification, non-advancement on FAIL, and independent QC1 residue separation. Round 3 flagged five test-coverage gaps; **three were filled in r4** (MD title-swap already present in r2, MD content-only swap added, 3-section middle-swap added, QC3/QC4-duplicate positive guard added). **Two remain open**: (a) top-level-content misplacement is still untested, and (b) existing QC4 asserts do not exclude spurious QC1/QC2/QC3 cross-class false positives. The spec-critical QC3-vs-QC4 discriminator (`_in_consumed`) is still covered only by cases where `prev_idx` is outside `consumed` — the symmetric "prev_idx inside consumed → must be QC3, not QC4" is not directly locked by a dedicated test.

**Rating**: 4/5 — spec-conformant, runtime-green, coverage clearly improved since r3, but two targeted gaps still block the ゼロトレランス bar for marking QC4 ✅.

## Condition 1: Implementation vs. spec

Spec §3-1 手順 2: *"JSON 順 i 番目要素の削除位置が、i-1 番目の削除位置よりも前であれば FAIL (QC4)"*. Classification between QC2/QC3/QC4 relies on `prev_idx` (from-start `find`) and whether that earlier position lies inside a previously consumed range.

### RST path — `_check_rst_content_completeness`

`tools/rbkc/scripts/verify/verify.py:529-608`.

- Forward scan: `idx = norm_source.find(norm_unit, current_pos)` (`verify.py:570`). On hit, append to `consumed`, advance `current_pos` (`verify.py:571-573`).
- On miss, `prev_idx = norm_source.find(norm_unit)` from start (`verify.py:575`). Branch:
  - `prev_idx == -1` → `[QC2]` fabricated (`verify.py:577-578, 583-584`).
  - `_in_consumed(prev_idx, len)` → `[QC3]` duplicate (`verify.py:579-580, 585-586`).
  - Otherwise → `[QC4]` misplaced (`verify.py:581-582, 587-588`).
- Non-advancement on FAIL: no `consumed.append` and no `current_pos` update in the else-branch. Spec-consistent.
- QC1 residue (`verify.py:595-606`) is an independent from-scratch delete, so a QC4-detected unit is still consumed during residue computation — misplacement does not leak into QC1 as a spurious false positive.

### MD path — `_check_md_content_completeness`

`tools/rbkc/scripts/verify/verify.py:611-703`. Same three-way branch (`verify.py:664-683`); structurally identical to RST path. Residue pass (`verify.py:686-703`) is similarly independent.

### §2-3 contract

Section-order preservation is a stated RBKC contract; verify consumes it by deriving the "expected position" from JSON order (the forward scan itself). Not a separately-coded check — correct.

**Verdict**: Implementation is spec-conformant on both formats, with clean separation between QC1 residue and QC4 ordering. No defects found.

## Condition 2: Unit tests

QC4-related FAIL/boundary inventory (grep `QC4\|three_section\|content_swap\|boundary`):

| # | Test | Fmt | Kind | Location |
|---|------|-----|------|----------|
| 1 | `test_fail_qc4_misplaced_title` | RST | 2-section title swap | `tests/ut/test_verify.py:850` |
| 2 | `test_fail_qc4_misplaced_title_md` | MD | 2-section title swap | `tests/ut/test_verify.py:1123` |
| 3 | `test_fail_qc4_three_section_middle_swap` | RST | 3-section middle swap (cascade) | `tests/ut/test_verify.py:1132` |
| 4 | `test_fail_qc4_md_content_swap` | MD | 2-section content swap | `tests/ut/test_verify.py:1144` |
| 5 | `test_fail_qc3_qc4_boundary_duplicate_text_misplaced` | RST | duplicate-source positive guard | `tests/ut/test_verify.py:1154` |
| 6 | `test_fail_qc4_misplaced_content_rst` | RST | 2-section content swap | `tests/ut/test_verify.py:1170` |

### Coverage checklist

| Case | Status | Evidence |
|------|--------|----------|
| RST title swap | Covered | test 1 |
| MD title swap | Covered | test 2 |
| RST content swap | Covered | test 6 |
| MD content-only swap | Covered (r4 gap-fill) | test 4 |
| 3-section middle-swap (cascade after QC4 non-advancement) | Covered (r4 gap-fill) | test 3 |
| QC3/QC4 boundary: duplicate source text, single consumption (positive guard) | Partially covered | test 5 |
| **QC3/QC4 boundary: both branches locked (prev_idx in consumed ⇒ QC3; not in consumed ⇒ QC4, using the same duplicated text)** | **Missing** | — |
| **Top-level (`__top__`) content misplaced into section region (or vice versa)** | **Missing** | — |
| **Cross-class exclusion on QC4 inputs (no spurious QC1/QC2/QC3)** | **Missing** | no negative assertions in tests 1–4, 6 |

### Assessment of `test_fail_qc3_qc4_boundary_duplicate_text_misplaced` (test 5)

The test name promises a QC3/QC4 boundary assertion, but the body only has a single JSON section consuming the first "note"; no second JSON unit drives the discriminator. The assertion `not any("QC3" in i for i in issues)` is a *positive guard* against spurious QC3 on duplicate source text, not a boundary test between QC3 and QC4. The spec-critical branch at `verify.py:579-582` / `674-677` — where the same text in two source positions must resolve to QC3 when prev occurrence is in `consumed` vs. QC4 when it is not — is **still not directly exercised**. A refactor inverting `_in_consumed` could leave tests 1–6 green while mis-classifying every real production QC3/QC4.

### Circular-test check

- All six tests drive real `check_content_completeness` against hand-crafted RST/MD source + JSON — no mocking of sequential-delete, no asserting on internal state.
- Assertions use `any("QC4" in i for i in issues)`, which reflects the spec's output contract, not the implementation.
- **Not circular.** However, asserts are coarse: only issue-class membership is pinned. None of tests 1–4, 6 assert the absence of QC1/QC2/QC3 on the same input. A bug that emits QC4 *plus* a spurious QC2 would still go green.

## Condition 3: v6 runtime + pytest

- `cd tools/rbkc && python -m pytest tests/ut/test_verify.py -q` → **148 passed in 0.93s**.
- `cd tools/rbkc && python -m scripts.run verify 6` → **All files verified OK** (0 FAIL).

Both green.

## Issues and proposed fixes

### [Medium] QC3/QC4 discriminator boundary not locked by a test

- **Description**: The `_in_consumed(prev_idx, len)` branch at `verify.py:579-580` (RST) and `verify.py:674-675` (MD) is what separates QC3 from QC4. Current tests never have a scenario where the *same* text token, duplicated in source, drives the two branches in a single test pair. Inverting `_in_consumed` would still pass tests 1–6.
- **Proposed fix**: Add two paired tests:
  - `test_fail_qc4_duplicate_text_second_position_not_consumed`: source `"X\n=\n\nnote\n\nY\n=\n\nnote\n"`, JSON `[{X,""}, {Y, "note"}, {Z, "note"}]` where `Z` is absent from source or positioned before `Y` — so the third unit must find the second "note" but its from-start find (first "note") is *not* in consumed range → QC4.
  - `test_fail_qc3_duplicate_text_second_position_already_consumed`: construct so the second JSON unit's `prev_idx` lands inside `consumed` → QC3. Keeps both branches locked in one commit.

### [Medium] Cross-class exclusion absent on QC4 tests

- **Description**: `test_fail_qc4_misplaced_title`, `..._title_md`, `..._three_section_middle_swap`, `..._md_content_swap`, `..._misplaced_content_rst` all use `any("QC4" in i for i in issues)`. None excludes spurious QC1/QC2/QC3 on the same input.
- **Proposed fix**: Append `assert not any(tag in i for tag in ("[QC1]", "[QC2]", "[QC3]") for i in issues)` (or a targeted pin to exactly 1 QC4 issue) to each of tests 1–4 and 6. The 3-section middle-swap test in particular should pin the QC4 count, because a bug in `current_pos` advancement could produce multiple FAILs.

### [Low] Top-level (`__top__`) misplacement untested

- **Description**: `_build_rst_search_units` and the MD equivalent place `__top__` title and content first in the scan order (`verify.py:487-492`, `639-643`). No test verifies QC4 fires when a source places the to-be-top content after the first section (or vice versa).
- **Proposed fix**: Construct a source where the substring matching `top_content` appears near the bottom of the source; JSON declares it as `data["content"]` → the first forward scan lookup for top-content should find it early or not at all, depending on ordering, exercising QC4 on `__top__`.

## Positive aspects

- Three-way QC2/QC3/QC4 classification is structurally identical on RST and MD paths — low drift risk.
- QC4 detection (forward scan) is independent from QC1 residue (from-scratch delete) — misplacement cannot leak into QC1 false positives.
- Non-advancement on FAIL is implemented and now exercised via the 3-section cascade test (r4 improvement vs. r3).
- MD content-swap test (r4 addition) closes the earlier RST-only asymmetry on content mis-placement.
- Tests are non-circular; they exercise the full normalise + delete path end-to-end.
- v6 verify 0 FAIL; 148/148 unit tests green.

## Verdict

- **Implementation**: Spec-conformant on RST and MD.
- **Tests**: Improved from r3 (3-section cascade, MD content swap added), but the QC3/QC4 discriminator boundary is still not locked by a dedicated test pair, top-level misplacement is still untested, and no QC4 test excludes cross-class false positives.
- **v6 runtime**: Green.

Under ゼロトレランス, v6 PASS + 6 green FAIL tests is necessary but not sufficient for ✅. Adding the paired QC3/QC4 discriminator tests and the cross-class exclusion asserts would directly eliminate the "silent refactor regression" class of defects. Top-level misplacement is lower priority (single code path), but still a real gap. Recommend holding QC4 at ⚠️ on the maturity matrix until at least the Medium-priority items are addressed.
