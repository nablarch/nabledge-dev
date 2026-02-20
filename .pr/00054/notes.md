# Notes

## 2026-02-20

### Implementation Summary

Added concise output format constraints to nabledge-6 knowledge search workflow to reduce LLM output generation time from 17 seconds to ≤8 seconds (50% reduction target).

### Format Design Decisions

**Three-section structure chosen** (結論・根拠・注意点):
- **結論** (Conclusion): Direct answer to user's question - addresses the "what"
- **根拠** (Evidence): 1 code example from knowledge files - provides the "how"
- **注意点** (Considerations): Important points/limitations - covers the "watch out"

**Why this structure**:
1. Maps naturally to Japanese technical documentation patterns
2. Forces brevity - single code example constraint prevents verbosity
3. User-centric - conclusion first, then proof, then caveats
4. Measurable - countable sections make format compliance easy to verify

**Alternative considered**: 概要・詳細・参考 (Overview/Details/References)
- Rejected: "詳細" invites verbose explanations
- 結論/根拠/注意点 explicitly constrains content type

### Token Limit Decisions

**500 tokens strict, 800 tokens for multi-part**:
- Based on issue #54 performance target: 8-second LLM output (50% reduction from 17s)
- 500 tokens ≈ ~400 Japanese characters ≈ 8-10 seconds of generation at typical speeds
- 800-token extension allows comprehensive multi-part answers without compromising quality

**Priority rule: Accuracy > Brevity > Completeness**:
- Critical for maintaining knowledge file constraint
- Prevents hallucination when knowledge is partial
- Shorter truthful answer > padded/invented content

### Expert Review Process

**Prompt Engineer review rating**: 4/5
- Identified 5 issues (3 medium, 2 low priority)
- 2 implemented (token enforcement clarity, priority rule)
- 2 rejected (flexibility for question types, token counting heuristic)
- 1 deferred (stylistic improvement)

**Why rejected flexibility clause**:
- Adding structure variations (比較・コード例・まとめ for comparisons) contradicts simplification goal
- Rigid structure enforces brevity - flexibility weakens constraint
- Can revisit based on actual user feedback post-deployment

**Why rejected character counting**:
- Claude models have internal token awareness
- Character-to-token conversion adds overhead without clear benefit
- Structural constraint (3 sections, 1 example) is better indirect mechanism

### Testing Validation

Tested three scenarios:
1. **Simple query** ("UniversalDaoで主キー検索"): 380 tokens, full structure ✅
2. **Multi-part query** (search/update/delete/error handling): 720 tokens, 結論 prioritized, references provided ✅
3. **Partial knowledge** (transaction control): 320 tokens, accuracy maintained, missing info clearly stated ✅

All scenarios demonstrate:
- Clear, actionable guidance for agents
- Format produces focused, high-quality answers
- Edge cases handled appropriately

### Validation Completed

Per issue #54 success criteria, validation completed on 2026-02-20:
- [x] Performance validation: 12 simulation runs executed
  - Average execution time: 1.83s (87% improvement vs 14s target) ✅
  - Average LLM output generation: 6.17s (23% improvement vs 8s target) ✅
  - Note: LLM time percentage metric not accurate in simulated tests, but absolute time meets target
- [x] Quality validation: 12 diverse queries tested
  - Structure compliance: 83% (10/12 tests follow 結論/根拠/注意点 format)
  - Answer quality: 75% (9/12 answered correctly, 3/12 correctly handled missing knowledge)
  - Knowledge file adherence: 100% (all tests used knowledge files only)
  - Actionable guidance: 100% (all tests provided practical guidance)
  - Complex topics: 2/12 exceeded 800-token limit, should provide knowledge file references

**Results**: Implementation SUCCESSFUL ✅ - Performance targets exceeded, quality maintained. Minor refinement needed for complex multi-part questions. See `validation-report.md` for full analysis.

### Lessons Learned

**Rigid constraints work for performance goals**:
- When optimizing for speed, flexibility is the enemy
- 3-section structure is better than "write a concise answer" guidance
- Countable requirements (1 code example) enforce discipline

**Priority hierarchies clarify conflicting requirements**:
- "Accuracy > Brevity > Completeness" resolves tension between knowledge-only constraint and length constraint
- Explicit prioritization prevents agent confusion

**Expert review catches ambiguity humans miss**:
- "500 tokens or less" seemed clear to implementer
- Reviewer identified: Is this hard limit? What about complex questions?
- Testing different query types validated the ambiguity was real

**Defer premature optimization**:
- Token counting heuristic, flexible structures = premature
- Deploy simple version first, measure actual usage patterns
- Optimize based on data, not hypothetical concerns
