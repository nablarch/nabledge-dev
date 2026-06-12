# ベンチマーク結果: baseline-current (2026-05-18, 3 runs)

## 品質サマリー（3 run集計）

| 軸 | PASS | FAIL | UNCERTAIN | ABSENT | PASS率 |
|---|---|---|---|---|---|
| 回答精度（must） | 108 | 0 | 3 | 18 | 83.7% |
| ハルシネーション | 13 | 63 | 14 | - | 14.4% |

## パフォーマンスサマリー（外れ値除外後）

| メトリクス | 平均±SD | 中央値 | P95 | 最大 | 外れ値除外件数 |
|---|---|---|---|---|---|
| 実行時間（総合） | 135s ± 41s | 138s | 205s | 238s | 0 |
| ターン数 | 7.5 ± 2.3 | 7.3 | 11.0 | 13.7 | 1 |
| コスト/シナリオ | $0.6593 ± $0.1678 | $0.6792 | $0.9484 | $0.9501 | 0 |

合計コスト（3 run）: $59.3384

## シナリオ別詳細（3 run平均）

| シナリオID | 精度 | 幻覚 | sections中央値 | ターン数中央値 |
|---|---|---|---|---|
| impact-01 | 100% | 67% | 2 | 4.0 |
| impact-03 | 100% | 0% | 5 | 8.0 |
| impact-06 | 100% | 0% | 6 | 12.0 |
| impact-08 | 100% | 0% | 6 | 7.0 |
| oos-impact-01 | 100% | 0% | 7 | 10.0 |
| oos-qa-01 | 100% | 0% | 3 | 6.0 |
| pre-01 | 100% | 0% | 4 | 8.0 |
| pre-02 | 100% | 0% | 7 | 5.0 |
| pre-03 | 100% | 33% | 7 | 6.0 |
| qa-01 | 100% | 67% | 3 | 6.0 |
| qa-02 | 17% | 0% | 10 | 7.0 |
| qa-03 | 100% | 0% | 4 | 6.0 |
| qa-04 | 100% | 0% | 6 | 8.0 |
| qa-05 | 100% | 0% | 4 | 7.0 |
| qa-06 | 100% | 100% | 5 | 6.0 |
| qa-07 | 100% | 33% | 4 | 9.0 |
| qa-08 | 100% | 0% | 5 | 4.0 |
| qa-09 | 100% | 0% | 8 | 8.0 |
| qa-10 | 100% | 67% | 4 | 9.0 |
| qa-11a | 100% | 0% | 8 | 8.0 |
| qa-11b | 0% | 0% | 10 | 6.0 |
| qa-12a | 33% | 0% | 8 | 20.0 |
| qa-12b | 50% | 0% | 7 | 7.0 |
| qa-13 | 0% | 0% | 9 | 7.0 |
| qa-14 | 100% | 0% | 10 | 7.0 |
| qa-15 | 100% | 0% | 8 | 4.0 |
| review-06 | 100% | 0% | 6 | 4.0 |
| review-07 | 100% | 67% | 5 | 10.0 |
| review-08 | 100% | 0% | 5 | 5.0 |
| review-09 | 100% | 0% | 6 | 10.0 |

## 人間レビュー対象

| シナリオID | 判定 | run数 |
|---|---|---|
| impact-01 | hallucination:FAIL | 1 |
| impact-03 | hallucination:FAIL | 3 |
| impact-06 | hallucination:FAIL | 3 |
| impact-08 | hallucination:FAIL, hallucination:UNCERTAIN | 3 |
| oos-impact-01 | hallucination:UNCERTAIN | 3 |
| oos-qa-01 | hallucination:UNCERTAIN | 3 |
| pre-01 | hallucination:FAIL | 3 |
| pre-02 | hallucination:FAIL | 3 |
| pre-03 | hallucination:FAIL | 2 |
| qa-01 | hallucination:FAIL | 1 |
| qa-02 | claim:ABSENT, hallucination:FAIL | 3 |
| qa-03 | hallucination:FAIL | 3 |
| qa-04 | hallucination:FAIL, hallucination:UNCERTAIN | 3 |
| qa-05 | hallucination:FAIL, hallucination:UNCERTAIN | 3 |
| qa-07 | hallucination:FAIL | 2 |
| qa-08 | hallucination:FAIL | 3 |
| qa-09 | hallucination:FAIL, hallucination:UNCERTAIN | 3 |
| qa-10 | hallucination:FAIL | 1 |
| qa-11a | hallucination:FAIL | 3 |
| qa-11b | claim:ABSENT, hallucination:FAIL, hallucination:UNCERTAIN | 3 |
| qa-12a | claim:ABSENT, hallucination:FAIL | 3 |
| qa-12b | claim:ABSENT, claim:UNCERTAIN, hallucination:FAIL | 3 |
| qa-13 | claim:ABSENT, claim:UNCERTAIN, hallucination:FAIL, hallucination:UNCERTAIN | 3 |
| qa-14 | hallucination:FAIL, hallucination:UNCERTAIN | 3 |
| qa-15 | hallucination:FAIL | 3 |
| review-06 | hallucination:FAIL | 3 |
| review-07 | hallucination:FAIL | 1 |
| review-08 | hallucination:FAIL, hallucination:UNCERTAIN | 3 |
| review-09 | hallucination:FAIL | 3 |
