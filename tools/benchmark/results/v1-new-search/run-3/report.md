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

## Known Issues

- **impact-08 FAIL**: `fixedDate` フォーマット文字列がナレッジ未収録（run-1でも同様）
- **qa-05 FAIL**: JaxbBodyConverterがapplication/jsonコンバータという記述がナレッジセクションに未収録
- **pre-02 UNCERTAIN / qa-12a 0.0**: Thymeleaf関連のエラー表示API / HttpErrorHandlerの動作詳細がナレッジ未収録（qa-12aはrun-2でHal FAILだったが今回はaccuracy ABSENT）
- **qa-15 UNCERTAIN**: SecureHandlerのデフォルトヘッダ値がナレッジセクションに明示なし
- **qa-12b null accuracy**: Factのovershimplificationによる（回答品質の問題ではない）
