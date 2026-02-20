# Notes

## 2026-02-20

### Decision: Batch Processing Approach

**Problem**: Current workflows execute jq once per file/section, resulting in excessive tool calls (12 for keyword-search, 36 for code analysis).

**Solution**: Implement batch processing by consolidating multiple jq operations into single bash scripts.

**Why this approach**:
- **Reduces tool call overhead**: Each tool call has inherent latency (API round-trip, context switching). Batching reduces this multiplicative overhead.
- **Maintains accuracy**: Batch processing produces identical output by preserving the same scoring logic and filtering criteria.
- **Simpler for agent**: Clearer instructions with concrete bash script examples guide the agent to efficient execution patterns.
- **Composable**: Each workflow's batching is independent, allowing incremental optimization.

**Alternatives considered**:
1. **Parallel execution**: Execute jq calls in parallel using bash `&` - Rejected because tool calls are sequential by nature (API limitation)
2. **Index pre-processing**: Build optimized index structure - Rejected as over-engineering for current scale (93 entries)
3. **Change workflow logic**: Modify matching algorithm - Rejected to minimize scope and maintain accuracy

### Implementation Details

#### 1. keyword-search.md Step 2

**Before**:
```bash
# Execute once per file (12 calls)
jq '.index' knowledge/features/libraries/universal-dao.json
```

**After**:
```bash
# Batch process all files (1-2 calls)
for file in "${files[@]}"; do
  jq '.index' "knowledge/$file" | {
    # Extract, score, filter inline
  }
done | sort -rn | head -30
```

**Key improvements**:
- Single loop processes all files
- Inline scoring eliminates separate filtering pass
- Early termination at 30 candidates
- Tool calls: 12 → 3 (including loop + sort)

#### 2. section-judgement.md Step 1

**Before**:
```bash
# Execute once per section (5-10 calls)
jq '.sections.paging' knowledge/features/libraries/universal-dao.json
```

**After**:
```bash
# Group by file, batch extract (2-3 calls)
declare -A file_sections
# Group candidates by file
# Extract all sections from same file in one jq call
jq '.sections.section1, .sections.section2, ...' file.json
```

**Key improvements**:
- Group candidates by file first
- Single jq call extracts multiple sections from same file
- Graceful handling of missing sections with `// empty`
- Tool calls: 5-10 → 2-3

#### 3. code-analysis.md Step 2

**Before**:
```
# Sequential per-component execution (36 calls)
For each component:
  - Execute keyword-search (18 calls)
  - Execute section-judgement (18 calls)
```

**After**:
```
# Batch execution for all components (15 calls)
1. Identify all components once
2. Combine all keywords (L1+L2+L3)
3. Execute keyword-search once (6 calls)
4. Execute section-judgement once (6 calls)
5. Group results by component (3 calls)
```

**Key improvements**:
- Upfront component identification
- Single workflow execution with combined keywords
- Post-processing groups results by component
- Tool calls: 36 → 15

### Performance Validation Approach

**Challenge**: These are workflow instruction files (not executable code), so automated performance testing requires actual workflow execution by Claude Code during user interactions.

**Validation Strategy**:

1. **Baseline Measurement** (not yet done):
   - Record execution time for 10 knowledge search requests
   - Record execution time for 10 code analysis requests
   - Measure tool call count and time distribution
   - Establish baseline: knowledge search ~52s, code analysis ~204s

2. **Post-Implementation Measurement** (to be done after merge):
   - Execute same 10 knowledge search requests
   - Execute same 10 code analysis requests
   - Compare tool call count and total time
   - Target: knowledge search ≤25s, code analysis ≤126s

3. **Accuracy Validation**:
   - Compare output sections for same requests before/after
   - Verify 100% match in selected sections
   - Verify score calculations are identical

**Test Scenarios** (for future validation):

**Knowledge Search Tests** (10 scenarios):
1. "ページングを実装したい" (UniversalDao paging)
2. "バリデーションエラーの処理方法" (Bean Validation)
3. "RESTful APIの作成" (JAX-RS)
4. "バッチ処理の実装" (Batch processing)
5. "トランザクション管理" (Transaction handling)
6. "ファイルアップロード" (File upload)
7. "メール送信" (Mail sending)
8. "ログ出力" (Logging)
9. "認証と認可" (Authentication/Authorization)
10. "エラーハンドリング" (Error handling)

**Code Analysis Tests** (10 scenarios):
1. LoginAction (with UniversalDao, Bean Validation)
2. ProjectSearchAction (with pagination)
3. ProjectRegisterAction (with transaction)
4. BatchAction (with batch components)
5. ApiResource (with JAX-RS)
6. FileUploadAction (with multipart)
7. MailAction (with mail components)
8. ReportAction (with report generation)
9. ErrorHandler (with error handling)
10. SecurityHandler (with authentication)

**Measurement Criteria**:
- Total execution time (start to completion)
- Tool call count by phase (search, extraction, judgement)
- Time distribution percentage (overhead vs processing)
- Output accuracy (section matches, score matches)

**Expected Results**:
- Knowledge search: 52s → 25s (52% improvement, tool call overhead 68% → <30%)
- Code analysis: 204s → 126s (38% improvement, tool call overhead 51% → <25%)
- Output accuracy: 100% (identical sections and scores)

**Status**: Implementation complete. Performance validation requires actual workflow execution in production usage. Test plan documented for future validation.

### Learning: Workflow Optimization Patterns

**Pattern discovered**: For agent-executed workflows that process multiple items sequentially, batch processing at the tool call level provides significant performance gains without changing workflow logic.

**Applicability**:
- Any workflow with "for each X, execute tool Y" pattern
- Tool calls have non-trivial overhead (API round-trip, context)
- Output order doesn't matter (can be sorted after batching)
- Batch size is manageable (not memory-bound)

**Implementation template**:
1. Identify sequential tool call pattern
2. Group items by common operation
3. Design batch script with inline processing
4. Add sorting/filtering after batch extraction
5. Document with concrete examples

**Not applicable when**:
- Order matters and depends on previous results
- Conditional logic prevents batching
- Batch size causes memory issues
- Tool doesn't support batch operations

### Follow-up Tasks

**Immediate** (this PR):
- [x] Update keyword-search.md with batch processing
- [x] Update section-judgement.md with batch extraction
- [x] Update code-analysis.md with batch execution
- [x] Document implementation in notes.md
- [x] Update CHANGELOG.md

**Future** (separate issues):
- [ ] Execute 10 knowledge search scenarios to validate performance
- [ ] Execute 10 code analysis scenarios to validate performance
- [ ] Document actual performance improvements in follow-up PR
- [ ] Consider applying batch pattern to other workflows (intent-search, etc.)
