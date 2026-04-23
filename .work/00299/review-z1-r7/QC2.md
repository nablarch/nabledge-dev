# QC2 — r7

## Summary

0 Findings. QC2 logic across RST, MD, and Excel paths aligns with spec §3-1.
The `_MD_SYNTAX_RE` tolerance list for Excel is explicitly sanctioned by
spec line 226 ("許容構文要素リスト（QC2 残存判定）"). The 1-char residue
test case (lines 1297-1309) exercises the ゼロトレランス requirement
derived from spec §3-1 Excel 手順 3.

Derivation (from spec, not from implementation):

1. Spec §3-1 (line 172): "正規化ソース中に当該テキストが一度も出現しなかった
   → FAIL（QC2: 誤追加）" — implemented at verify.py:578-579 (title),
   584-585 (content) for RST, 673-674 / 679-680 for MD. Classification
   via `prev_idx == -1` directly models "一度も出現しなかった".

2. Spec §3-1 (line 183): "JSON テキストが正規化ソースに全く存在せず | QC2"
   — same code paths.

3. Spec §3-1 Excel 手順 3 (line 223): "全ソーストークン削除後に JSON テキ
   ストに残ったテキスト（空白・空行を除く）→ FAIL" — implemented at
   verify.py:822-829. Residual computed by merge-and-skip of consumed
   spans (804-820); any non-whitespace split-token triggers QC2.

4. Spec §3-1 Excel (line 226): "許容構文要素リスト（QC2 残存判定）:
   テーブル記号 `|`・`---`、強調記号 `**` 等…これらは JSON テキストに残
   存しても QC2 の対象外とする" — `_MD_SYNTAX_RE` covers `|`,
   `|---|...`, `**`, `*`, `__` (word-boundary aware), `` ` ``,
   line-start `#+`, `>`, and `\d+.`. The named trio (`|`, `---`, `**`)
   is covered; the other patterns fall under 等.

## Findings

None.

## Observations

- **Test 1343-1345 (`test_fail_xls_qc2_fabrication`)**: asserts
  `"捏造" in i`. This is not circular — the substring "捏造" comes from
  the JSON title token (`"ABC 捏造"`) being echoed into the issue message
  via `{token!r}`. The test would still fail if verify silently dropped
  the fabrication, so it is a real behavioural assertion. No change
  required.

- **Test 1297-1309 (`test_fail_qc2_one_char_fabrication_detected`)**:
  directly guards the ゼロトレランス rule cited in `.claude/rules/rbkc.md`
  ("1-char Excel residue → FAIL. Spec §3-1 Excel 節 says any residue
  other than whitespace is QC2."). Good spec-derived oracle.

- **`_MD_SYNTAX_RE` word-boundary on `__`**: uses `__(?![\w])|(?<![\w])__`
  rather than a single `\b__\b`. Both forms are equivalent for ASCII; the
  current form is correct. Noted only because future contributors might
  simplify it and accidentally break on CJK-adjacent underscores.

- **RST/MD QC2 classification via `find(norm_unit)` from 0**: relies on
  a second pass to distinguish QC2 from QC3/QC4. This is correct per
  spec line 172 (classification is whether the unit appears anywhere
  in the normalised source). No double-counting because the branches
  are mutually exclusive (`prev_idx == -1` vs `_in_consumed` vs else).

- **Excel QC2 splits residual on whitespace after MD-syntax stripping**
  (verify.py:826). Each fabricated word becomes a separate issue line,
  matching the "report all fragments" convention in
  `.claude/rules/rbkc.md`. Consistent with MD QC1 all-fragments reporting.

## Positive Aspects

- Classification logic (QC2 vs QC3 vs QC4) is derived from `prev_idx` +
  `_in_consumed`, directly mirroring the spec's decision table
  (lines 183-185).
- Excel tolerance list is minimal and each pattern is defensible against
  spec line 226's named set plus 等.
- Tests cover: single-token fabrication, multiple fabrications,
  top-level fabrication, 1-char residue (zero-tolerance guard),
  near-miss/misplaced cases, `.xls` path parity with `.xlsx`.
- verify stays independent of the converter (spec line 209): the
  residual-check logic works from the JSON + Excel cells alone.
