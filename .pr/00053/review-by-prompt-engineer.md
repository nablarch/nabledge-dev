# Expert Review: Prompt Engineer

**Date**: 2026-02-20
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 2 files + 5 documentation files

## Overall Assessment

**Rating**: 4.5/5 - Excellent workflow clarity with minor improvement opportunities

**Summary**: The unified index search implementation demonstrates excellent prompt engineering principles. The workflow is clear, complete, and provides strong guidance for agent behavior. The single-stage approach significantly simplifies instructions while maintaining precision. Documentation is comprehensive with well-structured examples. Minor improvements could enhance error handling clarity and example diversity.

## Detailed Ratings

| Aspect | Rating | Notes |
|--------|--------|-------|
| **Overall workflow clarity** | 5/5 | Exceptionally clear structure with logical flow |
| **Instruction completeness** | 4/5 | Missing minor edge case handling details |
| **Agent behavior guidance** | 5/5 | Precise tool usage and decision criteria |
| **Example quality** | 4/5 | Good examples but could use more diversity |

## Key Issues

### High Priority

None identified. The workflow is production-ready.

### Medium Priority

#### M1: Error handling for section-judgement failures could be more explicit

**Description**: Line 109 states "DO NOT answer from LLM training data" but doesn't specify whether the agent should list available categories or suggest alternative search strategies.

**Current text** (lines 109-110):
```markdown
**Section-judgement returns no results**: State "この情報は知識ファイルに含まれていません", show available knowledge from index.toon. DO NOT answer from LLM training data.
```

**Suggestion**: Add explicit guidance on what "show available knowledge" means:
```markdown
**Section-judgement returns no results**:
1. State "この情報は知識ファイルに含まれていません"
2. List 3-5 related knowledge categories from index.toon that partially matched keywords
3. Suggest the user rephrase their question or check the official Nablarch documentation
4. DO NOT answer from LLM training data under any circumstances
```

**Reasoning**: More explicit steps prevent ambiguity in agent behavior during edge cases.

#### M2: Keyword extraction guidance could include boundary cases

**Description**: Lines 42-51 provide excellent examples of keyword extraction at three levels, but don't address what to do when user queries are very broad ("Nablarchについて") or very specific with no clear category ("バグ修正").

**Current approach**: Shows ideal example but no guidance for edge cases.

**Suggestion**: Add a subsection after line 51:

```markdown
**Edge cases**:
- **Very broad queries** (e.g., "Nablarchについて"): Extract general L1 terms only, inform user that query is too broad, suggest specific areas (データベース, バッチ, Web, etc.)
- **Very specific queries** (e.g., "この特定のバグ"): Extract any technical terms present, proceed with search, let section-judgement filter results
- **No obvious keywords** (e.g., "これの使い方"): Ask user to clarify what "これ" refers to before proceeding
```

**Reasoning**: Edge case handling prevents agent from getting stuck or making poor assumptions.

#### M3: Example execution could show failed scenarios

**Description**: Lines 111-129 provide an excellent successful search example, but no example of what happens when no results are found or too many candidates match.

**Suggestion**: Add a failed search example after line 129:

```markdown
### Example: No Results Found

**Request**: "量子コンピューティング統合" (quantum computing integration)

**Extract keywords**:
- L1: ["量子", "quantum"]
- L2: ["量子プロセッサ"]
- L3: ["統合", "integration"]

**Step 1**: Match against section-level index.toon
- No sections with score ≥2 found

**Error handling**:
- Message: "この情報は知識ファイルに含まれていません。Nablarchは量子コンピューティングをサポートしていません。"
- Show available categories: "利用可能な知識領域: データベースアクセス, バッチ処理, Web開発, REST API, テスト..."
```

**Reasoning**: Failed scenarios help agents understand expected error handling behavior.

### Low Priority

#### L1: Scoring strategy table formatting

**Description**: Lines 140-142 present a scoring strategy rationale table, but it only has one row (section selection). The table format suggests there should be multiple stages, which no longer exist.

**Current format**:
```markdown
| Stage | L1 Weight | L2 Weight | L3 Weight | Rationale |
|-------|-----------|-----------|-----------|-----------|
| **Section selection** | 0 | +2 | +2 | L2/L3 identify specific technology/function (equal importance). L1 too broad for section-level. |
```

**Suggestion**: Convert to a simpler format since there's only one stage now:

```markdown
**Scoring strategy for section selection**:
- **L1 (Technical domain)**: 0 points - Too broad for section-level discrimination
- **L2 (Technical component)**: +2 points per hint - Identifies specific technology (e.g., "DAO", "Handler")
- **L3 (Functional)**: +2 points per hint - Identifies specific function (e.g., "ページング", "commit")
- **Rationale**: At section level, both technical components and specific functions are equally discriminative. Equal weighting ensures balanced matching.
```

**Reasoning**: Simpler format is clearer for single-stage workflow.

#### L2: Grep tool usage is marked optional but not explained

**Description**: Line 27 mentions "Grep tool (optional)" but doesn't specify when to use Grep vs Read, or what to grep for.

**Current text**:
```markdown
**Tools you will use**:
- Read tool: Read knowledge/index.toon
- Grep tool (optional): Search for keywords in index.toon
```

**Suggestion**: Clarify usage scenario:
```markdown
**Tools you will use**:
- Read tool: Read knowledge/index.toon (primary method - index is small, 147 lines)
- Grep tool (optional): Quick pre-check if specific keyword exists before full read (rarely needed)
```

**Reasoning**: Reduces ambiguity about when to use optional tools.

#### L3: Output format example could be more complete

**Description**: Lines 75-91 show a detailed output format with score breakdown, then line 93 mentions a "simplified format" but doesn't show it.

**Current text** (line 93):
```markdown
**Note**: The detailed score breakdown is optional for section-judgement. A simplified format with just `matched_hints: ["DAO", "ページング", "per", "page"]` is also acceptable.
```

**Suggestion**: Show both formats explicitly:

```markdown
**Output formats** (both acceptable for section-judgement):

**Detailed format** (preferred for debugging):
```json
{
  "candidates": [
    {
      "file_path": "features/libraries/universal-dao.json",
      "section": "paging",
      "score": 8,
      "matched_hints": [
        {"hint": "DAO", "level": "L2", "points": 2},
        {"hint": "ページング", "level": "L3", "points": 2}
      ]
    }
  ]
}
```

**Simplified format** (faster, sufficient for section-judgement):
```json
{
  "candidates": [
    {
      "file_path": "features/libraries/universal-dao.json",
      "section": "paging",
      "score": 8,
      "matched_hints": ["DAO", "ページング", "per", "page"]
    }
  ]
}
```
```

**Reasoning**: Showing both formats helps agents choose appropriately based on context.

## Positive Aspects

### Excellent Workflow Structure

1. **Clear Table of Contents** (lines 5-13): Hierarchical structure makes navigation easy
2. **Who/What/Why sections** (lines 15-32): Answers key questions upfront - who executes, what inputs/outputs, what tools are needed
3. **Expected metrics** (lines 29-31): Concrete expectations (1-2 tool calls, 20-30 candidates) help agents self-assess
4. **Step-by-step process** (lines 33-102): Logical flow from keyword extraction to result passing

### Precise Tool Usage Guidance

1. **Tool specification** (lines 26-27, 37-39): Clear tool names with purpose
2. **Critical instructions** (line 52): Uses **CRITICAL** marker for mandatory behavior (include Japanese/English terms)
3. **Action verbs** (lines 39, 54): Precise verbs like "Extract", "Read", "Match", "Sort", "Select"

### Excellent Scoring Strategy Documentation

1. **Three-level keyword extraction** (lines 42-50): Clear categorization with examples
2. **Weighted scoring with rationale** (lines 54-67): Exact point values with reasoning
3. **Deterministic approach** (lines 144-148): Explicitly states why weighted scoring was chosen (deterministic, flexible, debuggable)
4. **Performance metrics** (line 148): Concrete improvement numbers (58% faster)

### Strong Example Quality

1. **Realistic query** (line 113): "ページングを実装したい" is a typical developer question
2. **Complete walkthrough** (lines 115-128): Shows every step from keyword extraction to final result
3. **Score calculation** (lines 121-124): Explicit point breakdown helps agents verify their understanding

### Clear Error Handling

1. **Three error scenarios** (lines 103-109): No matches, too many candidates, no results from judgement
2. **Specific actions** (line 107): "Select sections with 2+ matched hints, limit to top 30"
3. **User-facing messages** (line 109): Japanese message template provided

### Comprehensive Notes Section

1. **Comparison with complementary search** (line 133): Explains how keyword search relates to intent-search
2. **Rationale table** (lines 138-142): Summarizes scoring strategy design decisions
3. **Performance analysis** (lines 144-151): Explains why the approach is faster and more maintainable

## Recommendations

### For Immediate Implementation

1. **Enhance error handling** (M1): Add explicit steps for "show available knowledge"
2. **Add edge case guidance** (M2): Handle very broad, very specific, and unclear queries
3. **Include failed example** (M3): Show what happens when no results found

### For Future Improvements

1. **Multi-language support**: Currently assumes Japanese users, could generalize for English
2. **Scoring threshold tuning**: Monitor real-world usage to see if ≥2 threshold is optimal
3. **Hint quality metrics**: Consider adding hint effectiveness scoring based on usage patterns

### Process Improvements

1. **A/B testing framework**: Compare keyword-search vs intent-search performance
2. **Feedback loop**: Collect section-judgement filtering patterns to improve hint selection
3. **Documentation alignment**: Ensure hints in knowledge files match actual section content

## Index File Review (index.toon)

### Structure Quality: 5/5

- Clear header comment with format specification (line 3)
- Consistent format: `file.json#section_id, hint1 hint2 ...`
- All 147 entries follow identical structure
- Sorted by file (security → slf4j → data-read-handler → ...)

### Hint Quality: 4/5

**Strengths**:
- Bilingual hints (Japanese and English)
- Technical terms in context (e.g., "ページング per page Pagination EntityList 件数取得")
- Specific enough for discrimination (e.g., "SQLインジェクション OSコマンドインジェクション パストラバーサル")

**Minor issue**: Some sections have very few hints (e.g., line 145: "動作環境 APサーバ データベース OS") while others are very detailed. This could affect ranking consistency.

**Suggestion**: Consider adding a minimum of 5-7 hints per section, or document why some sections have fewer hints.

## Conclusion

This is an **excellent example of prompt engineering** with clear instructions, precise tool guidance, and comprehensive documentation. The unified index search approach significantly simplifies the workflow while maintaining accuracy and performance.

The workflow is production-ready with only minor improvements recommended for edge case handling and example diversity. The implementation demonstrates strong understanding of agent behavior guidance principles: deterministic scoring, explicit tool usage, clear error handling, and comprehensive examples.

**Recommended Action**: Implement Medium-priority improvements (M1-M3) to enhance robustness, then proceed with production deployment.

---

## Files Reviewed

### Modified
- `.claude/skills/nabledge-6/workflows/keyword-search.md` (Workflow definition)
- `.claude/skills/nabledge-6/knowledge/index.toon` (Section-level index)

### Documentation
- `.pr/00053/SUMMARY.md` (Implementation summary)
- `.pr/00053/notes.md` (Design decisions)
- `.pr/00053/verification.md` (Before/after comparison)
- `.pr/00053/test-results.md` (Test validation - 3 queries, all passed)
- `.pr/00053/regenerate-index.sh` (Maintenance automation)
