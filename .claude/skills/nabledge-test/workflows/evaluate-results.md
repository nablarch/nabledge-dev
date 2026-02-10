# Evaluate Results Workflow

Evaluate test results and generate review report with improvement recommendations.

## Input

- **test_session_dir**: Path to test session directory (e.g., "results/20260210-1430" or "20260210-1430")

## Output

- Review reports in test session directory:
  - `{scenario-file-name}-review.md` for each scenario file

## Execution Steps

### 1. Parse Arguments and Setup

**1.1 Parse Test Session Directory**

Extract test session directory from skill invocation:
```
/nabledge-test evaluate-results results/20260210-1430  → dir="results/20260210-1430"
/nabledge-test evaluate-results 20260210-1430          → dir="results/20260210-1430"
```

If no directory specified, list available sessions and ask user to select:
```bash
ls -d .claude/skills/nabledge-test/results/*/
```

**1.2 Verify Session Directory Exists**

Check that test session directory exists:
```bash
ls .claude/skills/nabledge-test/results/{timestamp}/
```

If not found, display error:
```
Error: Test session directory not found: {test_session_dir}

Available test sessions:
{list_of_available_sessions}

Please specify a valid test session directory.
```

### 2. Load Scenario Files and Results

**2.1 Identify Scenario Files**

Find all unique scenario file names from result files:
```bash
find .claude/skills/nabledge-test/results/{timestamp}/ -name "*.md" -type f
```

Extract scenario file names (e.g., "code-analysis", "keyword-search").

**2.2 Load Original Scenario Definitions**

For each identified scenario file:
- Determine version from session (check which version's scenarios were used)
- Load original scenario JSON file from `scenarios/{version}/{scenario-file-name}-scenarios.json`
- Extract evaluation criteria

**2.3 Load All Result Files**

For each scenario file:
- Find all result files in `results/{timestamp}/{category}/`
- Parse each result file to extract:
  - Scenario ID
  - Status (PASS/FAIL/PARTIAL)
  - Execution metrics (tokens, tool calls)
  - Issues found
  - Generated output

### 3. Analyze Results

For each scenario file:

**3.1 Calculate Statistics**

- Total scenarios
- Pass count / percentage
- Fail count / percentage
- Partial count / percentage
- Average token usage
- Token usage range (min/max)
- Average tool calls
- Tool calls range (min/max)

**3.2 Evaluate Each Scenario Against Criteria**

From original scenario JSON `evaluation_criteria`:

**Workflow Execution**:
- Check if expected workflow was executed
- Verify required steps were completed
- Assess tool usage appropriateness

**Output Quality** (for code-analysis):
- Verify expected output sections present
- Check for Mermaid diagrams
- Validate component explanations
- Confirm source code links
- Confirm knowledge file links

**Keyword Matching** (for keyword-search):
- Calculate keyword match percentage
- Identify missing keywords

**Knowledge Integration**:
- Verify expected knowledge files were referenced
- Check knowledge content was properly cited
- Assess code-knowledge correspondence

**Section Relevance** (for keyword-search):
- Verify expected sections were identified
- Check high-relevance sections prioritized

**Knowledge File Only** (for keyword-search):
- Confirm no LLM training data used
- Verify no external knowledge added
- Check only knowledge file content used

**Token Efficiency**:
- Compare actual vs target token range
- Calculate efficiency percentage

**Tool Call Efficiency**:
- Compare actual vs target tool call range
- Calculate efficiency percentage

**3.3 Identify Common Issues**

Group issues across scenarios by:
- Issue type (workflow, output, knowledge, efficiency)
- Frequency (how many scenarios affected)
- Severity (impact on results)

Categorize by priority:
- **High**: Affects multiple scenarios, significant impact
- **Medium**: Affects some scenarios, moderate impact
- **Low**: Affects few scenarios, minor impact

### 4. Generate Improvement Recommendations

**4.1 Skill Structure Improvements**

Analyze patterns and recommend:
- Knowledge file additions/updates
- Workflow refinements
- Tool usage optimizations
- Context management improvements

**4.2 Workflow Improvements**

Recommend:
- Step sequence optimization
- Decision logic refinement
- Error handling enhancement
- Context efficiency improvements

**4.3 Knowledge File Improvements**

For each knowledge file with issues:
- Identify missing information
- Suggest content additions
- Recommend structure improvements
- Propose example enhancements

**4.4 Performance Optimization**

Token usage optimization:
- Identify verbose outputs
- Suggest content reduction strategies
- Recommend context management improvements

Tool call optimization:
- Identify redundant calls
- Suggest call consolidation
- Recommend caching strategies

### 5. Generate Review Report

**5.1 Create Review File**

Use template from `templates/review.md` and populate with:

- **Test Session Metadata**: Date, time, directory, counts
- **Summary**: Overall assessment, pass rates by category
- **Detailed Results**: Each scenario with strengths, issues, metrics
- **Common Issues**: Grouped by priority with recommendations
- **Improvement Recommendations**: By area (skill, workflow, knowledge, performance)
- **Action Items**: Categorized by urgency (Immediate/Short-term/Long-term)
- **Next Steps**: Recommended actions

Save to:
```
.claude/skills/nabledge-test/results/{timestamp}/{scenario-file-name}-review.md
```

**5.2 Generate One Review Per Scenario File**

Create separate review for:
- code-analysis-scenarios-review.md
- keyword-search-scenarios-review.md
- (future scenario files)

### 6. Display Summary

```
## Evaluation Complete

**Test Session**: {timestamp}
**Scenario Files Evaluated**: {count}

**Overall Results**:
- Pass Rate: {overall_pass_percentage}%
- Average Token Usage: {avg_tokens}
- Average Tool Calls: {avg_calls}

**Generated Reviews**:
- {scenario-file-1}-review.md
- {scenario-file-2}-review.md

**Top Priority Issues** ({count}):
1. {issue_1}
2. {issue_2}
3. {issue_3}

**Review Reports**: .claude/skills/nabledge-test/results/{timestamp}/

**Recommended Next Steps**:
{next_steps_list}
```

## Error Handling

| Error | Response |
|-------|----------|
| Session directory not specified | List available sessions, ask user to select |
| Session directory not found | Display error with available sessions |
| Result files missing | Display error, suggest re-running tests |
| Template not found | Display error and stop |
| Scenario JSON not found | Display warning, use default criteria |

## Important Notes

1. **Objective evaluation**: Use criteria from scenario JSON files
2. **Pattern recognition**: Identify common issues across scenarios
3. **Actionable recommendations**: Provide specific, implementable suggestions
4. **Priority guidance**: Categorize issues and actions by priority/urgency
5. **Comprehensive coverage**: Evaluate all aspects (workflow, output, knowledge, efficiency)
6. **Clear reporting**: Use consistent format across all reviews
