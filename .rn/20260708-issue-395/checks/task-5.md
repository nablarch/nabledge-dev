# Self-check: Task #5 — v6 full benchmark

## QA フルベンチマーク (3 run)

- Results: `tools/benchmark/results/20260708-1153-section-links-v6/`
- crossrun-summary: 全シナリオ CLEAN / CONSISTENT
- quality-report: 実害ありの閾値割れ 0 件
- 判定: **OK**

## code-analysis フルベンチマーク

- Results: `tools/benchmark/results/20260709-code-analysis-section-links-v6/`
- Baseline: `tools/benchmark/results/20260701-1736-code-analysis-baseline/`

| シナリオ | correctness (新) | correctness (baseline) | regression |
|---|---|---|---|
| ca-01 | 1.000 | 0.300 | なし（改善） |
| ca-02 | 1.000 | 1.000 | なし |
| ca-03 | 1.000 | 1.000 | なし |

- faithfulness: 全件 1.00（推測・捏造ゼロ）
- REGRESSION DETECTED: なし
- 判定: **OK**

## 完了基準チェック

- [x] v6 QA フルベンチ crossrun-summary の全シナリオ pass rate がベースラインを下回っていない
- [x] v6 code-analysis フルベンチに新たな REGRESSION DETECTED がない
- [x] QA quality-report で実害ありの閾値割れシナリオが 0 件

**総合判定: OK**
