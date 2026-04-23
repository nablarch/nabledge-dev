# QA Review: QC4 配置正確性 (Round 3, independent)

**Date**: 2026-04-23
**Reviewer**: Independent QA Engineer (bias-avoidance: spec authoritative; v6 PASS alone is weak evidence)
**Spec**: `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1 (削除手順 → 手順 2 → QC4) + §2-3 セクション順序保存契約

## Summary

QC4's implementation on both RST and MD paths matches spec 手順 2 and cleanly separates from QC1/QC2/QC3. v6 verify reports 0 FAIL and 134/134 unit tests pass. However, **unit-test coverage for QC4 has not changed since Round 2** — only 3 FAIL cases exist (RST title-swap, MD title-swap, RST content-swap) and the critical QC3/QC4 boundary, 3-section middle-swap, top-level misplacement, and MD content-only swap cases remain uncovered. For a zero-tolerance quality gate this is a real gap: a refactor could silently flip QC3↔QC4 classification without any test catching it.

**Rating**: 3/5 — spec-conformant, runtime-clean, but FAIL-side test coverage is the weakest of the QC checks and has not been strengthened since the r2 review surfaced the gaps.

## Condition 1: Implementation vs. spec

Spec §3-1 手順 2: *"JSON 順 i 番目要素の削除位置が、i-1 番目の削除位置よりも前であれば FAIL (QC4)"*. Routing between QC2/QC3/QC4 is determined by `prev_idx` (from-start find) and whether that earlier position lies inside a consumed range.

### RST path

- `tools/rbkc/scripts/verify/verify.py:719-738` (`_check_rst_content_completeness` forward scan).
- For each `(orig_unit, norm_unit, sid, is_content)`:
  - `idx = norm_source.find(norm_unit, current_pos)` → if found, extend `consumed` and advance `current_pos` (`verify.py:720-723`).
  - Else `prev_idx = norm_source.find(norm_unit)` (from-start). Classification:
    - `prev_idx == -1` → `[QC2]` fabricated (`verify.py:728, 734`)
    - `_in_consumed(prev_idx, len)` → `[QC3]` duplicate (`verify.py:729-730, 735-736`)
    - otherwise → `[QC4]` misplaced (`verify.py:731-732, 737-738`)
- This exactly implements 手順 2 + 手順 4 branching.

### MD path

- `tools/rbkc/scripts/verify/verify.py:814-833` (`_check_md_content_completeness`). Same three-way branch (`verify.py:822-833`). No drift between formats.

### Residue / QC1 interaction

- QC1 residue is computed by an **independent from-scratch delete pass** (`verify.py:745-756` RST; `verify.py:836-849` MD). A QC4 unit that is found earlier in the source will still be consumed by the residue pass, so a misplacement does not leak into QC1 as a false positive. Correct separation.

### Non-advancement on QC4

- When a unit triggers QC4, `consumed` and `current_pos` are intentionally **not** advanced (verify.py:719-738 / 814-833). This is consistent with "do not reward a misplaced unit" and permits cascading QC4 detection on subsequent mis-ordered units.

### §2-3 contract

Section-order preservation is a stated RBKC contract (§2-3), not a verify responsibility. Correctly omitted from verify checks — QC4 derives its "expected position" from JSON order directly.

**Verdict**: Implementation is spec-conformant on both formats. No defects.

## Condition 2: Unit tests

Full QC4 FAIL inventory (`grep -n QC4 tests/ut/test_verify.py`):

| # | Test | Fmt | Kind | Location |
|---|------|-----|------|----------|
| 1 | `test_fail_qc4_misplaced_title` | RST | 2-section title swap | `tests/ut/test_verify.py:794` |
| 2 | `test_fail_qc4_misplaced_title_md` | MD | 2-section title swap | `tests/ut/test_verify.py:1043` |
| 3 | `test_fail_qc4_misplaced_content_rst` | RST | 2-section content swap | `tests/ut/test_verify.py:1052` |

### Coverage checklist (reviewer-required)

| Case | Status | Evidence |
|------|--------|----------|
| RST title swap | Covered | test 1 |
| MD title swap | Covered | test 2 |
| RST content swap | Covered | test 3 |
| **MD content-only swap** | **Missing** | — |
| **Top-level content misplaced into section position** | **Missing** | — |
| **3-section middle-swap (validates cascading current_pos)** | **Missing** | all existing are 2-section |
| **QC3/QC4 boundary: same text in two places, only `_in_consumed` disambiguates** | **Missing** | — |

The **QC3/QC4 boundary test** is the single most important omission. The classification branch at `verify.py:729-732` (RST) and `verify.py:824-827` (MD) depends entirely on whether `prev_idx` is inside `consumed`. Tests 1–3 use unique strings, so `prev_idx` is never in a consumed range — the QC3 branch never fires for a QC4 candidate in these tests. A refactor that accidentally inverted the `_in_consumed` condition would still make tests 1–3 green while mis-classifying every real QC3 or QC4 FAIL in production. **This is precisely the kind of silent regression a zero-tolerance gate must prevent.**

### Circular-test check

- All three QC4 tests drive real `check_content_completeness` against real RST/MD source text and crafted JSON (no mocking of sequential-delete).
- Assertions are `any("QC4" in i for i in issues)` — they require the correct issue class, which is a spec-level contract, not a restatement of implementation details.
- **Not circular.** However, the assertion granularity is weak: tests do not pin section id, count of issues, or absence of other classes. A bug that reports QC4 *plus* a spurious QC2 on the same run would still pass these asserts. Proposed strengthening under Issues below.

## Condition 3: v6 runtime + pytest

- `cd tools/rbkc && python -m pytest tests/ut/test_verify.py -q` → **134 passed in 0.55s**.
- `cd tools/rbkc && python -m scripts.run verify 6` → **All files verified OK** (0 FAIL).

Both green.

## Issues and proposed fixes

### [Medium] QC3/QC4 boundary branch untested

- **Description**: Branch at `verify.py:729-732` / `824-827` routes to QC3 when the from-start find lands inside a consumed range, else QC4. Tests 1–3 use unique strings so the earlier occurrence is never in `consumed` — the boundary is not exercised from both sides. A regression swapping the two branches or inverting `_in_consumed` would silently pass.
- **Proposed fix**: Add a test where a short string (e.g. a title `"A"`) appears at source positions P1 and P2, and JSON order forces `A` at P1 to be consumed first, then a later JSON unit asks for `A` again but its expected position is P2 — out-of-order, P2 not yet consumed → must fire QC4, not QC3. Mirror the same construction with P2 already consumed to force QC3. Both branches covered in a single commit keeps the boundary locked.

### [Medium] No 3+-section cascade test

- **Description**: All three QC4 FAILs are 2-section swaps. A bug that erroneously advances `current_pos` on a QC4 unit (e.g., moving the `consumed.append` above the else branch) would still pass tests 1–3 because no test has a "correctly-placed unit after a misplaced unit".
- **Proposed fix**: Add a 3-section case where section 2 content is misplaced and sections 1, 3 are correct. Assert exactly one QC4 issue and zero QC1/QC2/QC3.

### [Medium] MD content-only swap missing

- **Description**: `test_fail_qc4_misplaced_content_rst` exists (test 3) but MD only has the title-swap case (test 2). MD's `_squash`-based normalisation path (`verify.py:781-802`) differs enough from RST's that independent coverage is warranted.
- **Proposed fix**: Mirror test 3 as `test_fail_qc4_misplaced_content_md`.

### [Low] Top-level misplaced not tested

- **Description**: Top-level `__top__` units participate in the same forward scan (`verify.py:641-648`). No test asserts QC4 fires when a top-level content actually appears after sections in the source but JSON places it first (or vice versa).
- **Proposed fix**: Construct a source where `top_content` text appears near the bottom; JSON declares it as top-level → expect QC4 on `__top__` unit.

### [Low] Assertions do not exclude cross-class false positives

- **Description**: Existing QC4 tests use `any("QC4" in i ...)`. They do not assert absence of QC1/QC2/QC3 issues on the same input. A bug that emits both QC4 and spurious QC1 would pass.
- **Proposed fix**: In each QC4 test, additionally assert `not any("[QC1]" in i or "[QC2]" in i or "[QC3]" in i for i in issues)` (or pin issue count to 1 where the scenario supports it).

## Positive aspects

- Spec-aligned three-way classification, structurally identical across RST and MD paths — low drift risk.
- QC4 detection (forward scan) is cleanly separated from QC1 residue (from-scratch pass); QC4 cannot leak into QC1 false positives.
- Non-advancement of `current_pos` on QC4 is an important correctness choice and is visibly implemented (`verify.py:719-738`, `814-833`).
- Tests are non-circular — they exercise the full normalise + delete path.
- v6 verify 0 FAIL, 134/134 unit tests green.

## Verdict

- **Implementation**: Spec-conformant on RST and MD.
- **Tests**: Incomplete for a ゼロトレランス gate. The QC3/QC4 boundary, 3-section cascade, MD content swap, top-level misplacement, and cross-class exclusion gaps remain unchanged since r2.
- **v6 runtime**: Green.

v6 PASS + 3 narrowly-scoped FAIL tests is not sufficient evidence for a gate that must catch configuration-silent regressions. QC4 should not be marked ✅ on the maturity matrix until at least the QC3/QC4 boundary test and the 3-section cascade test are added — those are the two that directly guard against future refactors misclassifying real QC4 failures.
