# Expert Review: Prompt Engineer (Answer Generation)

**Date**: 2026-05-15
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 2 files

## Summary

2 Findings — fixed

## Findings

1. **answer.md step ordering: trace before answer creates constraint inversion**
   - Violated clause: Design doc §answer.md 処理手順 step 3→4 ordering (identify information → generate answer)
   - Description: Steps instructed trace (step 4) before answer (step 5), but trace's `mapped_to` field requires knowing the answer structure. This forces the LLM to mentally generate the answer while filling trace, degrading reliability.
   - Fix: Reordered to answer (step 4) → trace (step 5). Reframed trace instruction as "生成した回答を振り返り".

2. **verify.md `evidence` field for `supported: false` claims is unspecified**
   - Violated clause: Design doc §verify.md 出力 schema requires `evidence` on every claim entry
   - Description: No instruction for what value to use when `supported: false`. LLM could output "なし", empty string, omit field, or fabricate a reference.
   - Fix: Added explicit `evidence: ""（空文字）` instruction in 検証基準 step 3 and output spec.

## Observations

- Token budget (500/800) may be ambiguous whether it covers trace output. Consider clarifying "answerフィールドのみ".
- `hearing_answer` input section lacks "(あれば)" qualifier, though code handles None case.
- Design doc's `general_knowledge` evidence value never appears in practice since verify.md excludes general claims from extraction.

## Positive Aspects

- Two-prompt separation (generate then verify) is sound design
- verify.md's 境界ルール is unambiguous and correctly closes the plausible-inference hallucination escape hatch
- Trace's `extracted: 原文そのまま転記` forces explicit section-level accounting
- answer.md and verify.md are consistent on the general knowledge boundary (回答ルール ↔ 抽出対象外)

## Files Reviewed

- tools/benchmark/prompts/answer.md (prompt)
- tools/benchmark/prompts/verify.md (prompt)
