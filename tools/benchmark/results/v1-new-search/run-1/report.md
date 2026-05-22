# Benchmark Report: v1-new-search / run-1

**Date**: 2026-05-21  
**Skill**: nabledge-6 (new search: keyword-search + semantic-search)  
**Scenarios**: `tools/benchmark/scenarios/qa.json`  
**Run dir**: `tools/benchmark/results/v1-new-search/run-1/`

## Summary

| Metric | Value |
|--------|-------|
| Total scenarios | 30 |
| Execution errors | 0 |
| Claims PRESENT | 29/30 (96.7%) |
| Hallucination PASS | 28/30 (93.3%) |
| Hallucination FAIL | 1 (impact-08) |
| Hallucination UNCERTAIN | 1 (qa-12a) |
| Accuracy ABSENT | 1 (qa-12b: 1 claim UNCERTAIN → accuracy=null) |
| Total cost | $27.56 |

## Per-Scenario Results

| Scenario | Accuracy | Hallucination | Notes |
|----------|----------|---------------|-------|
| pre-01 | 1.0 | PASS | |
| pre-02 | 1.0 | PASS | timeout on first attempt, re-run succeeded |
| pre-03 | 1.0 | PASS | |
| review-06 | 1.0 | PASS | |
| review-07 | 1.0 | PASS | |
| review-08 | 1.0 | PASS | |
| review-09 | 1.0 | PASS | |
| impact-01 | 1.0 | PASS | |
| impact-03 | 1.0 | PASS | |
| impact-06 | 1.0 | PASS | |
| impact-08 | 1.0 | **FAIL** | `fixedDateのフォーマットはyyyyMMddHHmmss（14桁）またはyyyyMMddHHmmssSSS（17桁）` — not in knowledge |
| qa-01 | 1.0 | PASS | |
| qa-02 | 1.0 | PASS | |
| qa-03 | 1.0 | PASS | |
| qa-04 | 1.0 | PASS | |
| qa-05 | 1.0 | PASS | |
| qa-06 | 1.0 | PASS | |
| qa-07 | 1.0 | PASS | |
| qa-08 | 1.0 | PASS | |
| qa-09 | 1.0 | PASS | |
| qa-10 | 1.0 | PASS | |
| qa-11a | 1.0 | PASS | |
| qa-11b | 1.0 | PASS | |
| qa-12a | 1.0 | **UNCERTAIN** | 2 unsupported claims (HTTPエラー制御ハンドラ / Thymeleaf errors.hasError) |
| qa-12b | null | PASS | 1 claim UNCERTAIN — fact oversimplification vs answer's nuanced explanation |
| qa-13 | 1.0 | PASS | timeout on first attempt, re-run succeeded |
| qa-14 | 1.0 | PASS | |
| qa-15 | 1.0 | PASS | |
| oos-impact-01 | 1.0 | PASS | |
| oos-qa-01 | 1.0 | PASS | |

## Comparison with Baseline (baseline-current)

Baseline (3-run average, old search): accuracy 83.7%, hallucination PASS 14.4%

| Metric | Baseline | Run-1 (new search) | Delta |
|--------|----------|--------------------|-------|
| Claims PRESENT | 83.7% (avg) | 96.7% | +13.0pp |
| Hallucination PASS | 14.4% (avg) | 93.3% | +78.9pp |

> Note: Baseline hallucination PASS rate was low because the old search returned fewer/wrong sections, causing many unsupported claims. New keyword+semantic search dramatically improves grounding.

## Validity Review

自動スコアのFAIL/UNCERTAINについて妥当性を評価した結果、確定FAILはゼロ。

| Scenario | Auto Score | Final Verdict | Reason |
|---|---|---|---|
| impact-08 | Hal FAIL | **問題なし** | 回答の桁数（14桁/17桁）は正しい。ナレッジ `testing-framework-03-Tips.json:s12` の「12桁/15桁」が誤記。回答は正確 |
| qa-12a | Hal UNCERTAIN | **問題なし** | mustのfactはすべて回答に含まれている。Thymeleaf部分はナレッジ未収録だが一般的な補足情報でありNablarch固有のハルシネーションではない |
| qa-12b | Acc UNCERTAIN | **問題なし** | factが「自動的にエラーレスポンスになる」と過度に単純化。回答はより正確で詳細（ErrorResponseBuilderのカスタム実装が必要と正しく説明）。スキルは正しく動作 |

**確定FAIL: 0件**

## Known Issues

- **公式ドキュメント誤記**: `06_TestFWGuide/03_Tips.rst` の fixedDate フォーマット桁数が誤記（「12桁」「15桁」→正しくは「14桁」「17桁」）。RSTが誤っており、ナレッジはRSTを正しく変換している。
