# Z-1 r8 QC4 bias-avoidance review

**Scope**: QC4 (misplaced content) in `tools/rbkc/scripts/verify/verify.py`
against `tools/rbkc/docs/rbkc-verify-quality-design.md` §3-1, plus
`tools/rbkc/tests/ut/test_verify.py` QC4 coverage.

Format: **BINARY** — Findings (with quoted spec clause) / Observations.

---

## Findings

_None._

All r7 follow-up items are addressed in the current code and tests; no
residual spec-violation was found on this pass.

---

## Observations

### O-1. `_classify_missed_unit` correctly walks ALL occurrences

`verify.py:700-718` iterates every `norm_source.find(unit, start)` hit
and breaks only when an **unconsumed** occurrence is seen:

```python
while True:
    pos = norm_source.find(norm_unit, start)
    if pos == -1:
        break
    any_occurrence = True
    if not in_consumed(pos, len(norm_unit)):
        has_unconsumed = True
        break
    start = pos + 1
```

This matches spec §3-1 判定分岐のまとめ L184:

> | JSON テキストが正規化ソースに存在するが先行削除済み | QC3 |

i.e. the QC3 verdict requires *every* earlier occurrence to be consumed.
The earlier naive `find()` form (earliest-only) would have misclassified
mixed consumption patterns as QC3 instead of QC4. r7 F1 fixed.

### O-2. Section id is pinned in QC4 issue messages

Both RST (`verify.py:768`) and MD (`verify.py:866`) emit:

```
[QC4] section '{sid}': misplaced {label}: ...
```

Spec §3-1 table L84 names QC4 as "ソースのセクション A のコンテンツが
JSON の異なるセクションに配置されている" — i.e. the defective section
must be identifiable. Tests assert the `sid` substring explicitly:

- `test_fail_qc4_misplaced_title` — `"s2" in i`
- `test_fail_qc4_misplaced_title_md` — `"s2" in i`
- `test_fail_qc4_three_section_middle_swap` — `"s3" in i`
- `test_fail_qc4_md_content_swap` — `"s2" in i`
- `test_fail_qc4_misplaced_content_rst` — `"s2" in i`

r7 F2 fixed — previous assertions that checked only `[QC4] in i` are
replaced with id-pinned forms.

### O-3. Three-section content-only rotation covered for both RST and MD

`test_fail_qc4_three_section_content_only_rotation_rst` and
`test_fail_qc4_three_section_content_only_rotation_md` both exercise
the spec §3-1 L84 scenario where titles are in order but contents are
rotated A→a, B→c, C→b. r7 F3 fixed.

### O-4. QC3 ↔ QC4 boundary is pinned, not vacuously asserted

`test_fail_qc4_boundary_text_occurs_in_both_positions_misplaced`
(verify_test:1605-1625) explicitly asserts `[QC4]` presence. The
docstring calls out the prior weakness:

> This test pins the label explicitly — a prior version of this test
> asserted only 'not QC3' which was vacuous when only one consumption
> occurred.

Additionally `test_fail_qc4_not_qc3_when_middle_occurrence_is_unconsumed`
covers the precise boundary condition from spec L184 (every earlier
position consumed) vs. L185 (position regression) — earliest consumed
+ middle unconsumed + last consumed → must be QC4, not QC3. Both
inclusion (`[QC4] in issues`) and exclusion (`not [QC3] in issues`)
are asserted. This is the strongest form available for the boundary.

### O-5. QC2/QC3/QC4 label exclusivity guarded elsewhere

`test_fail_qc4_*` tests assert QC4 presence; complementary QC3 tests
(e.g. verify_test:1484, 1519, 1529) assert `not [QC2] or [QC4]`. Taken
together the test suite prevents any single miss from being silently
mis-labelled between QC2/QC3/QC4 — matching the three mutually-exclusive
branches of `_classify_missed_unit`.

### O-6. Unit signature is independent of call-site state

`_classify_missed_unit` takes `consumed` and `in_consumed` as
parameters rather than reading call-site locals — both the RST and MD
paths share the same classifier, so a bug fix in the classifier covers
both formats in one place (r7 F1 was one regression, not two).

---

## Conclusion

QC4 implementation and tests match spec §3-1 (L84, L165-166, L184-185).
All r7 findings (F1 earliest-only bug, F2 unpinned sid, F3 missing
three-section rotation, boundary pin) are resolved with spec-derived
assertions. No new spec violations observed.
