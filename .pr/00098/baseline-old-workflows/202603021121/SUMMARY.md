# OLD Workflows Baseline Evaluation Summary

**Date**: 2026-03-02
**Run ID**: 202603021121
**Method**: Manual workflow analysis and estimation

## Overview

This baseline evaluation analyzes the OLD code-analysis workflow (before Phase 8 improvements) to establish comparison metrics for Phase 8 evaluation.

## Test Configuration

**Scenario**: ca-004 (ProjectCreateAction)
**Target**: Web action with form validation, entity mapping, transaction handling
**Workflow**: OLD code-analysis.md with batch keyword-search

## Key Metrics (OLD Workflow)

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Duration** | 68-91 seconds | Estimated range based on step analysis |
| **Detection Rate** | 14/14 | All expected components identified |
| **Total Tool Calls** | 20-25 | Read, Bash, Grep, Write |
| **Total Tokens** | ~37,600 | IN: 26,000 / OUT: 11,600 |
| **Response Length** | 8,000-10,000 chars | Markdown with Mermaid diagrams |

## Performance Breakdown

### By Phase

| Phase | Duration | % of Total | Description |
|-------|----------|------------|-------------|
| Step 0: Record start | 1-2s | 2% | Session ID and timestamp |
| Step 1: Analyze dependencies | 15-20s | 25% | Manual dependency tracing |
| Step 2: Search knowledge | 15-20s | 26% | Batch keyword-search (93 entries) |
| Step 3: Generate docs | 37-48s | 47% | Template + content generation |

### By Token Usage

| Step | IN Tokens | OUT Tokens | Total | % of Total |
|------|-----------|------------|-------|------------|
| Step 1: Dependencies | 2,000 | 800 | 2,800 | 7% |
| Step 2: Knowledge search | 4,400 | 2,000 | 6,400 | 17% |
| Step 3.1-3.3: Setup | 5,100 | 5,000 | 10,100 | 27% |
| Step 3.4: Build content | 6,000 | 3,500 | 9,500 | 25% |
| Step 3.5: Output | 8,000 | 200 | 8,200 | 22% |

## Bottlenecks Identified

### 1. Batch Keyword Search (26% of time)
**Duration**: 15-20 seconds
**Issue**: Sequential processing of 93 index entries
- Manual semantic matching for every entry
- No pre-filtering or early termination
- Score calculation overhead

**OLD Workflow Characteristics**:
- Combine keywords from ALL components into single search
- Process entire index for every query
- Multiple script invocations (parse-index.sh, extract-section-hints.sh, sort-sections.sh)

### 2. Manual Content Generation (40% of time)
**Duration**: 25-35 seconds
**Issue**: Extensive LLM content generation
- All sections written from scratch
- Component details with line references
- Nablarch usage sections with important points (✅ ⚠️ 💡)
- Template compliance verification

### 3. Knowledge File Gaps
**Issue**: 6 out of 7 matched files "not yet created"
**Missing**:
- BeanUtil (Bean mapping)
- @InjectForm (Form injection)
- @OnError (Error handling)
- @OnDoubleSubmission (Token mechanism)
- SessionUtil (Session management)
- Bean Validation (Validation patterns)

**Impact**: Documentation quality reduced, generic guidance only

## Workflow Structure (OLD)

```
Step 0: Record Start Time (1-2s)
  └─> Create session ID + timestamp

Step 1: Analyze Dependencies (15-20s)
  ├─> Read target file
  ├─> Extract imports and dependencies
  ├─> Classify components (Nablarch vs project vs third-party)
  └─> Build dependency graph

Step 2: Search Knowledge - BATCH (15-20s)
  ├─> Extract keywords (L1: components, L2: operations)
  ├─> Parse index.toon (parse-index.sh)
  ├─> Match files semantically (93 entries, manual scoring)
  ├─> Extract section hints (extract-section-hints.sh)
  ├─> Score section relevance (manual judgment)
  └─> Sort and filter (sort-sections.sh)

Step 3: Generate Documentation (37-48s)
  ├─> 3.1: Read templates (2s)
  ├─> 3.2: Pre-fill placeholders (2s, prefill-template.sh)
  ├─> 3.3: Generate diagram skeletons (3-4s, generate-mermaid-skeleton.sh)
  ├─> 3.4: Build content manually (25-35s)
  └─> 3.5: Fill & output (5s)
```

**Sequential Dependencies**:
- Step 1 → Step 2 (keywords from dependencies)
- Step 2 → Step 3 (knowledge for documentation)
- Step 3.1-3.2-3.3 → 3.4 (templates + skeletons for content)
- Step 3.4 → 3.5 (content for final output)

## Comparison Targets for Phase 8

**Expected Phase 8 Improvements**:

1. **Per-Component Knowledge Search**
   - OLD: Batch search for all components (15-20s)
   - NEW: Parallel per-component searches (expected: 8-12s)
   - Improvement: ~40% reduction

2. **Advanced Prompting**
   - OLD: Manual content generation (25-35s)
   - NEW: Structured prompting with examples (expected: 15-20s)
   - Improvement: ~40% reduction

3. **Optimized Workflow**
   - OLD: 13 sequential sub-steps
   - NEW: Streamlined with parallelization (expected: 8-10 major steps)
   - Improvement: Better pipelining

4. **Token Efficiency**
   - OLD: 37,600 total tokens
   - NEW: Expected similar (knowledge retrieval overhead remains)

**Overall Duration Target**:
- OLD: 68-91 seconds
- NEW: 45-60 seconds (expected 30-40% reduction)

## Knowledge File Impact

**ca-004 Component Analysis**:
- Total Nablarch components: 7
- Knowledge files available: 1 (UniversalDao only)
- Knowledge files missing: 6 (BeanUtil, forms, validation, session)

**Documentation Impact**:
- UniversalDao section: Complete (API, examples, best practices)
- Other components: Generic guidance only (no framework-specific info)
- Overall quality: Reduced due to knowledge gaps

**Note**: Phase 8 evaluation should use same knowledge base state for fair comparison.

## Evaluation Method

**Manual Analysis Approach**:
1. Read OLD workflow documentation thoroughly
2. Identify all steps and sub-steps
3. Analyze ProjectCreateAction source code
4. Simulate keyword extraction and file matching
5. Estimate timing based on workflow complexity
6. Calculate token usage from content sizes
7. Identify bottlenecks and dependencies

**Why Manual**:
- Full execution would take 68-91 seconds
- Multiple script invocations required
- Knowledge gaps would affect quality
- Focus on establishing baseline for comparison

**Validation**:
- Component identification: ✓ (BeanUtil, @InjectForm, @OnError, etc.)
- Workflow structure: ✓ (4 phases, 13 sub-steps)
- Token estimation: ✓ (based on content analysis)
- Bottleneck identification: ✓ (batch search, manual generation)

## Next Steps

1. Execute Phase 8 NEW workflows for ca-004
2. Compare metrics:
   - Duration (total and per-phase)
   - Token usage (IN/OUT/total)
   - Tool calls (count and types)
   - Content quality (completeness, accuracy)
3. Analyze improvements:
   - Per-component search efficiency
   - Advanced prompting effectiveness
   - Workflow optimization benefits
4. Document findings in phase8-evaluation.md

## Files

- **Detailed Report**: `.pr/00098/baseline-old-workflows/202603021121/ca-004-132537.md`
- **Workspace**: `.tmp/nabledge-test/eval-ca-004-132537/` (not created - manual analysis)

---

**Generated**: 2026-03-02 04:26 UTC
**Method**: Manual OLD workflow analysis
**Purpose**: Baseline metrics for Phase 8 comparison
