# QA Review: QC4 配置正確性 (Round 2, independent)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (no prior review access)
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 (削除手順 → 手順 2), §2-3 セクション順序保存前提

## Summary

QC4 is **implemented correctly** per spec in both RST and MD paths, and
v6 verify passes with 0 FAIL (127/127 unit tests green). However, **test
coverage for QC4 is thin** relative to the spec's boundary conditions —
only 3 QC4 FAIL tests exist, with several important cases missing
(notably 3-section middle-swap, top-level misplaced into section, and
the QC3/QC4 boundary where a unit appears in two places and only order
decides which fires).

**Rating**: 3/5 — Works, spec-aligned, but FAIL coverage is the weakest
of any QC check in this suite. For a zero-tolerance quality gate this
is a real gap.

## Condition 1: Implementation vs. spec

Spec §3-1 手順 2 rule: "JSON 順 i 番目要素の削除位置が、i-1 番目の削除位置
よりも前であれば FAIL (QC4)".

### RST path

- `tools/rbkc/scripts/verify/verify.py:671-690` (`_check_rst_content_completeness`)
- For each unit, search from `current_pos` (which is the end offset of
  the previous successful delete). If found → advance. If not found,
  `prev_idx = norm_source.find(norm_unit)` searches from position 0.
  Classification: `prev_idx == -1` → QC2; inside a consumed range →
  QC3; otherwise → QC4 (verify.py:684, 690).
- This exactly matches spec: "削除位置が前に無く、後ろにも無い" → route
  to QC2/QC3 via residue (手順 4); "前にしか見つからない" → QC4.

### MD path

- `tools/rbkc/scripts/verify/verify.py:766-785` (`_check_md_content_completeness`)
- Same pattern, same classification (verify.py:779, 785). No drift
  between the two paths.

### Verdict

Implementation matches spec 手順 2 on both formats. Spec §2-3's section
order preservation is a **precondition** (RBKC contract), not a verify
responsibility — correctly omitted from verify's checks.

Minor notes (not defects):

- When a unit triggers QC4, it is not appended to `consumed` and
  `current_pos` is not advanced (verify.py:683-690, 778-785). Downstream
  units continue searching from the old `current_pos`. This is
  consistent with "do not give credit to a misplaced unit" and allows
  cascading QC4/QC2 detection.
- Residue pass for QC1 (verify.py:697-708) is independent of the
  forward-scan delete. A QC4 unit is still consumed from residue via
  from-scratch `find`, so QC4 does not bleed into QC1 — correct.

## Condition 2: Unit tests in `tests/ut/test_verify.py`

QC4 FAIL cases present:

| # | Test | Path | Kind | Line |
|---|------|------|------|------|
| 1 | `test_fail_qc4_misplaced_title` | RST | 2-section title swap | `tests/ut/test_verify.py:745` |
| 2 | `test_fail_qc4_misplaced_title_md` | MD | 2-section title swap | `tests/ut/test_verify.py:989` |
| 3 | `test_fail_qc4_misplaced_content_rst` | RST | 2-section content swap | `tests/ut/test_verify.py:998` |

**Both RST and MD paths have at least one QC4 FAIL test** — the format
coverage bar is met.

### Coverage against reviewer's checklist

| Case | Status | Evidence |
|------|--------|----------|
| Swapped section titles | Covered (RST + MD) | tests 1, 2 |
| Swapped section contents | Covered (RST only) | test 3 |
| **Swapped section contents (MD)** | **Missing** | — |
| **Top-level misplaced into section** | **Missing** | — |
| **Adjacent sections with similar content (near-collision)** | **Missing** | — |
| **3-section middle-swap** | **Missing** | all tests are 2-section |
| Minimal 2-section pair | Covered | tests 1-3 |
| **QC3/QC4 boundary (same text in two places, only order disambiguates)** | **Missing** | — |

The QC3/QC4 boundary gap is the most important one for a zero-tolerance
gate: the classification of "same string appears twice" depends on
whether the earlier occurrence lies in `consumed` (→ QC3) or not (→
QC4). No test exercises the QC4 side of that branch (`prev_idx` found
but `_in_consumed` is False).

### Circular-test check

All QC4 tests use real `check_content_completeness` with real source
text and crafted JSON. No mocking of the sequential-delete algorithm.
The asserts only require `"QC4" in i` for some issue string — they do
not pin the exact section id or message, but they do require the
correct issue class, which is the spec-level contract. **Not
circular.**

## Condition 3: v6 runtime + pytest

- `cd tools/rbkc && python -m scripts.run verify 6` → `All files verified OK`
  (0 FAIL).
- `pytest tests/ut/test_verify.py -q` → `127 passed in 0.91s`.

Both green.

## Issues and proposed fixes

### [Medium] Missing QC3/QC4 boundary test
- Description: The branch at verify.py:681-684 (RST) and 776-779 (MD)
  routes to QC3 when the earlier occurrence is in a consumed range and
  to QC4 otherwise. No test currently forces the "found but not
  consumed" branch on a unit whose text also appears elsewhere — so a
  regression swapping the two branches would not be caught by tests 1-3
  (which use unique strings).
- Proposed fix: Add a test where the first two sections have distinct
  titles `A` / `B`, a third section's title equals `A` in JSON, and
  source order is `A, B, A'` (with `A'` a distinct section whose title
  also happens to be `A`). Sequential-delete on the mis-ordered JSON
  should fire QC4 (not QC3) for the out-of-order `A`. Confirms branch
  selection.

### [Medium] No 3+-section middle-swap test
- Description: All QC4 FAILs are 2-section swaps. A bug that only
  mis-handles cascading `current_pos` updates after one misplaced unit
  (e.g., erroneously advancing `current_pos` on a QC4) would still pass
  tests 1-3 because there is no "normal unit after a QC4 unit".
- Proposed fix: Add a 3-section test where section 2 is misplaced and
  section 3 is in its correct position, asserting exactly one QC4 and
  no QC1/QC2/QC3.

### [Medium] No MD content-only swap test
- Description: `test_fail_qc4_misplaced_content_rst` exists; MD has
  only the title-swap case. MD's `_squash`/normalisation path is
  different enough from RST's to warrant its own content-swap test.
- Proposed fix: Mirror test 3 as `test_fail_qc4_misplaced_content_md`.

### [Low] Top-level content misplaced into a section not covered
- Description: top-level units (`__top__`) participate in the same
  sequential-delete (verify.py:741-745). No test asserts that a
  top-level content that actually appears late in the source fires
  QC4.
- Proposed fix: Source `section A ... section B ... top line` with
  JSON having `top_content = "top line"` and no sections after the top
  would be mis-ordered — expect QC4.

### [Low] Adjacent similar-content (near-collision) test
- Description: Whitespace-only differences between adjacent section
  contents can mask misplacement. Not currently tested.
- Proposed fix: Two adjacent sections with contents
  `"手順: A を実行する。"` and `"手順: B を実行する。"` swapped in JSON.

## Positive aspects

- Spec-aligned sequential-delete algorithm, identical structure across
  RST and MD paths.
- Clean separation: QC4 detection lives in the forward scan; QC1
  residue uses a separate from-scratch pass, so QC4 and QC1 do not
  cross-contaminate.
- Tests use real (not mocked) normalisation + delete, so they exercise
  the integrated path — no circularity risk.
- v6 verify 0 FAIL + 127/127 unit tests green.

## Verdict

- Implementation: **Spec-conformant** (RST + MD).
- Tests: **Incomplete** for a ゼロトレランス gate. Add the 5 cases
  above before treating QC4 as fully locked in.
- v6 runtime: **Green**.

Weak evidence alone — v6 PASS + 3 tests — should not be read as
sufficient. The missing QC3/QC4 boundary test in particular is the
kind of gap that lets a future refactor silently flip classifications
without any test catching it.
