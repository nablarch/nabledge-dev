# Stage 3 — 15件中間確認 (Sonnet)

**Date**: 2026-04-22
**Scenarios**: 15 (qa-v6-sample15.json)
**Model**: Sonnet

## シナリオ構成

5件パイロット (review-01/04, impact-01, req-02/09) +
新規10件 (review-07/08/09, impact-04/05/06/09, req-01/05/07)

| カテゴリ | 件数 |
|---------|------|
| review | 5 |
| impact | 5 |
| req    | 5 |

## 結果

- mean judge level:     **3.00 / 3**
- level distribution:  `{0: 0, 1: 0, 2: 0, 3: 15}`
- mean candidates:     76.6行 (fallback=none 全件)
- mean picks (AI-2):   5.1セクション (range 3–8)
- mean cost (USD):     **$0.522** /件
- mean wall (s):       **82.2s** /件

| id | filter | picks | judge |
|----|--------|-------|-------|
| review-01 | 57 | 8 | 3 |
| review-04 | 68 | 5 | 3 |
| review-07 | 79 | 5 | 3 |
| review-08 | 113 | 6 | 3 |
| review-09 | 46 | 4 | 3 |
| impact-01 | 67 | 5 | 3 |
| impact-04 | 56 | 3 | 3 |
| impact-05 | 124 | 7 | 3 |
| impact-06 | 23 | 3 | 3 |
| impact-09 | 68 | 4 | 3 |
| req-01 | 124 | 5 | 3 |
| req-02 | 124 | 7 | 3 |
| req-05 | 68 | 5 | 3 |
| req-07 | 66 | 5 | 3 |
| req-09 | 66 | 4 | 3 |

Full run: `tools/benchmark/.results/20260422-141243-stage3-sonnet/`

## 注目点

- **impact-04 (3セクション)**: RetryHandler 1ファイルに絞り込み、回答は XML 設定例・ハンドラ順序・上限値設定指針まで完全網羅。AI-2 の「fewer is better」が正しく機能。
- **impact-06 (3セクション)**: CSP + JSP 書き換えの not-built-in 系。23候補の最少フィルタでも judge=3。
- **review-08 (マルチスレッドDB更新)**: 113候補から6セクションに絞り judge=3。複雑な横断トピックも機能。
- **fallback=none 全15件**: 1件もフォールバックなし。ファセット設計が安定。

## AI-2 pick count 分布（5件→15件比較）

| 件数 | mean picks |
|------|-----------|
| 5件  | 8.6 |
| 15件 | 5.1 |

→ PE レビューで追加した「目標3–6」ルールが効いて大幅改善。コスト削減にも貢献。

## Assessment

分散なし。5件パイロットの傾向が15件でも完全に再現。
異常値・judge=2以下は出なかった。

**懸念**: 全15件 judge=3 は「難しい問題がまだない」可能性を排除できない。
ただし新規10件には事前に expected_facets を設定しておらず、出来レース要素は5件のみに限定されている。

## Decision

15件確認クリア。**30件ベースライン**に進む。
