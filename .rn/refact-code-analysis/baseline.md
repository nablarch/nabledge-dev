# Baseline — code-analysis workflow (current 685-line file)

**Date**: 2026-07-03  
**Results dir**: `tools/benchmark/results/20260701-1736-code-analysis-baseline/`  
**Workflow**: `.claude/skills/nabledge-6/workflows/code-analysis.md` (685 lines, unmodified)

## Score Summary

| Scenario | answer_correctness | answer_relevancy | faithfulness | format_check |
|----------|-------------------|------------------|--------------|--------------|
| ca-01    | 0.30              | 0.96             | 1.00         | PASS         |
| ca-02    | 1.00              | 0.99             | 1.00         | PASS         |
| ca-03    | 1.00              | 0.97             | 1.00         | PASS         |

## Notes

- ca-01 (ProjectAction): `answer_correctness` は 0.30 — JAX-RS アノテーション (`@Path("/projects")`) と `ValidatorUtil.validate()` の2事実が欠落または誤記述。Nablarch Web フレームワーク実装として誤認識された。
- ca-02 (AuthenticationAction): 全スコア高水準。
- ca-03: 全スコア高水準。
- 全シナリオで format check PASS（placeholder なし、全7セクション存在、Mermaid 両図あり）。

## Acceptance Criterion for Task #6

Task #6 の検証条件：全シナリオの DeepEval スコアがこのベースライン以上であること。

| Scenario | answer_correctness ≥ | answer_relevancy ≥ | faithfulness ≥ |
|----------|---------------------|-------------------|---------------|
| ca-01    | 0.30                | 0.96              | 1.00          |
| ca-02    | 1.00                | 0.99              | 1.00          |
| ca-03    | 1.00                | 0.97              | 1.00          |
