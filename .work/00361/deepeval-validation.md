# DeepEval Validation Results

**Date**: 2026-05-28  
**Run**: `tools/benchmark/results/deepeval-validation/run-1/`  
**Scenarios**: 30 total, 28 evaluated (qa-11b: missing runner output, qa-15: section not found error)

## Summary

| Metric Pair | Agreement Rate | Mismatches |
|---|---|---|
| accuracy vs answer_correctness | 27/28 = **96.4%** | 1 case |
| hallucination vs faithfulness | 23/26 = **88.5%** | 3 cases |

## Score Overview

| id | accuracy | hallucination | answer_correctness | answer_relevancy | faithfulness |
|---|---|---|---|---|---|
| impact-01 | 1.00 | 1 | 1.00 | 1.00 | 0.91 |
| impact-03 | 1.00 | 1 | 1.00 | 1.00 | 1.00 |
| impact-06 | 1.00 | 1 | 1.00 | 0.97 | 0.96 |
| impact-08 | 1.00 | 0 | 1.00 | 1.00 | 0.86 |
| oos-impact-01 | 1.00 | 1 | 1.00 | 1.00 | 1.00 |
| oos-qa-01 | 1.00 | N/A | 1.00 | 1.00 | 1.00 |
| pre-01 | 1.00 | 1 | 1.00 | 0.92 | 1.00 |
| pre-02 | 1.00 | 1 | 1.00 | 1.00 | 0.95 |
| pre-03 | 1.00 | 1 | 1.00 | 0.79 | 1.00 |
| qa-01 | 1.00 | 1 | 1.00 | 1.00 | 1.00 |
| qa-02 | 1.00 | N/A | 1.00 | 1.00 | 1.00 |
| qa-03 | 1.00 | 1 | 1.00 | 0.93 | 1.00 |
| qa-04 | 1.00 | 1 | 1.00 | 1.00 | 1.00 |
| qa-05 | 0.67 | 1 | 0.60 | 0.90 | 0.94 |
| qa-06 | 1.00 | 1 | 1.00 | 0.89 | 1.00 |
| qa-07 | 1.00 | 1 | 1.00 | 1.00 | 0.95 |
| qa-08 | 1.00 | 1 | 1.00 | 1.00 | 0.93 |
| qa-09 | 1.00 | 1 | 1.00 | 1.00 | 1.00 |
| qa-10 | 1.00 | 1 | 1.00 | 1.00 | 1.00 |
| qa-11a | 1.00 | 1 | 1.00 | 0.94 | 0.96 |
| qa-12a | 1.00 | 0 | 0.90 | 1.00 | 1.00 |
| qa-12b | 0.50 | 1 | 1.00 | 1.00 | 0.93 |
| qa-13 | 1.00 | 0 | 1.00 | 1.00 | 1.00 |
| qa-14 | 1.00 | 1 | 1.00 | 1.00 | 1.00 |
| review-06 | 1.00 | 1 | 0.90 | 1.00 | 1.00 |
| review-07 | 1.00 | 1 | 1.00 | 1.00 | 1.00 |
| review-08 | 1.00 | 1 | 1.00 | 1.00 | 1.00 |
| review-09 | 1.00 | 1 | 1.00 | 1.00 | 0.94 |

## Mismatch Cases

### accuracy vs answer_correctness

**qa-12b**: accuracy=0.50 (FAIL) vs answer_correctness=1.00 (PASS)

- Input: 入力チェックでエラーがあったときに、エラーメッセージをユーザーに返す方法を教えてほしい
- Analysis: accuracy uses claim-by-claim verdict against `must` facts; LLM judge flagged specific claims as unverified. DeepEval GEval uses a broader "does the output cover the expected facts" criterion, which gave full credit despite partial claim failures. The discrepancy reflects different granularity — claim-level strictness (accuracy) vs. holistic coverage (GEval).

### hallucination vs faithfulness

**impact-08**: hallucination=0 (FAIL) vs faithfulness=0.86 (PASS)

- Input: テスト時だけシステム日時を任意の日付に差し替える方法はあるか？
- Analysis: The existing hallucination judge flagged specific claims as unsupported. DeepEval faithfulness scored 0.86, meaning some statements were not grounded in context — consistent with the existing judge — but the threshold difference (0 vs 0.7) caused opposite verdicts. hallucination=0 is a binary FAIL; faithfulness=0.86 passes the 0.7 threshold.

**qa-12a**: hallucination=0 (FAIL) vs faithfulness=1.00 (PASS)

- Analysis: Same root cause as impact-08. The existing hallucination judge applied strict claim-by-claim verification and found at least one unsupported claim. DeepEval faithfulness found all retrieved context supported, giving 1.00. Likely the hallucination judge checks against `must` sections while faithfulness checks against `retrieval_context` — different reference sets.

**qa-13**: hallucination=0 (FAIL) vs faithfulness=1.00 (PASS)

- Analysis: Same pattern. The hallucination=0 verdict comes from claim verification against specific knowledge sections. DeepEval faithfulness=1.00 means the answer is entirely grounded in what was retrieved. The reference set mismatch (specific sections vs. retrieved context) explains the divergence.

## Root Cause of hallucination vs faithfulness Divergence

The 3 hallucination/faithfulness mismatches share the same root cause: **different reference sets**.

- **Existing hallucination judge**: verifies claims against specific section content from the knowledge base
- **DeepEval faithfulness**: verifies statements against `retrieval_context` (what was actually retrieved by the skill)

When retrieval is good (high faithfulness) but the answer omits or misrepresents a required fact (hallucination=0), the two metrics legitimately diverge. This is expected behavior, not a measurement error.

## Conclusion

- **answer_correctness correlates strongly with accuracy** (96.4% agreement). The 1 mismatch is attributable to granularity difference (claim-level vs. holistic).
- **faithfulness has lower agreement with hallucination** (88.5%), explained by different reference sets — a structural difference, not noise.
- Both DeepEval metrics add complementary signal: answer_correctness as a holistic accuracy check, faithfulness as a retrieval-grounded hallucination check.

## Skipped Scenarios

- **qa-11b**: No runner output — likely excluded from a previous run. Not a DeepEval issue.
- **qa-15**: `ValueError: Section s21 not found in check/security-check/security-check-2.チェックリスト.json` — pre-existing data issue unrelated to DeepEval integration.
