# Scenario Result: {scenario-id}

## Metadata

| Item | Value |
|------|-------|
| Scenario ID | {scenario-id} |
| Category | {category} |
| Test Date | {date} |
| Test Time | {time} |
| Duration | {duration}s |

## Test Input

### Question
```
{question}
```

### Target
```
{target_code or target_file}
```

### Expected Components
{expected_components_list}

### Expected Knowledge
{expected_knowledge_list}

## Execution Results

### Workflow Execution

| Step | Status | Details |
|------|--------|---------|
| Workflow Start | {status} | {details} |
| Target Identification | {status} | {details} |
| Dependency Analysis | {status} | {details} |
| Knowledge Retrieval | {status} | {details} |
| Output Generation | {status} | {details} |

### Resource Usage

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Tokens | {tokens} | {target_range} | {pass/fail} |
| Tool Calls | {tool_calls} | {target_range} | {pass/fail} |
| Execution Time | {time}s | - | - |

### Tool Calls Summary

{list of tool calls with parameters}

## Generated Output

### Output Sections Present

- [ ] Overview
- [ ] Architecture (if applicable)
- [ ] Components
- [ ] Flow
- [ ] Nablarch Framework Usage

### Output Content

```markdown
{actual_output_content}
```

## Evaluation Against Criteria

### Workflow Execution
{evaluation_details}

### Code Explanation Output (code-analysis only)
{evaluation_details}

### Keyword Matching (keyword-search only)
{evaluation_details}

### Knowledge Integration
{evaluation_details}

### Section Relevance
{evaluation_details}

### Token Efficiency
{evaluation_details}

### Tool Call Efficiency
{evaluation_details}

## Issues Found

{list of issues}

## Status

**Overall Result**: {PASS/FAIL/PARTIAL}

## Notes

{additional_notes}
