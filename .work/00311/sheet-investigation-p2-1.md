# P2(c) Column-Indent Structure Investigation

## Summary

64 P2(c) sheets analyzed (run_length<3 with useful_width>2; §8-2 sheets excluded).

| Category | Count | Treatment |
|----------|-------|-----------|
| Column-indent (P2-1 candidate) | 16 | Absolute-column → Markdown heading |
| Table structure (P2-2) | 45 | Current behavior maintained |
| Flat / single-col (P2-2) | 2 | Current behavior maintained |

## Column-Indent Sheets (P2-1 Candidates)

Criteria: single_cell_ratio ≥ 0.60 AND distinct_cols_used ≥ 2

The absolute-column mapping adopted in task [A] applies: col0=H1, col1=H2, col2=H3, col3+=body.

| Version | File | Sheet | useful_width | single_cell_ratio | col_distribution |
|---------|------|-------|--------------|-------------------|-----------------|
| v1.4 | nablarch-1.4.10-releasenote.xlsx | JSON読み取り失敗ケース | 4 | 0.86 | {1:4, 2:3, 5:5} |
| v1.4 | nablarch-1.4.9-releasenote.xlsx | 汎用データフォーマットXXE脆弱性 | 3 | 1.0 | {1:6, 2:27, 3:46} |
| v5 | Nablarch機能のセキュリティ対応表.xlsx | 1.概要 | 5 | 0.9 | {1:1, 2:2, 3:15} |
| v5 | nablarch5-releasenote.xlsx | 別紙_分割後jarの取り込み | 4 | 0.75 | {0:15, 1:4, 2:8} |
| v5 | nablarch5u12-releasenote.xlsx | データベースアクセスの型変換機能削除の対応方法 | 4 | 1.0 | {0:4, 1:11, 2:22, 3:2} |
| v5 | nablarch5u14-releasenote.xlsx | HIDDENストア脆弱性 | 9 | 0.95 | {0:1, 1:6, 2:15, 3:21, 4:14, 5:7, 6:11} |
| v5 | nablarch5u14-releasenote.xlsx | 汎用データフォーマットXXE脆弱性 | 3 | 1.0 | {1:6, 2:27, 3:46} |
| v5 | nablarch5u15-releasenote.xlsx | テスティングフレームワークの設定変更方法 | 3 | 1.0 | {1:4, 2:17, 3:7} |
| v5 | nablarch5u19-releasenote.xlsx | Content-Typeの互換性維持方法 | 3 | 1.0 | {1:1, 2:3, 3:3} |
| v5 | nablarch5u19-releasenote.xlsx | JSON読み取り失敗ケース | 4 | 0.86 | {1:4, 2:3, 5:5} |
| v5 | nablarch5u19-releasenote.xlsx | 環境依存値の設定方法 | 3 | 1.0 | {1:1, 2:3, 3:3} |
| v5 | nablarch5u22-releasenote.xlsx | バージョンアップ手順 | 3 | 0.62 | {0:2, 1:3} |
| v5 | nablarch5u5-releasenote.xlsx | データベース機能のバージョンアップ対応 | 3 | 1.0 | {0:1, 1:5, 2:25} |
| v5 | nablarch5u6-releasenote.xlsx | メッセージ分割 | 3 | 1.0 | {0:5, 1:16, 2:33} |
| v5 | nablarch5u9-releasenote.xlsx | メール送信の設定変更内容 | 3 | 0.84 | {1:9, 2:7} |
| v6 | Nablarch機能のセキュリティ対応表.xlsx | 1.概要 | 5 | 0.9 | {1:1, 2:2, 3:15} |
| v6 | nablarch6u3-releasenote.xlsx | マルチパートリクエストのサポート対応 | 5 | 1.0 | {1:3, 2:8, 3:12, 4:12, 5:6} |

### Notes on col_distribution

Most column-indent sheets start at col1 (col0 is empty). With the absolute mapping:
- col0 data → H1 (rare; `別紙_分割後jarの取り込み`, `HIDDENストア脆弱性` use col0 for top-level headings)
- col1 data → H2
- col2 data → H3
- col3+ data → body paragraph

The `HIDDENストア脆弱性` sheet uses up to col6 — cols 3-6 all map to body (H4 is not used in the spec).

### Special case: nablarch5u22 バージョンアップ手順

col_dist={0:2, 1:3} with SCR=0.62. This appears in the column-indent list due to a borderline heuristic result, but is structurally a 2-col step table (not a prose outline). The run_length=2 header `[(1, 'No'), (2, '適用手順')]` confirms it. The actual step data rows have 2 cells (col1=No, col2=手順), pushing multi_col_ratio to 0.38 (just below the 0.5 "table" threshold). **Corrected classification: P2-2** (step table, current behavior maintained). This leaves 16 confirmed P2-1 sheets.

## P1 run_length=2 Candidates (threshold 3→2 side-effect analysis)

30 sheets would change from P2 to P1 if the threshold is lowered from 3 to 2.

All 30 fall into exactly 2 patterns:

| Pattern | Sheets | Header row |
|---------|--------|-----------|
| バージョンアップ手順 (step tables) | 28 | `No / 適用手順` at col1/col2 |
| 3.PCIDSS対応表 (v5/v6) | 2 | `PCI DSS 要件 / 2.チェックリストとの対応` at col1/col2 |

**No false positives confirmed**: The 17 column-indent sheets (prose outlines) do NOT appear in the P1 run_length=2 candidates list — they have no row with run_length=2 that resembles a header. The threshold change would affect only 2-column step tables.

## Recommendation: Drop P1-1 (threshold change)

The P1-1 improvement (threshold 3→2 → `バージョンアップ手順` becomes P1) is safe but low-value:

- `バージョンアップ手順` P2 output is already readable: `No  適用手順\n1  step1`
- Promoting to P1 changes JSON content from flat text to `No: 1\n適用手順: step1` per section — not a readability gain
- `3.PCIDSS対応表` has embedded LF issues better addressed by P2-3 (LF preservation)
- Adds implementation complexity and verify coverage changes

**Decision**: P1-1 is out of scope for this issue. Focus on P2-1 and P2-3.

## Final Pattern Classification

From the combined analysis (xlsx-p2-investigation.md + this file):

| Pattern | Count | Sheets |
|---------|-------|--------|
| **P2-1** (column-indent → Markdown headings) | 17 | Prose outline docs |
| **P2-2** (current behavior maintained) | 95 | バージョンアップ手順 (table), 分類, etc. |
| **P2-3** (LF preserved as Markdown line breaks) | 5 | PCIDSS, v6u2/v5u25 バージョンアップ手順, v5u5 認可 |

Note: The 5 P2-3 sheets remain P2 but get LF-preservation treatment. Some P2-1 sheets and P2-2 sheets overlap with P2-3 if they have embedded LF — but the investigation found no column-indent sheets with embedded LF, so the categories are disjoint.
