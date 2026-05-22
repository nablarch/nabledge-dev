# Benchmark Report: v1-new-search / run-3

**Date**: 2026-05-22  
**Skill**: nabledge-6 (new search: keyword-search + semantic-search)  
**Scenarios**: `tools/benchmark/scenarios/qa.json`  
**Run dir**: `tools/benchmark/results/v1-new-search/run-3/20260522-084759/`

## Summary

| Metric | Value |
|--------|-------|
| Total scenarios | 30 |
| Execution errors | 0 |
| Claims PRESENT | 28/30 (93.3%) |
| Hallucination PASS | 26/30 (86.7%) |
| Hallucination FAIL | 2 (impact-08, qa-05) |
| Hallucination UNCERTAIN | 2 (pre-02, qa-15) |
| Accuracy ABSENT | 1 (qa-12b: 1 claim UNCERTAIN) |
| Accuracy 0.0 | 1 (qa-12a: 1 claim ABSENT) |

## Per-Scenario Results

| Scenario | Accuracy | Hallucination | Notes |
|----------|----------|---------------|-------|
| pre-01 | 1.0 | PASS | |
| pre-02 | 1.0 | **UNCERTAIN** | Thymeleaf errors.hasError/getMessage/allMessages — not in knowledge |
| pre-03 | 1.0 | PASS | |
| review-06 | 1.0 | PASS | |
| review-07 | 1.0 | PASS | |
| review-08 | 1.0 | PASS | |
| review-09 | 1.0 | PASS | |
| impact-01 | 1.0 | PASS | |
| impact-03 | 1.0 | PASS | |
| impact-06 | 1.0 | PASS | |
| impact-08 | 1.0 | **FAIL** | `fixedDateのフォーマットyyyyMMddHHmmss(14桁)/yyyyMMddHHmmssSSS(17桁)` — not in knowledge |
| qa-01 | 1.0 | PASS | |
| qa-02 | 1.0 | PASS | |
| qa-03 | 1.0 | PASS | |
| qa-04 | 1.0 | PASS | |
| qa-05 | 1.0 | **FAIL** | `JaxbBodyConverterがapplication/jsonに対応したコンバータ` — not in knowledge |
| qa-06 | 1.0 | PASS | |
| qa-07 | 1.0 | PASS | |
| qa-08 | 1.0 | PASS | |
| qa-09 | 1.0 | PASS | |
| qa-10 | 1.0 | PASS | |
| qa-11a | 1.0 | PASS | |
| qa-11b | 1.0 | PASS | |
| qa-12a | **0.0** | PASS | 1 claim ABSENT: HttpErrorHandlerがApplicationExceptionをErrorMessagesに変換しリクエストスコープに設定 |
| qa-12b | null | PASS | 1 claim UNCERTAIN — fact oversimplification vs nuanced answer |
| qa-13 | 1.0 | PASS | |
| qa-14 | 1.0 | PASS | |
| qa-15 | 1.0 | **UNCERTAIN** | SecureHandlerのデフォルトヘッダ値（X-XSS-Protection, Referrer-Policy）— not in knowledge |
| oos-impact-01 | 1.0 | PASS | |
| oos-qa-01 | 1.0 | PASS | |

## Validity Review

自動スコアのFAIL/UNCERTAIN/0.0について妥当性を評価した結果、確定FAILは2件。

| Scenario | Auto Score | Final Verdict | Reason |
|---|---|---|---|
| impact-08 | Hal FAIL | **問題なし** | run-1と同じ。RSTの誤記（12桁/15桁）に起因。回答の14桁/17桁が正確 |
| qa-05 | Hal FAIL | **確定FAIL** | JaxbBodyConverterをapplication/json用と説明しているが、ナレッジ（handlers-body-convert-handler.json s4）ではapplication/xml用と明示されており事実誤認 |
| pre-02 | Hal UNCERTAIN | **問題なし** | run-2 qa-12a / run-1 qa-12aと同じThymeleaf補足情報。Nablarch固有のハルシネーションではない |
| qa-15 | Hal UNCERTAIN | **問題なし** | X-XSS-ProtectionとReferrer-Policyのデフォルト値。ナレッジにクラス名はあるがデフォルト値が未記載。補足情報として問題なし |
| qa-12a | Acc 0.0 | **問題なし** | mustの「HttpErrorHandler言及」はpurpose=実装したいに対して過剰。`@InjectForm + @OnError + <n:errors>` で答えるのが正しく、ハンドラ内部動作の説明は不要 |
| qa-12b | Acc null | **問題なし** | run-1/2と同パターン（factの過単純化）。回答品質の問題ではない |

**確定FAIL: 1件（qa-05）**

## Known Issues

- **qa-05 (確定FAIL)**: JaxbBodyConverterをapplication/json用と誤説明。ナレッジ（handlers-body-convert-handler.json:s4）はapplication/xml用と明示。JSON用コンバータの設定例はナレッジ未収録
