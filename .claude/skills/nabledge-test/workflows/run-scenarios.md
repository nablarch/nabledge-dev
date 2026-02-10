# Run Scenarios Workflow

Execute test scenarios for specified nabledge skill version.

## Input

- **version**: Target nabledge skill version (e.g., "nabledge-6", "nabledge-5")

## Output

- Scenario result files in `results/YYYYMMDD-HHMM/<category>/<scenario-id>.md`
- Work log summary in `work/YYYYMMDD/scenario-test.md`

## Execution Steps

### 1. Parse Arguments and Setup

**1.1 Parse Version Argument**

Extract version from skill invocation:
```
/nabledge-test run-scenarios nabledge-6  → version="nabledge-6"
/nabledge-test run-scenarios nabledge-5  → version="nabledge-5"
```

If no version specified, ask user to select:
- nabledge-6
- nabledge-5 (if scenarios exist)
- nabledge-1.4 (if scenarios exist)

**1.2 Verify Scenarios Exist**

Check that `scenarios/{version}/` directory exists and contains scenario files:
```bash
ls .claude/skills/nabledge-test/scenarios/{version}/
```

If not found, display error:
```
Error: No scenarios found for {version}.

Available versions:
- nabledge-6

Please specify a valid version.
```

**1.3 Create Test Session Directory**

Create timestamped directory for test results:
```bash
timestamp=$(date '+%Y%m%d-%H%M')
mkdir -p .claude/skills/nabledge-test/results/${timestamp}
```

Record start time:
```bash
date '+%Y-%m-%d %H:%M:%S'
```

### 2. Load Scenario Files

**2.1 Find All Scenario Files**

```bash
find .claude/skills/nabledge-test/scenarios/{version}/ -name "*-scenarios.json"
```

**2.2 Parse Each Scenario File**

For each scenario file:
- Read JSON content
- Extract metadata (version, description, total_scenarios)
- Extract scenarios array
- Extract evaluation_criteria

### 3. Execute Scenarios

For each scenario in each scenario file:

**3.1 Prepare Scenario Context**

Extract from scenario JSON:
- id
- category
- question
- target_code or file (depending on workflow type)
- expected_components
- expected_knowledge
- expected_output_sections (if applicable)

**3.2 Determine Workflow Type**

Based on category:
- `code-analysis` → Use code-analysis workflow
- `handlers`, `libraries`, `tools`, `processing`, `adapters` → Use keyword-search workflow

**3.3 Execute Skill with Scenario**

Record start time:
```bash
start_time=$(date '+%Y-%m-%d %H:%M:%S')
```

Execute nabledge skill:

**For code-analysis scenarios**:
```
/{version} code-analysis

Target: {target_code}
Question: {question}
```

**For keyword-search scenarios**:
```
/{version} keyword-search

Question: {question}
```

Record end time:
```bash
end_time=$(date '+%Y-%m-%d %H:%M:%S')
```

**IMPORTANT**: Clear skill context between scenarios to ensure independent execution.

**3.4 Capture Execution Metrics**

Record the following:
- Start time
- End time
- Skill output
- Token usage (estimate from output length)
- Tool calls (count from skill output if visible)

**3.5 Generate Scenario Result File**

Use template from `templates/scenario-result.md` and populate with:
- Metadata (scenario ID, category, dates, times)
- Test input (question, target, expectations)
- Execution results (workflow steps, resource usage)
- Generated output (skill response)
- Evaluation against criteria (from scenario JSON)
- Issues found (manual review needed)
- Status (PASS/FAIL/PARTIAL based on criteria)

Save to:
```
.claude/skills/nabledge-test/results/{timestamp}/{category}/{scenario-id}.md
```

**3.6 Display Progress**

Show progress after each scenario:
```
[{current}/{total}] Completed: {scenario-id} ({status})
```

### 4. Generate Summary

**4.1 Calculate Statistics**

- Total scenarios executed
- Pass count
- Fail count
- Partial count
- Average token usage
- Average tool calls

**4.2 Create Work Log Summary**

Create `work/{YYYYMMDD}/scenario-test.md`:

```markdown
# Scenario Test: {version}

## Metadata

- Date: {date}
- Test Session: {timestamp}
- Total Scenarios: {total}

## Results

| Status | Count | Percentage |
|--------|-------|------------|
| Pass   | {pass_count} | {pass_percentage}% |
| Fail   | {fail_count} | {fail_percentage}% |
| Partial | {partial_count} | {partial_percentage}% |

## Key Findings

{list_of_major_issues}

## Details

Full test results: `.claude/skills/nabledge-test/results/{timestamp}/`

## Next Steps

{recommended_next_steps}
```

**4.3 Display Summary**

```
## Test Execution Complete

**Version**: {version}
**Test Session**: {timestamp}
**Total Scenarios**: {total}

**Results**:
- Pass: {pass_count}
- Fail: {fail_count}
- Partial: {partial_count}

**Pass Rate**: {pass_percentage}%

**Details**: .claude/skills/nabledge-test/results/{timestamp}/
**Work Log**: work/{YYYYMMDD}/scenario-test.md

To evaluate results and generate review:
/nabledge-test evaluate-results {timestamp}
```

## Error Handling

| Error | Response |
|-------|----------|
| Version not specified | Ask user to select version |
| Scenarios not found | Display error with available versions |
| Skill execution failed | Record as FAIL, continue with next scenario |
| Template not found | Display error and stop |

## Important Notes

1. **Context isolation**: Clear skill context between scenarios
2. **Independent execution**: Each scenario runs independently
3. **Record everything**: Capture all execution details for evaluation
4. **Progress feedback**: Show progress after each scenario
5. **Work log summary**: Create concise summary for daily work log
6. **Next step guidance**: Prompt user to run evaluate-results
