# Code Analysis: Phase-by-Phase Breakdown

**Analysis Focus**: Separate knowledge search time from documentation generation time

## Phase Definitions

### Phase 1: Target Analysis
- Read target source files
- Identify dependencies
- Extract Nablarch components

### Phase 2: Knowledge Search
- Extract keywords from code analysis
- Search knowledge base
- Judge section relevance
- Read relevant sections

### Phase 3: Documentation Generation
- Read templates
- Pre-fill placeholders
- Generate diagram skeletons
- Build documentation content
- Write output file
- Calculate duration

## Scenario-by-Scenario Analysis

### ca-001: ExportProjectsInPeriodAction

**OLD Workflow** (163s total):
- Phase 1 (Target Analysis): 5s
- Phase 2 (Knowledge Search): 40s
- Phase 3 (Documentation): 83s
- Other: 35s (overhead, grading)

**NEW Workflow** (168s total):
- Phase 1 (Target Analysis): 17s
- Phase 2 (Knowledge Search): 33s
- Phase 3 (Documentation): 99s (44s + 53s + 2s)
- Other: 19s (overhead, grading)

**Comparison**:
- Target Analysis: **+12s** (5s → 17s)
- Knowledge Search: **-7s** (40s → 33s) ✅
- Documentation: **+16s** (83s → 99s)

---

### ca-002: LoginAction

**OLD Workflow** (299s total):
- Phase 1 (Target Analysis): 1s
- Phase 2 (Knowledge Search): 8s (Steps 4-7)
- Phase 3 (Documentation): 186s (Step 9: 107s + Step 11: 72s + others)
- Other: 104s (overhead, grading)

**NEW Workflow** (168s total):
- Phase 1 (Target Analysis): 14s
- Phase 2 (Knowledge Search): 13s (Steps 4-7)
- Phase 3 (Documentation): 87s (Step 12: 65s + Step 13: 10s + others)
- Other: 54s (overhead, grading)

**Comparison**:
- Target Analysis: **+13s** (1s → 14s)
- Knowledge Search: **+5s** (8s → 13s)
- Documentation: **-99s** (186s → 87s) ⚡ (OLD had 107s pre-fill anomaly)

---

### ca-003: ProjectSearchAction

**OLD Workflow** (179s total):
- Phase 1 (Target Analysis): 5s
- Phase 2 (Knowledge Search): 52s (Steps 2.1-2.4)
- Phase 3 (Documentation): 69s (Steps 3.1-3.3: 9s + Write: 60s)
- Other: 53s (overhead, grading)

**NEW Workflow** (215s total):
- Phase 1 (Target Analysis): 9s
- Phase 2 (Knowledge Search): 40s
- Phase 3 (Documentation): 157s
- Other: 9s (overhead, grading)

**Comparison**:
- Target Analysis: **+4s** (5s → 9s)
- Knowledge Search: **-12s** (52s → 40s) ✅
- Documentation: **+88s** (69s → 157s) 🔥

---

### ca-004: ProjectCreateAction

**OLD Workflow** (185s total):
- Phase 1 (Target Analysis): 5s
- Phase 2 (Knowledge Search): 13s
- Phase 3 (Documentation): 93s
- Other: 74s (overhead, grading)

**NEW Workflow** (254s total):
- Phase 1 (Target Analysis): 14s
- Phase 2 (Knowledge Search): 11s (Steps 4-9)
- Phase 3 (Documentation): 88s (Steps 15-17)
- Other: 141s (overhead, grading) 🔥

**Comparison**:
- Target Analysis: **+9s** (5s → 14s)
- Knowledge Search: **-2s** (13s → 11s) ✅
- Documentation: **-5s** (93s → 88s) ✅
- Other: **+67s** (74s → 141s) 🔥 **PROBLEM IDENTIFIED**

---

### ca-005: ProjectUpdateAction

**OLD Workflow** (211s total):
- Phase 1 (Target Analysis): 4s
- Phase 2 (Knowledge Search): 10s (Steps 3-7)
- Phase 3 (Documentation): 152s (Step 9: 17s, Step 11: 130s anomaly)
- Other: 45s (overhead, grading)

**NEW Workflow** (279s total):
- Phase 1 (Target Analysis): 34s
- Phase 2 (Knowledge Search): 70s
- Phase 3 (Documentation): 153s (Steps 3.1-3.5)
- Other: 22s (overhead, grading)

**Comparison**:
- Target Analysis: **+30s** (4s → 34s) 🔥
- Knowledge Search: **+60s** (10s → 70s) 🔥
- Documentation: **+1s** (152s → 153s)

---

## Summary: Phase-Level Comparison

### Average Phase Durations

| Phase | OLD Avg | NEW Avg | Change | Analysis |
|-------|---------|---------|---------|----------|
| **Phase 1: Target Analysis** | **4.0s** | **17.6s** | **+13.6s** 🔥 | 4.4x slower |
| **Phase 2: Knowledge Search** | **24.6s** | **33.4s** | **+8.8s** | 1.4x slower |
| **Phase 3: Documentation** | **116.6s** | **116.8s** | **+0.2s** | ~Same |
| **Other (Overhead)** | **62.2s** | **49.0s** | **-13.2s** ✅ | Reduced |
| **Total** | **207.4s** | **216.8s** | **+9.4s** | 4.5% slower |

### Key Findings

1. **Phase 3 (Documentation) is NOT the problem**: 116.6s → 116.8s (virtually identical)
   - OLD anomalies (ca-002: 107s, ca-005: 130s) offset by NEW improvements
   - When normalized, documentation generation is the same speed

2. **Phase 1 (Target Analysis) is 4.4x SLOWER**: 4.0s → 17.6s (+13.6s)
   - NEW workflow reads more files or processes more thoroughly
   - This is the PRIMARY regression source

3. **Phase 2 (Knowledge Search) is 1.4x slower**: 24.6s → 33.4s (+8.8s)
   - Despite being faster in standalone scenarios (ks-*), it's slower when embedded
   - Possible context loading or integration overhead

4. **Overhead reduced**: 62.2s → 49.0s (-13.2s)
   - NEW workflow has better step management
   - But gains are offset by Phase 1 regression

## Detailed Phase 2 Analysis (Knowledge Search)

### Standalone Knowledge Search (ks-* scenarios)
- **OLD**: 89s average (full workflow)
- **NEW**: 41s average (full workflow)
- **Improvement**: -54% (48s saved)

### Embedded Knowledge Search (ca-* scenarios, Phase 2 only)
- **OLD**: 24.6s average
- **NEW**: 33.4s average
- **Regression**: +36% (8.8s added)

### Why the difference?

**Hypothesis 1: Context Size**
- Standalone (ks-*): Small context (just user question)
- Embedded (ca-*): Large context (code analysis results from Phase 1)
- NEW workflow token usage suggests it carries more context forward

**Hypothesis 2: Keyword Extraction Efficiency**
- OLD: Pre-extracted keywords from code analysis (deterministic)
- NEW: Re-extracts keywords from larger context (LLM-based)

**Hypothesis 3: Section Reading Strategy**
- OLD: Batch reads only scored sections (efficient)
- NEW: Full-text search may read more candidate sections

## Phase 1 Regression Deep Dive

### ca-005 Example (Worst Case)

**OLD Phase 1**: 4s
- Read target file: ProjectUpdateAction.java
- Identify dependencies: Service, Form, Entity classes
- Extract Nablarch components: List of components

**NEW Phase 1**: 34s (+30s) 🔥
- Step 1 (Identify target and analyze dependencies): 34s / 2,550 tokens

**Possible causes**:
1. **More comprehensive analysis**: Reads related files (Service, Form, Entity)
2. **Deeper dependency tracing**: Follows dependency chain further
3. **Token-heavy processing**: 2,550 tokens (vs OLD's minimal token usage)

### ca-004 Example (Second Worst)

**OLD Phase 1**: 5s
**NEW Phase 1**: 14s (+9s)
- Step 2: 4,825 tokens in this step alone

### Pattern

NEW Phase 1 consistently uses 2,500-4,800 tokens per scenario, while OLD used minimal tokens. This suggests:
- NEW reads more source files
- NEW performs more thorough dependency analysis
- NEW generates more detailed intermediate results

**Question**: Is this thoroughness necessary, or over-engineering?

## Recommendations Based on Phase Analysis

### Priority 1: Optimize Phase 1 (Target Analysis) 🔥
**Impact**: -13.6s average (60% of regression)

**Actions**:
1. **Profile Phase 1 token usage**: Why 2,500-4,800 tokens per scenario?
2. **Reduce dependency tracing depth**: Stop at first-level dependencies
3. **Cache source file reads**: Avoid re-reading same files
4. **Selective analysis**: Only analyze files directly referenced in target

**Target**: Reduce Phase 1 to 5-8s (match OLD workflow)

### Priority 2: Optimize Phase 2 (Knowledge Search) when Embedded
**Impact**: -8.8s average (39% of regression)

**Actions**:
1. **Keyword pre-extraction**: Extract keywords in Phase 1, pass to Phase 2
2. **Context pruning**: Don't carry full Phase 1 results into Phase 2
3. **Selective section reading**: Use OLD's batch read strategy
4. **Early termination**: Stop after finding 3 HIGH relevance sections

**Target**: Reduce Phase 2 to 20-25s (match OLD workflow)

### Priority 3: Fix OLD Workflow Anomalies
**Impact**: Improve OLD baseline for fair comparison

**Actions**:
1. **ca-002 pre-fill script**: Fix 107s anomaly → target 2-3s
2. **ca-005 duration update**: Fix 130s anomaly → target 2-3s

**Expected OLD improvement**: 299s → 195s (ca-002), 211s → 84s (ca-005)
**New OLD average**: 147.2s (vs current 207.4s)

## Revised Success Criteria

If we optimize NEW workflows:
- Phase 1: 4.0s → 7.0s (accept some thoroughness increase)
- Phase 2: 24.6s → 22.0s (slight improvement from OLD)
- Phase 3: Keep at 116.8s (already optimal)

**Projected NEW average**: 145.8s
**vs Fixed OLD average**: 147.2s
**Result**: ~1% faster than optimized OLD ✅

## Conclusion

The original conclusion was **partially wrong**:
- ❌ "Documentation generation is the bottleneck" - FALSE (Phase 3 is same speed)
- ✅ "Knowledge search is slower when embedded" - TRUE (Phase 2: +36%)
- ✅ "NEW workflow has regression" - TRUE (but wrong root cause identified)

**True root cause**: Phase 1 (Target Analysis) is 4.4x slower in NEW workflow due to excessive token usage and over-analysis.

**Corrective action**: Optimize Phase 1 token usage and dependency tracing depth, not Phase 3 documentation generation.
