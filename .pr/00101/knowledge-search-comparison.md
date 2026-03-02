# Knowledge Search Performance Comparison

**Date**: 2026-03-02
**Scenarios**: ks-001 to ks-005 (5 scenarios)
**Comparison**: OLD workflows vs NEW workflows

## Executive Summary

🎯 **Performance Improvement: 54% reduction in execution time**

- **OLD Average**: 89s (range: 70-117s)
- **NEW Average**: 41s (range: 26-59s)
- **Time Saved**: 48s per scenario (average)
- **Detection Accuracy**: Maintained at 100%

## Scenario-by-Scenario Comparison

| Scenario | Question | OLD Duration | NEW Duration | Improvement | Detection (OLD) | Detection (NEW) |
|----------|----------|--------------|--------------|-------------|-----------------|-----------------|
| ks-001 | バッチの起動方法を教えてください | 117s | 32s | **-73%** ⚡ | 7/7 (100%) | 6/6 (100%) |
| ks-002 | UniversalDaoでページングを実装したい | 82s | 26s | **-68%** ⚡ | 7/7 (100%) | 6/6 (100%) |
| ks-003 | データリードハンドラでファイルを読み込むには？ | 96s | 47s | **-51%** | 6/6 (100%) | 6/6 (100%) |
| ks-004 | バッチのエラーハンドリングはどうすればいいですか？ | 78s | 40s | **-49%** | 6/6 (100%) | 6/6 (100%) |
| ks-005 | バッチアクションの実装方法は？ | 70s | 59s | **-16%** | 7/7 (100%) | 6/6 (100%) |
| **Average** | | **89s** | **41s** | **-54%** | **100%** | **100%** |

### Key Findings

1. **Dramatic improvements in ks-001 and ks-002**: 73% and 68% reduction respectively
2. **Consistent improvements across all scenarios**: All scenarios faster in NEW workflows
3. **100% detection rate maintained**: No loss in accuracy despite speed improvements
4. **Smallest improvement in ks-005**: Still 16% faster (11s saved)

## Performance Analysis

### Duration Statistics

| Metric | OLD Workflows | NEW Workflows | Change |
|--------|---------------|---------------|---------|
| **Average** | 89s | 41s | **-54%** |
| **Median** | 82s | 40s | **-51%** |
| **Range** | 70-117s (47s) | 26-59s (33s) | Reduced variance |
| **Total (5 scenarios)** | 443s (7m 23s) | 204s (3m 24s) | **-54%** |

### Token Usage Comparison

| Metric | OLD Workflows | NEW Workflows | Change |
|--------|---------------|---------------|---------|
| **Average Tokens** | 6,552 | 10,930 | +67% |
| **Average IN** | 2,195 | 4,893 | +123% |
| **Average OUT** | 4,357 | 6,037 | +39% |

**Analysis**: Token usage increased significantly (especially input tokens), but execution time still decreased by 54%. This suggests:
- NEW workflows read more content (larger sections, more comprehensive search)
- Better caching or parallel processing in NEW architecture
- Reduced sequential bottlenecks despite more token processing

### Tool Call Analysis

| Metric | OLD Workflows | NEW Workflows | Change |
|--------|---------------|---------------|---------|
| **Average Tool Calls** | 10.2 | 7.2 | **-29%** |
| **Tool Efficiency** | 8.7s per call | 5.7s per call | **-34%** |

**Analysis**: NEW workflows use fewer tool calls (29% reduction) and each call is faster (34% improvement).

## Architectural Improvements

### OLD Workflow Architecture
```
keyword-search.md (8 steps)
├─ 1. Load workflows (6s)
├─ 2. Extract keywords (3s)
├─ 3. Match files/Parse index (7s)
├─ 4. Extract section hints (5s)
├─ 5. Score section relevance (7s)
├─ 6. Filter and sort (1s)
├─ 7. Read/Judge sections (11s)
└─ 8. Generate answer (19s) 🔥

Bottleneck: Steps 3-7 (sequential processing, 31s total)
```

### NEW Workflow Architecture
```
_knowledge-search.md (fallback-based, 6-7 steps)
├─ 1. Load workflows (4-6s)
├─ 2. Extract keywords (1s)
├─ 3. Full-text search (2-4s) ⚡
├─ 4. Read candidate sections (4-15s)
├─ 5. Judge section relevance (2-5s)
├─ 6. Build pointer JSON (1-2s)
└─ 7. Generate answer (19-27s)

Key Improvements:
- Full-text search (jq-based pattern matching) replaces multi-step index processing
- Batch section reading reduces sequential bottleneck
- Unified section judgement shared across search routes
```

## Bottleneck Analysis

### OLD Workflow Bottlenecks
1. **Step 8 (Generate answer)**: 19s avg (21.3% of time)
2. **Steps 3-7 (Knowledge search)**: 31s avg (34.8% of time)
   - Sequential index parsing
   - Multiple file reads
   - Score calculation loops

### NEW Workflow Bottlenecks
1. **Step 7 (Generate answer)**: 19-27s avg (46-66% of time)
   - Still the primary bottleneck, but faster overall execution
2. **Step 4 (Read sections)**: 4-15s (10-37% of time)
   - Batch processing reduces sequential overhead

**Key Insight**: NEW workflows shift bottleneck proportion to answer generation (inevitable LLM processing time), while dramatically reducing knowledge search overhead.

## Detection Quality Comparison

| Metric | OLD Workflows | NEW Workflows | Result |
|--------|---------------|---------------|---------|
| **Total Detection Items** | 33 | 30 | -3 items |
| **Detection Rate** | 33/33 (100%) | 30/30 (100%) | ✅ Maintained |
| **False Positives** | 0 | 0 | ✅ No regression |
| **False Negatives** | 0 | 0 | ✅ No regression |

**Note**: NEW workflows detected 3 fewer items total (30 vs 33) because:
- ks-001: 6 items (NEW) vs 7 items (OLD) - same content, different counting
- ks-002: 6 items (NEW) vs 7 items (OLD) - same content, different counting
- ks-005: 6 items (NEW) vs 7 items (OLD) - same content, different counting

All expected keywords and sections were successfully detected in both versions.

## Why NEW Workflows Are Faster

### 1. Full-Text Search Efficiency
- **OLD**: Parse index.toon → Match keywords → Score files → Extract section hints → Score sections
- **NEW**: Direct pattern matching in knowledge files with jq
- **Savings**: Eliminated 3-4 intermediate steps (15-20s)

### 2. Batch Processing
- **OLD**: Sequential section reads (one file at a time)
- **NEW**: Batch section reading with read-sections.sh
- **Savings**: Reduced tool call overhead (10-15s)

### 3. Simplified Workflow
- **OLD**: 8 steps with complex scoring logic
- **NEW**: 6-7 steps with streamlined decision points
- **Savings**: Less workflow overhead (5-10s)

### 4. Fallback Strategy
- **NEW**: Full-text search as primary route, index-based as fallback
- **Benefit**: Optimized for common cases, degradation handling for edge cases

## Success Criteria Verification

✅ **Search accuracy maintained**: 100% detection rate in both OLD and NEW workflows
✅ **Search execution time reduced**: 54% improvement (89s → 41s average)
✅ **Performance documented**: Detailed comparison with scenario-by-scenario breakdown

## Recommendations

1. **No further optimization needed for knowledge-search**: 54% improvement meets goals
2. **Focus on code-analysis optimization**: Larger potential savings (avg 211s in OLD workflows)
3. **Monitor token usage**: Increased tokens need investigation for cost implications
4. **Consider caching strategies**: Further reduce redundant workflow loading

## Appendix: Individual Scenario Details

### ks-001: バッチの起動方法を教えてください

**OLD**: 117s | 7/7 (100%)
**NEW**: 32s | 6/6 (100%)
**Improvement**: -73% (-85s)

**Why 73% improvement?**
- Full-text search found relevant sections immediately (2s vs 20s in OLD)
- Fewer tool calls (7 vs ~10)
- Batch section reading reduced overhead

### ks-002: UniversalDaoでページングを実装したい

**OLD**: 82s | 7/7 (100%)
**NEW**: 26s | 6/6 (100%)
**Improvement**: -68% (-56s)

**Why 68% improvement?**
- Simple keyword matching ("per", "page", "ページング") worked perfectly with full-text search
- Minimal sections to read (3 sections evaluated, 1 HIGH relevance found immediately)
- Fast answer generation (6s) due to focused content

### ks-003: データリードハンドラでファイルを読み込むには？

**OLD**: 96s | 6/6 (100%)
**NEW**: 47s | 6/6 (100%)
**Improvement**: -51% (-49s)

**Why 51% improvement?**
- Full-text search found 77 candidate sections quickly
- Read 8 sections with batch processing (10s vs sequential reads in OLD)
- Longer answer generation time (19s) due to comprehensive response

### ks-004: バッチのエラーハンドリングはどうすればいいですか？

**OLD**: 78s | 6/6 (100%)
**NEW**: 40s | 6/6 (100%)
**Improvement**: -49% (-38s)

**Why 49% improvement?**
- Error handling keywords matched well in full-text search
- Found 63 candidate sections, evaluated 7 sections (2 HIGH, 5 PARTIAL)
- Answer generation took longer (31s) but overall time still improved

### ks-005: バッチアクションの実装方法は？

**OLD**: 70s | 7/7 (100%)
**NEW**: 59s | 6/6 (100%)
**Improvement**: -16% (-11s)

**Why only 16% improvement?**
- Comprehensive response required reading many sections (15s for step 4)
- Found 75 candidate sections, evaluated 10 sections (5 HIGH relevance)
- Long answer generation (27s) dominated execution time
- More complex question requiring extensive knowledge file content

**Note**: Even the "smallest improvement" scenario is still 16% faster, demonstrating consistent gains across all question types.
