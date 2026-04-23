# QC3 — r7

## Summary

QC3 detection logic in `verify.py` (`_check_rst_content_completeness`,
`_check_md_content_completeness`, `_verify_xlsx`) is spec-consistent:
sequential-delete with `_in_consumed()` correctly implements spec §3-1
手順4 ("既に削除済みの領域と重複していた → FAIL（QC3）"). However,
**three test assertions weaken QC3 detection** by OR-ing "QC3" with a
substring of the message body ("duplicate content" / "duplicated"),
which allows a future non-QC3 emission containing the same substring
to pass the assertion — a direct violation of the bias-avoidance rule
that spec §3-1 distinguishes QC3 from QC2/QC4 by label.

## Findings

### F1. Test OR-assert weakens QC3 label enforcement — RST duplicate content

**Violated clause (spec §3-1, 判定分岐のまとめ)**:
> "JSON テキストが正規化ソースに存在するが先行削除済み | QC3"
> "JSON テキストが正規化ソースに全く存在せず | QC2"
> "削除位置が JSON 順より前に逆行 | QC4"

The spec names QC3 as the single correct label for duplicate-content
detection. Tests must assert that exact label.

**Description**: `test_fail_qc3_duplicate_content_rst` (line 1129) asserts:

```python
assert any("QC3" in i or "duplicate content" in i for i in issues)
```

The OR branch `"duplicate content" in i` matches the issue body. If a
future regression mis-labels the duplicate as `[QC2] ... duplicate
content` (e.g., the `_in_consumed` check is inverted and falls through
to the QC2 fabricated branch with a copy-pasted message), the assert
still passes. The test therefore does not enforce the spec label.

**Fix**: Replace with label-exact assert:
```python
assert any("[QC3]" in i for i in issues)
```
and additionally assert no QC2/QC4 on the same unit:
```python
assert not any("[QC2]" in i or "[QC4]" in i for i in issues)
```

### F2. Test OR-assert weakens QC3 label enforcement — top-level/section duplicate

**Violated clause**: same as F1 (§3-1 判定分岐のまとめ).

**Description**: `test_fail_qc3_top_level_and_section_content_duplicated`
(line 1162) asserts:

```python
assert any("QC3" in i or "duplicate content" in i for i in issues)
```

Same gap as F1 — the substring branch masks a mis-labelled emission.

**Fix**: Use `"[QC3]" in i` and add a negative assertion excluding
QC2/QC4 labels.

### F3. Test OR-assert weakens QC3 label enforcement — MD duplicate content

**Violated clause**: same as F1 (§3-1 判定分岐のまとめ).

**Description**: `test_fail_qc3_duplicate_content_md` (line 1171) asserts:

```python
assert any("QC3" in i or "duplicate content" in i for i in issues)
```

Same gap as F1.

**Fix**: Use `"[QC3]" in i` and add a negative assertion excluding
QC2/QC4 labels.

### F4. Test OR-assert weakens QC3 label enforcement — Excel duplicate cell

**Violated clause (spec §3-1 Excel 削除手順, clause 4)**:
> "QC3（重複）: ソーストークンが見つかったが、その位置が既消費領域と重複していた → FAIL"

**Description**: `test_fail_qc3_duplicate_cell_in_json` (line 1375) asserts:

```python
assert any("QC3" in i or "duplicated" in i for i in issues)
```

The "duplicated" substring appears in the QC3 message body only today,
but the OR branch permits a future non-QC3 issue containing that word
to pass the assertion. Spec pins QC3 as the sole correct label for
Excel duplicate-cell detection.

**Fix**: Use `"[QC3]" in i` and add a negative assertion excluding
QC1/QC2 labels for the same token.

## Observations

- `test_fail_qc3_duplicate_title_md` (line 1138) correctly uses a
  label-only assert (`any("QC3" in i ...)`) without the OR-substring
  escape hatch. This is the correct shape for the other QC3 tests.
- `test_pass_qc3_short_cjk_repeated_in_source_and_json` (line 1140) is
  a legitimate positive guard — source has "概要" twice, each JSON
  title consumes a distinct occurrence, so no QC3 must fire. The
  negative assertion `not any("QC3" in i and "概要" in i ...)` is
  shape-correct.
- `test_fail_qc3_qc4_boundary_duplicate_text_misplaced` (line 1206) is
  a negative guard — single JSON consumption of a duplicated source
  text must not raise QC3. Spec-consistent.
- RST/MD QC3 emission uses the spec-aligned branch order: first
  `find(norm_unit, current_pos)` → hit means in-order (no fault);
  miss then `prev_idx = find(norm_unit)` → if hit and
  `_in_consumed(prev_idx, len)` → QC3; if hit outside consumed → QC4;
  if no hit → QC2 (content) or QC2 fabricated title. This matches
  §3-1 手順 4 exactly.
- `_in_consumed` uses overlap semantics (`pos < e and end > s`), which
  correctly flags partial overlap as duplicate — stricter than "exact
  range reuse" and spec-consistent with "既消費領域と重複".

## Positive Aspects

- QC3 vs QC4 disambiguation is implemented through position state
  (`_in_consumed` vs `prev_idx` relative to `current_pos`), not through
  heuristics — structurally matches spec §3-1 手順 2/4.
- Excel QC3 (`_verify_xlsx`) uses the same `_in_consumed` helper
  pattern, ensuring cross-format consistency with the spec.
- `test_fail_qc3_duplicate_title_md` demonstrates the correct
  label-exact assertion shape — other QC3 tests should follow this
  pattern.
- The positive guard
  `test_pass_qc3_short_cjk_repeated_in_source_and_json` prevents
  false-positive QC3 on legitimate CJK short-title repetition, a real
  risk class for the corpus.
