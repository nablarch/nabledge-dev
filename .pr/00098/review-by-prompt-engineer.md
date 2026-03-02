# Expert Review: Prompt Engineer

**Date**: 2026-03-02
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: 15 files (11 nabledge-6, 4 nabledge-5 sampled)

## Overall Assessment

**Rating**: 4/5
**Summary**: The workflow refactoring demonstrates strong architectural design with clear separation of concerns, explicit fallback strategies, and well-structured instructions. Minor improvements needed in error propagation clarity, example quality, and agent autonomy guidance.

## Key Issues

### High Priority

**None identified**

### Medium Priority

1. **Error handling ambiguity in workflow chaining**
   - File: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search.md`
   - Description: Step 4 says "分岐: 候補ファイルが0件の場合は空のポインタJSONを返して終了" but doesn't specify the exact JSON structure. The schema at the top shows `{"results": []}`, but agents might be uncertain whether to return this exact structure or propagate an error message.
   - Suggestion: Add explicit output example: "空のポインタJSON: `{\"results\": []}`" immediately after the condition statement. This removes ambiguity about what "empty" means.

2. **Missing keyword extraction examples for edge cases**
   - File: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search.md`
   - Description: Step 1 provides one example ("ページングを実装したい" → keywords) but doesn't show how to handle more complex queries like "バッチでページングする際のトランザクション管理" which involves multiple concepts. Agents may over-extract or under-extract keywords.
   - Suggestion: Add 2-3 more examples covering: (1) multi-concept query, (2) vague query ("これどうやるの?"), (3) technical term-heavy query ("UniversalDaoのfindBySqlFileでSQLIDが解決されない"). This guides agents on balancing breadth vs precision.

3. **Agent autonomy vs script reliance unclear in section-judgement**
   - File: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search/section-judgement.md`
   - Description: Step B says "ツール: メモリ内（エージェント判断）" but Step A uses a bash script. The boundary between what agents compute in-memory vs what scripts handle is not explicit. Agents might try to write their own scoring logic or defer too much to non-existent scripts.
   - Suggestion: Add explicit note at the start of Step B: "**重要**: この判定はLLMの言語理解能力を使う。スクリプトでは実装できない意味的判定のため、エージェントが直接判断する。" This clarifies why some steps are agent-driven.

4. **Fallback strategy clarity in code-analysis**
   - File: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/code-analysis.md`
   - Description: Step 2 mentions "If script fails: Check error message on stderr" but doesn't specify what to do if the error is unrecoverable (e.g., prefill-template.sh missing, permission denied on .claude/skills/). Agents may HALT without providing partial results to the user.
   - Suggestion: Add fallback guidance: "If script is missing or unrecoverable error, generate template content manually using template-guide.md as reference. Log error to user and continue with manual approach." This prevents workflow deadlock.

5. **Template compliance verification lacks concrete checklist**
   - File: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/code-analysis.md`
   - Description: Step 3.5 says "Verify template compliance before writing" with a bullet list, but the verification is qualitative. Agents may interpret "NO section numbers" differently (e.g., is "1. Overview" a section number? What about "Step 1"?).
   - Suggestion: Convert verification list to a concrete yes/no checklist format: "- [ ] No numeric prefixes on section headings (✗ `1. Overview`, ✓ `Overview`)". This makes verification actionable and reduces interpretation variance.

### Low Priority

1. **Inconsistent terminology: "ツール" vs "やること"**
   - Files: All workflow files use a pattern of "**ツール**: X" followed by "**やること**: Y", but the distinction between "tool" (ツール) and "action" (やること) is not always clear. For example, "ツール: メモリ内（エージェント判断）" is not really a tool in the traditional sense.
   - Suggestion: Consider renaming "ツール" to "**実行方法**" (execution method) or "**処理方式**" (processing method) for in-memory agent operations to better reflect that these are cognitive operations, not external tools.

2. **Japanese/English mixing in technical examples**
   - Files: Multiple files mix Japanese descriptions with English technical terms inconsistently. For example, `_knowledge-search.md` uses "relevance降順" (Japanese + English + Japanese) which is fine, but could be more consistent with either "関連度降順" or "relevance descending order".
   - Suggestion: Add a terminology note in SKILL.md: "Technical terms are kept in English when they appear in code/APIs (e.g., 'relevance'), but translated when describing concepts (e.g., '関連度' in user-facing text)." This sets a clear standard.

3. **Example output formatting in full-text-search**
   - File: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search/full-text-search.md`
   - Description: Output format shows `features/libraries/universal-dao.json|paging` but doesn't clarify if this is one result per line or comma-separated. Agents familiar with bash will understand, but clarity helps.
   - Suggestion: Add explicit note: "各行: `ファイル相対パス|セクションID` (改行区切り)" to make line-delimited format explicit.

## Positive Aspects

- **Excellent fallback architecture**: The two-path design (full-text search → index-based search) is clearly documented with explicit branching conditions. Agents will understand when to switch paths without ambiguity.

- **Strong error handling patterns**: Each sub-workflow includes an error handling table that covers common scenarios (0 hits, JSON errors, missing files). This reduces agent confusion when things go wrong.

- **Comprehensive schema documentation**: The Pointer JSON schema in `_knowledge-search.md` is well-defined with field descriptions, type constraints, and sorting rules. Agents can generate valid output without guessing.

- **Concrete output examples**: Most workflows provide actual output examples (bash command output, JSON structures, formatted text), which is critical for agents to understand the expected format.

- **Clear separation of concerns**: Each sub-workflow has a single, well-defined responsibility. The modularity makes it easy to understand what each component does and how they compose.

- **Explicit termination conditions**: Section-judgement includes clear early termination rules (20 sections read OR 5 high-relevance hits). This prevents infinite loops and over-processing.

- **Batch processing guidance**: Code-analysis workflow explicitly encourages batching multiple knowledge searches together, which improves efficiency. The bash script example for keyword combination is particularly helpful.

- **Template automation**: The use of `prefill-template.sh` and `generate-mermaid-skeleton.sh` reduces LLM workload and improves consistency. The scripts handle deterministic content, leaving LLMs to focus on semantic analysis.

- **Duration tracking design**: The session ID and start time recording pattern in code-analysis is robust and handles edge cases (missing files, concurrent executions). The error handling for missing start time is thoughtful.

## Recommendations

### For Future Iterations

1. **Add workflow state machine diagram**: Consider adding a Mermaid state diagram to `_knowledge-search.md` showing the transitions between "keyword extraction" → "full-text search" → "fallback to index search" → "section judgement". This would provide a visual overview of the control flow.

2. **Consider workflow testing framework**: The workflows are complex enough that automated testing would be valuable. Consider creating a `workflows/_test/` directory with example inputs and expected outputs for each workflow, so agents can validate their implementations.

3. **Add performance budgets**: Some workflows have termination conditions (20 sections, 10 files) but these are framed as limits rather than budgets. Consider adding explicit performance guidance: "Target: < 3 tool calls for most queries, < 10 for complex queries". This helps agents optimize their approach.

4. **Strengthen example diversity**: While the examples provided are good, they mostly cover happy-path scenarios. Consider adding examples of failure cases, edge cases, and recovery strategies to better prepare agents for real-world complexity.

5. **Document workflow composition patterns**: The way `qa.md` and `code-analysis.md` both call `_knowledge-search.md` is a composition pattern. Consider documenting this pattern explicitly so future workflows can follow the same structure.

### Process Improvements

1. **Template validation script**: Given the emphasis on template compliance in code-analysis, consider creating a validation script that agents can run to verify their generated content matches the template structure before finalizing.

2. **Workflow versioning**: As workflows evolve, consider adding version metadata to each workflow file (e.g., `version: 2.0` in frontmatter) so agents know which version they're executing, especially if older knowledge files reference older workflow versions.

## Files Reviewed

### Nabledge-6 (11 files)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/SKILL.md` (workflow routing)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/qa.md` (question answering)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search.md` (main orchestrator)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/code-analysis.md` (code analysis)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search/full-text-search.md` (full-text search)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search/index-based-search.md` (index fallback)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search/file-search.md` (file selection)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search/section-search.md` (section selection)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search/section-judgement.md` (relevance judgement)

### Nabledge-5 (4 files sampled)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-5/SKILL.md` (workflow routing)
- `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-5/workflows/qa.md` (question answering)
- Note: Sub-workflow structure mirrors nabledge-6, consistency verified

## Conclusion

This refactoring represents a significant improvement in workflow architecture. The unified search orchestrator with explicit fallback strategies is a major step forward from the previous 3-step pipeline. The modular sub-workflow design makes the system more maintainable and testable.

The medium-priority issues identified are minor and do not block deployment. They primarily concern edge case handling and example coverage, which can be addressed incrementally as the workflows are used in practice.

Overall, these workflows demonstrate mature prompt engineering practices: clear structure, explicit branching, comprehensive examples, and thoughtful error handling. The consistency between nabledge-6 and nabledge-5 implementations is also commendable.

**Recommendation**: Approve for deployment with minor improvements tracked as follow-up tasks.
