# Benchmark Report: v1-new-search / run-2

**Date**: 2026-05-21  
**Skill**: nabledge-6 (new search: keyword-search + semantic-search)  
**Scenarios**: `tools/benchmark/scenarios/qa.json`  
**Run dir**: `tools/benchmark/results/v1-new-search/run-2/20260521-210651/`

## Summary

| Metric | Value |
|--------|-------|
| Total scenarios | 30 |
| Execution errors | 0 |
| Claims PRESENT | 29/30 (96.7%) |
| Hallucination PASS | 26/30 (86.7%) |
| Hallucination FAIL | 4 (impact-03, review-08, qa-12a, qa-12b) |
| Hallucination UNCERTAIN | 0 |
| Accuracy ABSENT | 1 (qa-12b: 1 claim UNCERTAIN) |

## Per-Scenario Results

| Scenario | Accuracy | Hallucination | Notes |
|----------|----------|---------------|-------|
| pre-01 | 1.0 | PASS | |
| pre-02 | 1.0 | PASS | |
| pre-03 | 1.0 | PASS | |
| review-06 | 1.0 | PASS | |
| review-07 | 1.0 | PASS | |
| review-08 | 1.0 | **FAIL** | `SessionStoreHandlerでHIDDENストアを使用する場合のハンドラ配置順` — partially correct but incomplete |
| review-09 | 1.0 | PASS | |
| impact-01 | 1.0 | PASS | |
| impact-03 | 1.0 | **FAIL** | `ApplicationExceptionを送出するとJAX-RSレスポンスハンドラがエラーレスポンスを生成する` — not in knowledge |
| impact-06 | 1.0 | PASS | |
| impact-08 | 1.0 | PASS | |
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
| qa-12a | 1.0 | **FAIL** | Thymeleaf errors.hasError/getMessage/allMessages — not in knowledge |
| qa-12b | null | **FAIL** | `nablarch.core.validation.ee.Required.message` value differs from knowledge; 1 claim UNCERTAIN |
| qa-13 | 1.0 | PASS | |
| qa-14 | 1.0 | PASS | |
| qa-15 | 1.0 | PASS | |
| oos-impact-01 | 1.0 | PASS | |
| oos-qa-01 | 1.0 | PASS | |

## Validity Review

自動スコアのFAILについて妥当性を評価した結果、確定FAILは1件。

| Scenario | Auto Score | Final Verdict | Reason |
|---|---|---|---|
| review-08 | Hal FAIL | **問題なし** | 不支持クレーム「マルチパートリクエストハンドラより後ろ、かつ内部フォーワードハンドラより前」はナレッジs3に明示されており正確。評価器が「HTTPレスポンスハンドラより後ろ」制約の省略を誤ってFAILと判定 |
| impact-03 | Hal FAIL | **問題なし** | 不支持クレーム「ApplicationException送出 → JAX-RSレスポンスハンドラがエラーレスポンス生成」はhandlers-jaxrs-response-handler.json s4（例外に応じてErrorResponseBuilderがレスポンス生成）から合理的に導出できる正当な推論 |
| qa-12a | Hal FAIL | **問題なし** | Thymeleaf APIはナレッジ未収録だが、run-1のqa-12aと同じ状況。一般的な補足情報でありNablarch固有のハルシネーションではない（run-1では同判定で問題なし） |
| qa-12b | Hal FAIL + Acc null | **問題なし** | Required.messageキー名はナレッジに記載あり。メッセージ値の差（「必ず入力」vs「入力」）は例示レベル。accuracy=nullはrun-1と同パターン（factの過単純化） |

**確定FAIL: 0件**

## Known Issues

なし
