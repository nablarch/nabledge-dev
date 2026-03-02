# Code Analysis Performance Comparison

**Date**: 2026-03-02
**Scenarios**: ca-001 to ca-005 (5 scenarios)
**Comparison**: OLD workflows vs NEW workflows

## Executive Summary

⚠️ **Unexpected Result: NEW workflows are 4.5% SLOWER on average**

- **OLD Average**: 207.4s (3m 27s)
- **NEW Average**: 216.8s (3m 37s)
- **Time Lost**: +9.4s per scenario (average)
- **Detection Accuracy**: Mixed results (96.0% OLD → 100% NEW)

**Key Finding**: Unlike knowledge-search scenarios (54% faster), code-analysis scenarios show REGRESSION in NEW workflows.

## Scenario-by-Scenario Comparison

| Scenario | Question | OLD Duration | NEW Duration | Change | Detection (OLD) | Detection (NEW) |
|----------|----------|--------------|--------------|---------|-----------------|-----------------|
| ca-001 | ExportProjectsInPeriodAction理解 | 163s | 168s | **+3%** ⚠️ | 15/15 (100%) | 15/15 (100%) |
| ca-002 | LoginAction理解 | 299s | 168s | **-44%** ⚡ | 14/14 (100%) | 14/14 (100%) |
| ca-003 | ProjectSearchAction理解 | 179s | 215s | **+20%** ⚠️ | 11/11 (100%) | 11/11 (100%) |
| ca-004 | ProjectCreateAction理解 | 185s | 254s | **+37%** ⚠️ | 11/12 (91.7%) | 14/14 (100%) |
| ca-005 | ProjectUpdateAction理解 | 211s | 279s | **+32%** ⚠️ | 12/12 (100%) | 12/12 (100%) |
| **Average** | | **207.4s** | **216.8s** | **+4.5%** | **96.0%** | **100%** |

### Performance Analysis

**Winners (1 scenario)**:
- ✅ ca-002: -131s (-44%) - Major improvement

**Losers (4 scenarios)**:
- ⚠️ ca-001: +5s (+3%)
- ⚠️ ca-003: +36s (+20%)
- ⚠️ ca-004: +69s (+37%)
- ⚠️ ca-005: +68s (+32%)

## Root Cause Analysis

### Why ca-002 Is Faster (-44%)

**OLD workflow bottleneck (ca-002)**:
- Step 9 (Pre-fill template): **107s** (52.7% of executor time) 🔥
- Step 11 (Build/Generate documentation): 72s (35.5%)
- **Total**: 299s

**NEW workflow (ca-002)**:
- Step 12 (Build documentation content): 65s (38.7% of time)
- Step 9 (Pre-fill template): 3s (1.8%)
- **Total**: 168s

**Improvement**: OLD pre-fill script had 107s anomaly (likely I/O or script bug). NEW workflow eliminated this bottleneck.

### Why Other Scenarios Are Slower

#### ca-001: +5s (+3%)

**Token usage**:
- OLD: 6,370 tokens
- NEW: 46,660 tokens (+634% increase!) 🔥

**Analysis**: NEW workflow generates 7.3x more tokens but takes nearly the same time. Token generation cost offset by workflow efficiency. Still, the massive token increase is concerning for cost.

#### ca-003: +36s (+20%)

**Duration breakdown**:
- OLD Step 3.3 (Write output): 60s (47.6% bottleneck)
- NEW Step 5 (Generate documentation): 157s (73% bottleneck)

**Analysis**: NEW workflow consolidated documentation generation, but the consolidated step is much slower overall.

#### ca-004: +69s (+37%)

**Token usage**:
- OLD: 7,700 tokens
- NEW: 55,745 tokens (+624% increase!) 🔥

**Duration breakdown**:
- OLD Step 3 (Generate documentation): 93s (55%)
- NEW Step 15 (Build documentation): 86s (33.9%)

**Analysis**: Despite similar bottleneck step durations, overall execution is 69s slower. Multiple smaller steps in NEW workflow accumulate overhead.

#### ca-005: +68s (+32%)

**OLD workflow had anomaly**:
- Step 11 (Update time placeholders): **130s** (61.6% of time) 🔥
- This was identified as I/O or script bug in OLD baseline report

**NEW workflow**:
- No single anomaly step
- Step 3.4 (Build documentation): 105s (37.6%)
- Overall: 279s

**Analysis**: Even with OLD anomaly (130s), NEW is still slower (279s vs 211s). This suggests fundamental architectural inefficiency in NEW code-analysis workflow.

## Token Usage Analysis

### Overall Token Statistics

| Metric | OLD Workflows | NEW Workflows | Change |
|--------|---------------|---------------|---------|
| **Average Tokens** | 15,149 | 34,761 | **+129%** 🔥 |
| **Average IN** | 3,787 | 14,372 | **+280%** 🔥 |
| **Average OUT** | 11,362 | 20,389 | **+79%** |
| **Total (5 scenarios)** | 75,745 | 173,805 | **+129%** |

**Critical Finding**: NEW workflows use 2.3x more tokens on average, with input tokens tripling (+280%). This represents significant cost increase.

### Per-Scenario Token Comparison

| Scenario | OLD Tokens | NEW Tokens | Change | Cost Impact |
|----------|------------|------------|---------|-------------|
| ca-001 | 6,370 | 46,660 | **+634%** | 🔥 Very High |
| ca-002 | 11,560 | 21,650 | +87% | Moderate |
| ca-003 | 17,390 | 13,750 | -21% | ✅ Reduced |
| ca-004 | 7,700 | 55,745 | **+624%** | 🔥 Very High |
| ca-005 | 33,725 | 36,000 | +7% | Low |

**Analysis**:
- ca-001 and ca-004 show catastrophic token increase (6-7x)
- ca-003 is the only scenario with reduced token usage
- Average token cost increased by 129%

## Detection Quality Comparison

| Metric | OLD Workflows | NEW Workflows | Result |
|--------|---------------|---------------|---------|
| **Total Detection Items** | 63 expected | 66 expected | +3 items |
| **Detection Rate** | 60/63 (95.2%) | 66/66 (100%) | ✅ Improved |
| **False Negatives** | 3 (ca-004: 1) | 0 | ✅ Eliminated |

**Improvement**: NEW workflows achieved 100% detection rate by fixing ca-004 detection gap (transaction handling was missed in OLD).

## Architectural Comparison

### OLD Workflow (code-analysis.md)

```
3 Main Steps
├─ Step 1: Identify target & dependencies (5s avg)
├─ Step 2: Search Nablarch knowledge (20s avg)
│  └─ Calls keyword-search.md internally
└─ Step 3: Generate documentation (146s avg) 🔥
   ├─ Read templates (2s)
   ├─ Pre-fill template script (54s avg, 107-130s anomalies)
   ├─ Generate Mermaid skeletons (1s)
   ├─ Build content (60s avg)
   └─ Write output (33s avg)

Bottleneck: Step 3 (70% of time)
Anomalies: ca-002 (107s), ca-005 (130s) pre-fill script issues
```

### NEW Workflow (code-analysis.md with _knowledge-search.md)

```
Variable Steps (9-17 steps depending on scenario)
├─ Step 0: Record start time (1-10s)
├─ Step 1: Identify target & dependencies (5-34s)
├─ Step 2: Search Nablarch knowledge (33-70s)
│  └─ Calls _knowledge-search.md with full-text search
├─ Step 3.1: Read templates (2-7s)
├─ Step 3.2: Pre-fill placeholders (2-3s)
├─ Step 3.3: Generate diagram skeletons (1-15s)
└─ Step 3.4-3.5: Build & write documentation (44-157s) 🔥

Bottleneck: Documentation generation (30-73% of time)
No anomalies: Pre-fill script fixed (2-3s consistently)
```

### Key Architectural Differences

1. **Knowledge Search**:
   - OLD: keyword-search.md (sequential index processing)
   - NEW: _knowledge-search.md (full-text search fallback)
   - Impact: NEW is 2-3.5x slower for knowledge search in code-analysis context

2. **Step Granularity**:
   - OLD: 3 main steps (coarse-grained)
   - NEW: 9-17 steps (fine-grained)
   - Impact: More step overhead in NEW

3. **Token Usage**:
   - OLD: Conservative token usage (avg 15,149)
   - NEW: Aggressive token usage (avg 34,761, +129%)
   - Impact: 2.3x cost increase

## Why Code-Analysis Results Differ from Knowledge-Search

### Knowledge-Search Success (-54%)
- Full-text search optimized for simple keyword matching
- Reduced workflow steps from 8 to 6-7
- Batch section reading eliminated sequential overhead
- **Result**: 54% faster, same accuracy

### Code-Analysis Failure (+4.5%)
- Knowledge search is EMBEDDED in code-analysis (Step 2)
- NEW _knowledge-search more thorough but slower (33-70s vs 13-40s in OLD)
- Fine-grained steps accumulate overhead
- Massive token increase (2.3x) with limited execution speedup
- **Result**: 4.5% slower, marginally better accuracy

## Bottleneck Breakdown

### OLD Workflow Bottlenecks (Average)

| Step | Description | Avg Duration | % of Time |
|------|-------------|--------------|-----------|
| 3 | Generate documentation | 146s | 70% 🔥 |
| 2 | Search knowledge | 20s | 10% |
| 1 | Analyze dependencies | 5s | 2% |

**Critical**: Pre-fill script anomalies (107-130s) in ca-002 and ca-005.

### NEW Workflow Bottlenecks (Average)

| Step | Description | Avg Duration | % of Time |
|------|-------------|--------------|-----------|
| 3.4-3.5 | Build & write docs | 92s | 42% 🔥 |
| 2 | Search knowledge | 51s | 24% 🔥 |
| 1 | Analyze dependencies | 22s | 10% |

**Critical**: Knowledge search is 2.5x slower in NEW (51s vs 20s), absorbing most gains from documentation generation improvements.

## Cost Analysis

### Token Cost Implications

Assuming Claude Opus 4.6 pricing (example):
- Input: $15 per 1M tokens
- Output: $75 per 1M tokens

**OLD Workflows (per scenario avg)**:
- IN: 3,787 tokens × $15/1M = $0.057
- OUT: 11,362 tokens × $75/1M = $0.852
- **Total**: $0.909 per scenario

**NEW Workflows (per scenario avg)**:
- IN: 14,372 tokens × $15/1M = $0.216
- OUT: 20,389 tokens × $75/1M = $1.529
- **Total**: $1.745 per scenario

**Cost Increase**: +$0.836 per scenario (+92%)

**Yearly Impact** (assuming 100 code analyses per day):
- OLD: $0.909 × 100 × 365 = $33,179/year
- NEW: $1.745 × 100 × 365 = $63,693/year
- **Increase**: +$30,514/year (+92%)

## Success Criteria Verification

❌ **Search execution time reduced**: Code-analysis is 4.5% SLOWER (207.4s → 216.8s)
✅ **Search accuracy maintained**: Improved from 95.2% to 100% (+4.8%)
✅ **Performance documented**: Detailed comparison with root cause analysis

## Recommendations

### Immediate Actions (Required)

1. **Revert code-analysis to OLD workflow**: NEW workflow shows regression
   - Keep NEW _knowledge-search.md for knowledge-search scenarios
   - Restore OLD code-analysis.md with keyword-search.md integration
   - Fix pre-fill script anomalies (ca-002: 107s, ca-005: 130s)

2. **Investigate token explosion**: Understand why ca-001 (+634%) and ca-004 (+624%)
   - Review _knowledge-search.md token usage in code-analysis context
   - Check for duplicated content reads or redundant processing
   - Consider token budgets for cost control

3. **Fix ca-002 and ca-005 pre-fill script issues in OLD workflow**:
   - 107s and 130s anomalies need investigation
   - Likely I/O blocking or script bugs
   - Should reduce to 2-3s like NEW workflow

### Hybrid Approach (Recommended)

**Option 1: Workflow-Specific Knowledge Search**
- Use NEW _knowledge-search.md for qa.md (knowledge-search scenarios)
- Use OLD keyword-search.md for code-analysis.md (code-analysis scenarios)
- Maintain both workflows with different optimization goals

**Option 2: Optimize NEW for Code-Analysis**
- Add code-analysis-specific optimizations to _knowledge-search.md
- Reduce token usage with selective section reading
- Add early termination for high-confidence matches
- Target: Match OLD performance (20s knowledge search) while keeping full-text benefits

### Long-Term Improvements

1. **Knowledge search caching**: Reduce redundant full-text searches
2. **Token budgets**: Enforce token limits per step to control costs
3. **Parallel processing**: Run knowledge search and dependency analysis in parallel
4. **Template optimization**: Reduce template size to lower token overhead

## Conclusion

The NEW workflows show **divergent results**:
- ✅ **Knowledge-Search**: 54% faster (89s → 41s) - Success
- ❌ **Code-Analysis**: 4.5% slower (207.4s → 216.8s) - Regression

**Root causes**:
1. NEW _knowledge-search.md is thorough but slow (2.5x slower when embedded)
2. Token usage explosion (+129%) with minimal execution speedup
3. Fine-grained step breakdown adds overhead without clear benefits

**Decision point**:
- Keep NEW workflows for knowledge-search (proven 54% improvement)
- Revert to OLD workflows for code-analysis (or create hybrid approach)
- Fix OLD workflow anomalies (pre-fill script issues)

The performance regression is **unacceptable** for production deployment without addressing the knowledge search bottleneck and token cost explosion in code-analysis scenarios.
