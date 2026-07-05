# シナリオ別スコアサマリー（リライト後検証）

run数: 1 / シナリオ数: 3

## スコアサマリー

| 指標 | 平均 | ベースライン比 |
|---|---|---|
| answer_correctness | 1.000 | +0.233 |
| answer_relevancy | 0.961 | -0.011 |
| faithfulness | 1.000 | 0.000 |

## シナリオ別スコア

| scenario | input | correctness | relevancy | faithfulness |
|---|---|---|---|---|
| ca-01 | ProjectAction | 1.000 | 0.974 | 1.000 |
| ca-02 | AuthenticationAction | 1.000 | 0.989 | 1.000 |
| ca-03 | ImportZipCodeFileAction | 1.000 | 0.918 | 1.000 |

## ベースラインとの差分

| scenario | correctness Δ | relevancy Δ | faithfulness Δ |
|---|---|---|---|
| ca-01 | **+0.700** | +0.014 | 0.000 |
| ca-02 | 0.000 | +0.001 | 0.000 |
| ca-03 | 0.000 | -0.050 | 0.000 |

## パフォーマンス集約

| メトリクス | 平均 | P50 | 最大 |
|---|---|---|---|
| 実行時間 | 220s | 227s | 233s |
| コスト | $1.110 | $1.063 | $1.197 |
