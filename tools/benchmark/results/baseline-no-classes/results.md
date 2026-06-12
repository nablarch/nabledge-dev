# Baseline: classes.md なし (origin/main semantic-search)

**実行日**: 2026-06-12  
**条件**: classes.md なし、origin/main の semantic-search.md  
**目的**: classes.md 導入前のベースライン（qa-05 / qa-19 各 10 回）

---

## qa-05（purpose: 実装したい）

must: Formクラス / String型の2ファクト

| run | adapter_page | s2到達 | correctness |
|-----|:---:|:---:|:---:|
| run-01 | ✗ | ✗ | 1.0 |
| run-02 | ✗ | ✗ | 1.0 |
| run-03 | ✗ | ✗ | 1.0 |
| run-04 | ✗ | ✗ | 1.0 |
| run-05 | ✓ | ✗ | 1.0 |
| run-06 | ✗ | ✗ | 1.0 |
| run-07 | ✗ | ✗ | 1.0 |
| run-08 | ✗ | ✗ | 1.0 |
| run-09 | ✗ | ✗ | 1.0 |
| run-10 | ✗ | ✗ | 1.0 |
| **集計** | **1/10** | **0/10** | **avg 1.000** |

---

## qa-19（purpose: 仕組み・動作を理解したい）

must: JSONのボディ変換はJackson2BodyConverterが担当する（adapters-jaxrs-adaptor.json:s2）

| run | adapter_page | s2到達 | correctness |
|-----|:---:|:---:|:---:|
| run-01 | ✗ | ✗ | 0.1 |
| run-02 | ✗ | ✗ | 0.0 |
| run-03 | ✓ | ✓ | 0.8 |
| run-04 | ✗ | ✗ | 0.3 |
| run-05 | ✗ | ✗ | 0.0 |
| run-06 | ✗ | ✗ | 0.0 |
| run-07 | ✗ | ✗ | 0.0 |
| run-08 | ✗ | ✗ | 0.1 |
| run-09 | ✗ | ✗ | 0.0 |
| run-10 | ✗ | ✗ | 0.0 |
| **集計** | **1/10** | **1/10** | **avg 0.130** |
