# Stage 3 — 30件ベースライン (Sonnet, 2026-04-22)

**Date**: 2026-04-22
**Scenarios**: qa-v6.json (全30件)
**Model**: Sonnet
**Run dir**: `tools/benchmark/.results/20260422-143411-stage3-sonnet/`
**Baseline**: `tools/benchmark/baseline/20260422-stage3-sonnet/`

## 結果

- judge=3 率: **30/30 (100%)**
- level 分布: `{0:0, 1:0, 2:0, 3:30}`
- fallback=none: 全30件
- mean candidates: 81.8行
- mean picks: 5.3セクション (min 1, max 8)
- mean cost: $0.528/件 (合計 $15.83)
- mean wall: 82.7s/件 (合計 41.4分、逐次実行)

## スケール比較

| サンプル | judge=3 率 | mean picks | mean cost |
|---------|-----------|-----------|----------|
| 5件     | 5/5 (100%) | 8.6 | $0.557 |
| 15件    | 15/15 (100%) | 5.1 | $0.522 |
| 30件    | 30/30 (100%) | 5.3 | $0.528 |

→ 5件→15件で AI-2 picks が改善（PE レビューの効果）。15件→30件は安定。

## 特記事項

- **review-10** (candidates=2, picks=1): 静的解析ツール質問。2候補から1セクション選択で完全回答。ファセット設計の精度が高い証拠。
- **出来レース要素**: expected_facets を持つのは元の5件のみ。残り25件は事前調整なし。
- **全フォールバックなし**: 30件全件で type×category AND-filter がプライマリで命中。

## Decision

ベースライン確立。次: **本番 skill への反映**（全5バージョン）。
