# Z-1 r7 Bias-avoidance review — QC4 (misplaced content)

**Scope**: `tools/rbkc/scripts/verify/verify.py` QC4 logic (RST + MD)
and `tools/rbkc/tests/ut/test_verify.py` QC4 tests.
**Spec source of truth**: `tools/rbkc/docs/rbkc-verify-quality-design.md`
§3-1 (L60–L185).

---

## Spec re-derivation (from scratch, ignoring r1–r6)

QC4 is defined by §3-1 as follows:

- **L84 definition**: "ソースのセクション A のコンテンツが JSON の異なる
  セクションに配置されている"
- **L166 rule**: "JSON 順 i 番目要素の削除位置が、i-1 番目の削除位置よりも
  前であれば FAIL（QC4: 配置ミス）"
- **L185 branch table**: "削除位置が JSON 順より前に逆行 | QC4"
- **L183–L184 discrimination**: "JSON テキストが正規化ソースに全く存在せず
  → QC2" / "JSON テキストが正規化ソースに存在するが先行削除済み → QC3"

Spec-forced properties:

1. QC4 ⇔ position-regression (find from `current_pos` fails, but the text
   exists at some earlier unconsumed offset).
2. QC4 ≠ QC3: if *every* earlier occurrence is already consumed, the
   verdict is QC3. Tests that only assert "not QC3" do not prove QC4.
3. QC4 ≠ QC2: if no occurrence exists at all, the verdict is QC2.
4. Scope: definition talks about "コンテンツ". §3-1 手順 1 makes section
   `title` part of the same JSON-order unit list, so title misplacement
   rides the same rule. Both title and content misplacement must be
   detectable as QC4.

---

## Findings

### F1. QC3/QC4 boundary test asserts only the negative side — does not pin the spec-specific label

`test_fail_qc3_qc4_boundary_duplicate_text_misplaced` (test_verify.py L1206–L1220)
docstring claims:

> "Must raise QC4 (not QC3) because the text occurs in both positions."

But the assertion is:

```python
assert not any("QC3" in i for i in issues)
```

Two spec-violating defects:

1. **No assertion on QC4 label.** Under ゼロトレランス
   (.claude/rules/rbkc.md §"Decide from the spec"), boundary tests between
   two named checks must pin the spec-named outcome — not merely negate
   the wrong one. "Must raise QC4" is stated in prose but not enforced
   by assertion. Spec clause L185 names QC4 specifically; the test must
   assert `any("QC4" in i for i in issues)` to bind to that clause.

2. **Fixture does not exercise QC3/QC4 discrimination.** The data dict
   contains only one section (`s1`) consuming a single "note". There
   is no second JSON unit that could regress in position, so no
   QC3/QC4 decision is ever reached inside the sequential-delete loop.
   The test is a vacuous guard ("one match → no duplicate flag"), not a
   boundary test. The spec's QC3 vs QC4 split (L184 vs L185) is not
   covered.

**Proposed fix**: replace with a genuine boundary pair — e.g. source
`A\n=\n\nnote\n\nB\n=\n\nnote\n`, JSON with two sections both carrying
`"note"` in swapped positions, and assert the label the spec assigns
(QC4 for regression when an unconsumed earlier occurrence exists; QC3
when the earlier occurrence is already consumed). Add *both* cases as
separate tests so each spec branch has a positive pin.

Spec clause quoted: §3-1 L184–L185 — "JSON テキストが正規化ソースに存在
するが先行削除済み | QC3" / "削除位置が JSON 順より前に逆行 | QC4".

### F2. QC3/QC4 discrimination bug in implementation — `find()` without offset picks earliest, but a later-but-still-before-current-pos occurrence may be unconsumed

`_check_rst_content_completeness` L576 and `_check_md_content_completeness`
L671 both use:

```python
prev_idx = norm_source.find(norm_unit)
```

This returns the **earliest** occurrence. The code then branches on
whether *that earliest offset* is in a consumed range:

- earliest consumed → QC3
- earliest not consumed → QC4

But when the unit occurs 3+ times in the normalised source, it is
possible for the earliest to be consumed while a later (but still before
`current_pos`) occurrence is not consumed. By spec L185 that is QC4
(an unconsumed earlier offset exists, so position-regression holds).
The implementation reports QC3.

Constructable example (3 occurrences of `note`, offsets 0, 10, 20):
section A consumes offset 0 (so `consumed = [(0, 4)]`, `current_pos = 4`);
something else consumes 20+ so `current_pos = 24`; then a later JSON
unit `"note"` whose `find(..., current_pos=24)` fails. `prev_idx =
find("note") = 0`, which is consumed → code reports QC3. But offset 10
is unconsumed and earlier than 24 → spec says QC4.

Spec clause quoted: §3-1 L184 "JSON テキストが正規化ソースに存在するが
**先行削除済み**" (emphasis on 先行削除済み — requires *all* earlier
positions to be consumed, not just the lexicographically first).

**Proposed fix**: scan all occurrences of `norm_unit` in `norm_source`
via iterative `find` / `finditer`. Classify:
- if any occurrence lies in `[0, current_pos)` and is not in `consumed`
  → QC4;
- else if every occurrence lies in `consumed` → QC3;
- else (no occurrence at all) → QC2.

Add a test pinning the 3-occurrence scenario described above (source
has the token three times; consumption pattern leaves a middle
occurrence unconsumed) and assert QC4, not QC3.

Horizontal check: same pattern duplicated in MD branch (L671) — both
sites must be fixed in one pass per `.claude/rules/review-feedback.md`
§"Root-cause horizontal check".

### F3. Three-section rotation coverage is partial — middle-position content swap not tested

`test_fail_qc4_three_section_middle_swap` (L1184) uses three sections
A/B/C and swaps s2/s3 *titles*. But the swap is of full sections (title
+ content both move together), so the regression point is the very
first unit of the swapped section. A content-only middle swap — where
titles stay in order but section B's content appears under section C
and vice versa — is not covered. That case is the pure form of the
spec's L84 definition ("セクション A のコンテンツが JSON の異なる
セクションに配置されている"), since the title placement is innocent.

Existing `test_fail_qc4_md_content_swap` (L1196) covers content-only
swap but only with two sections. Two-section content swap leaves a
single regression point; three-section content-only middle rotation
(e.g. A/B/C titles correct, contents rotated A→a, B→c, C→b) is the
pattern that distinguishes "single swap" from "rotation" and proves
the algorithm tracks each unit independently, not just first-regression.

**Proposed fix**: add an RST and MD case with three sections, titles in
spec order, contents rotated (e.g. s1.content = A, s2.content = C,
s3.content = B). Assert QC4 fires for the middle section's content.

### F4. QC4 tests do not assert the section id in the message

All four QC4 tests assert only `any("QC4" in i for i in issues)`. None
assert *which* section id is flagged. The implementation emits
`f"[QC4] section '{sid}': misplaced ..."` — so the sid is part of the
contract, and a bug that reported the wrong section would be invisible
to these tests.

Spec basis: §3-1 L84 defines the defect as "*セクション A の*
コンテンツが *異なるセクションに* 配置されている" — the identity of
the affected section is part of the defect definition. A test that
does not assert the section id cannot verify the spec property.

**Proposed fix**: for each QC4 test, assert the expected sid appears in
the flagged message (e.g. `any("QC4" in i and "s2" in i for i in issues)`).

---

## Observations (non-blocking, spec-sanctioned)

- **O1. Both title and content regression covered.** `test_fail_qc4_misplaced_title`
  (RST, L884), `test_fail_qc4_misplaced_title_md` (L1175),
  `test_fail_qc4_misplaced_content_rst` (L1222), and
  `test_fail_qc4_md_content_swap` (L1196) together exercise both
  title-swap and content-swap for both formats. This satisfies spec
  §3-1 手順 1 which treats titles and contents as unit-list entries.

- **O2. Implementation order of classification is correct.** The
  if/elif chain first excludes "not found at all" (QC2), then "found but
  consumed" (QC3, subject to F2), then defaults to QC4. The ordering
  itself agrees with the L183–L185 table.

- **O3. `_in_consumed` uses half-open interval overlap** (`pos < e and
  end > s`), which matches the closed-open `(idx, idx + len)` ranges
  appended to `consumed`. No off-by-one bug.

---

## Summary

Four findings. F1 and F4 are test-quality defects (tests do not
assert the spec-named label or the spec-named affected section).
F2 is an implementation bug (QC3/QC4 misclassification when the
unit occurs three or more times with specific consumption pattern) —
present in both RST and MD branches, must be fixed as one class per
horizontal-check rule. F3 is a coverage gap (three-section
content-only rotation missing).

Under ゼロトレランス all four are blocking.
