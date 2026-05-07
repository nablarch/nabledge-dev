# Excel P2 Sheet Investigation

## Summary

- Total Excel files analyzed: 76
- Total sheets analyzed: 212
- P1 sheets: 95
- P2 sheets: 117 (breakdown: §8-2 forced=53, header-detection-fail=64)

## P2 Sheets by Version

### v6

| File | Sheet | P2 Reason | Category | Cell-LF? | Notes |
|------|-------|-----------|----------|----------|-------|
| Nablarch機能のセキュリティ対応表.xlsx | 1.概要 | run_length<3 | (c) | no | useful_width=5; free-form prose with sparse single-cell rows |
| Nablarch機能のセキュリティ対応表.xlsx | 3.PCIDSS対応表 | run_length<3 | (b) | yes | useful_width=3; 2-col table (PCI要件, チェックリスト対応) with 4 cells containing enumerated items joined by \\n |
| nablarch6-releasenote.xlsx | バージョンアップ手順 | §8-2 | (c) | no | useful_width=2 (1 step only, free text reference) |
| nablarch6u1-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3; 2-col numbered step table (No/適用手順) with col 0 empty |
| nablarch6u1-releasenote.xlsx | 件数取得SQLの拡張ポイント追加 | §8-2 | (c) | no | useful_width=2; 1-col description text |
| nablarch6u2-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (b) | yes | useful_width=3; 2-col step table; 1 data cell has Maven artifact list with \\n (list items run together) |
| nablarch6u3-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3; 2-col step table, no LF in data |
| nablarch6u3-releasenote.xlsx | マルチパートリクエストのサポート対応 | run_length<3 | (c) | no | useful_width=5; pure prose/instructions with deep indentation structure |

### v5

| File | Sheet | P2 Reason | Category | Cell-LF? | Notes |
|------|-------|-----------|----------|----------|-------|
| Nablarch機能のセキュリティ対応表.xlsx | 1.概要 | run_length<3 | (c) | no | useful_width=5; free-form prose (same as v6) |
| Nablarch機能のセキュリティ対応表.xlsx | 3.PCIDSS対応表 | run_length<3 | (b) | yes | useful_width=3; same as v6; 4 cells with enumerated items joined by \\n |
| nablarch5-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1; single-column classification list |
| nablarch5-releasenote.xlsx | 別紙_分割後jarの取り込み | run_length<3 | (c) | no | useful_width=4; prose instructions |
| nablarch5u1-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3; 2-col step table, no LF |
| nablarch5u1-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch5u10-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u11-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u12-releasenote.xlsx | NumberRangeの対応方法 | §8-2 | (c) | no | useful_width=1 |
| nablarch5u12-releasenote.xlsx | データベースアクセスの型変換機能削除の対応方法 | run_length<3 | (c) | no | useful_width=4; prose instructions |
| nablarch5u12-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u13-releasenote.xlsx | Domaのロガーを5u12までと同じ動作にする方法 | §8-2 | (c) | no | useful_width=1 |
| nablarch5u13-releasenote.xlsx | システムリポジトリを5u12までと同じ動作にする方法 | §8-2 | (c) | no | useful_width=1 |
| nablarch5u13-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u13-releasenote.xlsx | 定型メール送信要求を5u12までと同じ動作にする方法 | §8-2 | (c) | no | useful_width=1 |
| nablarch5u14-releasenote.xlsx | HIDDENストア脆弱性 | run_length<3 | (c) | no | useful_width=9; long security report document (deeply indented prose) |
| nablarch5u14-releasenote.xlsx | バージョンアップ手順 | §8-2 | (c) | no | useful_width=2; 2-col step table (No/適用手順) with col 0 empty — §8-2 forces P2 |
| nablarch5u14-releasenote.xlsx | ボタンのアイコンを変更する場合 | §8-2 | (c) | no | useful_width=2; 1-col prose instructions |
| nablarch5u14-releasenote.xlsx | 汎用データフォーマットXXE脆弱性 | run_length<3 | (c) | no | useful_width=3; prose |
| nablarch5u15-releasenote.xlsx | HttpServerクラスを使っている場合の対応方法 | §8-2 | (c) | no | useful_width=2 |
| nablarch5u15-releasenote.xlsx | テスティングフレームワークの設定変更方法 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u15-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u15-releasenote.xlsx | 標準プラグインの変更点 | run_length<3 | (b) | yes | useful_width=6; has proper 6-col header but only 1 data row → data_rows_available<2 triggers P2; header cells "変更実施\nバージョン" and "プラグイン\nバージョン" contain \\n |
| nablarch5u16-releasenote.xlsx | Jackson1系の使用有無判断方法 | §8-2 | (c) | no | useful_width=2 |
| nablarch5u16-releasenote.xlsx | Jackson1系の設定変更方法 | §8-2 | (c) | no | useful_width=2 |
| nablarch5u16-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u17-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u18-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u19-releasenote.xlsx | Content-Typeの互換性維持方法 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u19-releasenote.xlsx | JSON読み取り失敗ケース | run_length<3 | (c) | no | useful_width=4 |
| nablarch5u19-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u19-releasenote.xlsx | 環境依存値の設定方法 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u2-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u2-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch5u20-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u21-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u21-releasenote.xlsx | 使用不許可APIチェックツールの設定方法 | run_length<3 | (c) | no | useful_width=5 |
| nablarch5u22-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u23-releasenote.xlsx | DBアクセス失敗時の例外ハンドリング | §8-2 | (c) | no | useful_width=2 |
| nablarch5u23-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u24-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u24-releasenote.xlsx | 件数取得SQLの拡張ポイント追加 | §8-2 | (c) | no | useful_width=2 |
| nablarch5u25-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (b) | yes | useful_width=3; 2-col step table; 1 data cell has Maven artifact list with \\n |
| nablarch5u26-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u3-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u3-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch5u4-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u4-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch5u5-releasenote.xlsx | データベース機能のバージョンアップ対応 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u5-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u5-releasenote.xlsx | 認可データ設定ツールのバージョンアップ方法 | §8-2 | (b) | yes | useful_width=2; §8-2 forced; row 17 contains a ~25-line XML code example in a single cell — severely flattened |
| nablarch5u6-releasenote.xlsx | X-Frame-Optoinsの設定 | §8-2 | (c) | no | useful_width=1 |
| nablarch5u6-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u6-releasenote.xlsx | メッセージ分割 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u7-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u8-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u9-releasenote.xlsx | ETLの設定変更内容 | §8-2 | (c) | no | useful_width=0 (empty sheet body) |
| nablarch5u9-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch5u9-releasenote.xlsx | メール送信の設定変更内容 | run_length<3 | (c) | no | useful_width=3 |

### v1.4

| File | Sheet | P2 Reason | Category | Cell-LF? | Notes |
|------|-------|-----------|----------|----------|-------|
| nablarch-1.4.0-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.0.4-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.1-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.1.1-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.10-releasenote.xlsx | JSON読み取り失敗ケース | run_length<3 | (c) | no | useful_width=4; prose instructions |
| nablarch-1.4.10-releasenote.xlsx | バージョンアップ手順 | §8-2 | (c) | no | useful_width=2; 2-col step table (No/適用手順); 1 step only |
| nablarch-1.4.10-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.11-releasenote.xlsx | バージョンアップ手順 | §8-2 | (c) | no | useful_width=2; 2-col step table; 1 step only |
| nablarch-1.4.11-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.2-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.3-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.4-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.5-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3; 2-col step table (col 0 empty) |
| nablarch-1.4.6-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.4.6-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.7-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.4.7-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.8-releasenote.xlsx | NumberRangeの対応方法 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.8-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.4.8-releasenote.xlsx | リポジトリを1.4.7までと同じ動作にする方法 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.8-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.9-releasenote.xlsx | バージョンアップ手順 | §8-2 | (c) | no | useful_width=2; 2-col step table; 1 step only |
| nablarch-1.4.9-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.4.9-releasenote.xlsx | 汎用データフォーマットXXE脆弱性 | run_length<3 | (c) | no | useful_width=3; prose security report |

### v1.3

| File | Sheet | P2 Reason | Category | Cell-LF? | Notes |
|------|-------|-----------|----------|----------|-------|
| nablarch-1.3.2-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.3.3-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.3.3-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.3.4-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.3.4-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.3.5-releasenote.xlsx | NumberRangeの対応方法 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.3.5-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.3.5-releasenote.xlsx | リポジトリを1.3.4までと同じ動作にする方法 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.3.5-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.3.6-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.3.6-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.3.7-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.3.7-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |

### v1.2

| File | Sheet | P2 Reason | Category | Cell-LF? | Notes |
|------|-------|-----------|----------|----------|-------|
| nablarch-1.2.3-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.2.4-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.2.4-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.2.5-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.2.5-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.2.6-releasenote.xlsx | NumberRangeの対応方法 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.2.6-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.2.6-releasenote.xlsx | リポジトリを1.2.5までと同じ動作にする方法 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.2.6-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.2.7-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.2.7-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |
| nablarch-1.2.8-releasenote.xlsx | バージョンアップ手順 | run_length<3 | (c) | no | useful_width=3 |
| nablarch-1.2.8-releasenote.xlsx | 分類 | §8-2 | (c) | no | useful_width=1 |

## Cross-version Patterns

### バージョンアップ手順 (44 sheets, the dominant P2 pattern)

Every release note file has a `バージョンアップ手順` sheet.  Its structure is invariant:

- Col 0: empty (no data)
- Col 1: `No` (row number)
- Col 2: `適用手順` (step text)

Because col 0 is always empty, `_run_length()` of the header row returns **2**, which is below the detection threshold of 3. Result: P2 via `run_length<3` (useful_width=3) or §8-2 (useful_width=2 when the sheet has ≤2 steps and openpyxl trims col 0).

The current P2 JSON output is readable — `No  適用手順\n1  step1\n2  step2` — so most of these are correctly (c). However, when a data cell contains a `\n`-separated list of Maven artifact names (v6u2, v5u25), the list items are joined with spaces and lose their list structure.

### 分類 sheets (many versions, §8-2 forced, useful_width=1)

All releasenote files include a `分類` sheet with a single column of classification codes. `useful_width=1 ≤ 2` → §8-2 forced P2. Content is simple enumeration; P2 output is correct.

### セキュリティ対応表 — 3.PCIDSS対応表 (v5 and v6)

The `Nablarch機能のセキュリティ対応表.xlsx` sheet `3.PCIDSS対応表` appears in both v5 and v6. It has useful_width=3 but the first two rows are preamble prose, and col 0 carries the preamble while cols 1–2 hold the 2-col table. The header row `PCI DSS 要件 / 2.チェックリストとの対応` has run_length=2, so header detection fails. Four data cells contain `\n`-joined enumerated vulnerability category names that are flattened.

### Embedded-LF count

6 of 117 P2 sheets have at least one cell containing `\n`. All 6 are in v5/v6 only; v1.x P2 sheets have no embedded newlines.

## Candidate Improvements

### (a) Misclassified as P2 (should be P1)

No sheets are misclassified as P2. All P2 classifications reflect genuine structural limitations:

- §8-2 sheets with useful_width=2 (バージョンアップ手順 1.4.9/1.4.10/1.4.11, nablarch5u14): these are 2-col numbered step tables, but §8-2 correctly treats them as P2. The P2 output "No  適用手順\n1  step\n2  step" is already readable. Promoting to P1 would produce the same information in slightly more structured form but is not a quality issue.
- `nablarch5u15 標準プラグインの変更点`: 6-col table with a proper header, but only 1 data row — `data_rows_available < 2` prevents P1. With only 1 data row, a P1 single-section output adds no readability value over the P2 flat rendering.
- All `run_length<3` バージョンアップ手順 sheets: the col-0 empty column reduces run_length to 2. P2 output renders the table content inline and remains readable.

**Conclusion**: no sheets need reclassification from P2 to P1.

### (b) Correctly P2 but poor readability

5 sheets are correctly classified P2 but suffer readability loss due to `\n` → space flattening in `_flatten_ws`:

| Version | File | Sheet | LF Impact |
|---------|------|-------|-----------|
| v6 | Nablarch機能のセキュリティ対応表.xlsx | 3.PCIDSS対応表 | 4 cells; each cell enumerates 3–6 vulnerability category names (e.g. "1.SQLインジェクション\n7.HTTPヘッダ・インジェクション") — flattened to a run-on string |
| v5 | Nablarch機能のセキュリティ対応表.xlsx | 3.PCIDSS対応表 | Same file/same issue |
| v6 | nablarch6u2-releasenote.xlsx | バージョンアップ手順 | 1 cell; Maven artifact list ("・micrometer-registry-datadog\n・micrometer-registry-cloudwatch2\n...") joined with spaces |
| v5 | nablarch5u25-releasenote.xlsx | バージョンアップ手順 | Same pattern as v6u2 |
| v5 | nablarch5u5-releasenote.xlsx | 認可データ設定ツールのバージョンアップ方法 | 1 cell; ~25-line XML code example stored in a single cell — severely flattened into a single long line |

**Fix**: In `_build_p2_content()`, replace `_flatten_ws(c)` with a version that converts `\n` to `  \n` (Markdown hard line break) rather than space, so list items within a cell remain on separate lines. Alternatively, split multi-line cells into separate output lines separated by `\n`. The fix must be validated against verify's QC1/QC3 token checks to ensure no regression.
