# Run Scenarios Workflow

Execute test scenarios for specified nabledge skill version.

## Your Mission

You are a **Test Executor** for the nabledge skill. Your job:
1. Load a test scenario from JSON
2. Call the nabledge skill using the Skill tool
3. Capture its output
4. Evaluate the output
5. Save results to files

**Success criteria**: Two files created:
- Result file: `.claude/skills/nabledge-test/results/{timestamp}/{category}/{scenario_id}.md`
- Work log: `work/{YYYYMMDD}/scenario-test.md`

---

## Input

- **version**: "6" or "5"
- **scenario_id**: (Optional) Specific scenario to test, or null for all

## Output

- Scenario result files in `results/YYYYMMDD-HHMM/<category>/<scenario-id>.md`
- Work log summary in `work/YYYYMMDD/scenario-test.md`

---

## Execution Checklist

Use this checklist to ensure you complete all steps:

- [ ] 1. Create test session directory with timestamp
- [ ] 2. Load scenario from JSON file
- [ ] 3. **Execute nabledge skill** using Skill tool (not direct answer)
- [ ] 4. Capture complete skill output (do not summarize)
- [ ] 5. Evaluate output (check sections, keywords)
- [ ] 6. **Create result file** using Write tool
- [ ] 7. **Create work log** using Write tool
- [ ] 8. Display summary to user

---

## Step-by-Step Execution

### Step 1: Setup

**1.1 Verify scenarios directory exists**

```bash
ls .claude/skills/nabledge-test/scenarios/${version}/
```

Expected: `code-analysis.json`, `keyword-search.json`

If not found:
```
Error: No scenarios found for version {version}.
Available versions: 6 (Nablarch 6)
```

**1.2 Create test session directory**

```bash
timestamp=$(date '+%Y%m%d-%H%M')
mkdir -p .claude/skills/nabledge-test/results/${timestamp}
echo "Test session: ${timestamp}"
```

Example output: `Test session: 20260210-2045`

---

### Step 2: Load Scenario

**2.1 Determine scenario file from ID pattern**

For scenario ID like `6-handlers-001`:
- Extract version: `6`
- Extract category: `handlers`
- Map to file: `handlers` → `keyword-search.json`

Mapping rules:
- `code-analysis` → `code-analysis.json`
- `handlers`, `libraries`, `tools`, `processing`, `adapters` → `keyword-search.json`

```bash
# Example for 6-handlers-001
scenario_file=".claude/skills/nabledge-test/scenarios/6/keyword-search.json"
```

**2.2 Extract scenario data using jq**

```bash
scenario_json=$(jq --arg id "6-handlers-001" '.scenarios[] | select(.id == $id)' "${scenario_file}")
category=$(echo "${scenario_json}" | jq -r '.category')
question=$(echo "${scenario_json}" | jq -r '.question')
```

Example output:
```
category: handlers
question: データリードハンドラでファイルを読み込むにはどうすればいいですか？
```

**2.3 Verify scenario exists**

If not found:
```bash
echo "Error: Scenario '6-handlers-001' not found."
echo "Available scenarios:"
jq -r '.scenarios[].id' scenarios/6/*.json | sort
```

---

### Step 3: Execute Nabledge Skill

**⚠️ CRITICAL: Use Skill tool, not direct answer**

You must invoke the nabledge skill. Do NOT answer the question yourself.

**3.1 Determine workflow type**

Based on category:
- `code-analysis` → use `code-analysis` workflow
- `handlers`, `libraries`, `tools`, `processing`, `adapters` → use `keyword-search` workflow

**3.2 Call Skill tool**

Record start time, then call Skill:

```bash
start_time=$(date '+%Y-%m-%d %H:%M:%S')
```

**For keyword-search (handlers, libraries, etc.):**
```
Skill
  skill: "nabledge-6"
  args: "keyword-search

Question: データリードハンドラでファイルを読み込むにはどうすればいいですか？"
```

**For code-analysis:**
```
Skill
  skill: "nabledge-6"
  args: "code-analysis

Target: path/to/file.java
Question: この処理の構造を説明してください"
```

**3.3 Capture skill output**

Store the **complete output** from the Skill tool. This will be evaluated in the next step.

Example of what you'll receive:
```
## データリードハンドラでファイルを読み込む方法

DataReadHandlerでファイルを読み込むには...
[長い説明が続く]
```

Record end time:
```bash
end_time=$(date '+%Y-%m-%d %H:%M:%S')
```

---

### Step 4: Evaluate Output

**4.1 Check expected sections (if defined in scenario)**

```bash
# Extract expected sections from scenario JSON
expected_sections=$(echo "${scenario_json}" | jq -r '.expected_output_sections[]? // empty')
```

For each expected section, check if it appears in the skill output:
- Look for markdown headers like `## 概要`, `## 実装手順`
- Count found vs. missing sections

**4.2 Check expected keywords (if defined in scenario)**

```bash
expected_keywords=$(echo "${scenario_json}" | jq -r '.expected_keywords[]? // empty')
```

For each keyword, check if it appears in the skill output (case-insensitive).

Calculate match rate: `keyword_found / keyword_total * 100`

**4.3 Determine status**

Logic:
- Status starts as `PASS`
- If keyword match rate < 80%: `PARTIAL`
- If expected sections are missing: `PARTIAL`
- If skill output contains "error" or "failed": `FAIL`

---

### Step 5: Create Result File

**⚠️ MANDATORY: Use Write tool to create this file**

**5.1 Create result directory**

```bash
result_dir=".claude/skills/nabledge-test/results/${timestamp}/${category}"
mkdir -p "${result_dir}"
```

Example: `.claude/skills/nabledge-test/results/20260210-2045/handlers/`

**5.2 Build file path**

```bash
result_file_path="${result_dir}/${scenario_id}.md"
```

Example: `.claude/skills/nabledge-test/results/20260210-2045/handlers/6-handlers-001.md`

**5.3 Write result file**

Use Write tool with this content (substitute actual values):

```markdown
# Scenario Result: 6-handlers-001

## Metadata

| Item | Value |
|------|-------|
| Scenario ID | 6-handlers-001 |
| Category | handlers |
| Test Date | 2026-02-10 |
| Test Time | 20:45:32 |
| Status | PASS |

## Test Input

**Question**: データリードハンドラでファイルを読み込むにはどうすればいいですか？

**Target**: N/A

## Execution Results

### Expected Sections

- Overview
- Implementation Steps
- Example Code

### Expected Keywords

5/6 (83%)

### Matched Keywords
- DataReadHandler
- ファイル読み込み
- ObjectMapper
- BatchAction
- createReader

### Missing Keywords
- None

## Skill Output

```
[Complete output from nabledge-6 skill goes here]
```

## Evaluation

### Status Determination

- Keyword match rate: 83% (≥80%) ✓
- Expected sections: All found ✓
- No errors detected ✓

Result: PASS

## Status: PASS
```

**5.4 Verify file created**

```bash
ls -lh "${result_file_path}"
```

Expected output: `-rw-r--r-- 1 user user 12K Feb 10 20:45 .../6-handlers-001.md`

---

### Step 6: Create Work Log

**⚠️ MANDATORY: Use Write tool to create this file**

**6.1 Create work log directory**

```bash
work_log_dir="work/$(date '+%Y%m%d')"
mkdir -p "${work_log_dir}"
```

Example: `work/20260210/`

**6.2 Calculate statistics**

For single scenario mode:
- Total: 1
- Pass/Fail/Partial: Based on status from Step 4.3

For all scenarios mode:
- Count results by status
- Calculate percentages

**6.3 Write work log**

Use Write tool at `work/20260210/scenario-test.md`:

```markdown
# Scenario Test: Nablarch 6

## Metadata

- Date: 2026-02-10
- Test Session: 20260210-2045
- Total Scenarios: 1

## Results

| Status | Count | Percentage |
|--------|-------|------------|
| Pass   | 1     | 100%       |
| Fail   | 0     | 0%         |
| Partial | 0    | 0%         |

## Scenarios Executed

- 6-handlers-001: PASS

## Key Findings

All tests passed successfully. The nabledge-6 skill correctly answered questions about DataReadHandler file reading.

## Details

Full test results: `.claude/skills/nabledge-test/results/20260210-2045/`

## Next Steps

- Review result file for detailed output
- Run additional scenarios if needed
- Use `/nabledge-test evaluate-results 20260210-2045` for detailed review
```

---

### Step 7: Display Summary

Show this summary to the user:

```
## Test Execution Complete

✓ Test session: 20260210-2045
✓ Scenarios executed: 1
✓ Status: 1 PASS, 0 FAIL, 0 PARTIAL

**Results**:
- Result file: .claude/skills/nabledge-test/results/20260210-2045/handlers/6-handlers-001.md
- Work log: work/20260210/scenario-test.md

**Next step**:
/nabledge-test evaluate-results 20260210-2045
```

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Scenario file not found | Display error with available scenario IDs |
| Scenario ID not in JSON | List all available IDs from that version |
| Skill tool fails | Record status as FAIL, capture error in result file, continue workflow |
| Cannot create result file | Display error, show file path, exit |
| Cannot create work log | Display error, show directory path, exit |

---

## Examples

### Example 1: Single Scenario Success

Input: `version=6`, `scenario_id=6-handlers-001`

Flow:
1. Create `.claude/skills/nabledge-test/results/20260210-2045/`
2. Load from `scenarios/6/keyword-search.json`
3. Call `Skill tool: nabledge-6 keyword-search`
4. Capture output (2000 characters)
5. Evaluate: 5/6 keywords found (83%), PASS
6. Write `.../handlers/6-handlers-001.md` (3KB)
7. Write `work/20260210/scenario-test.md` (500 bytes)
8. Display summary

Output files:
- `.claude/skills/nabledge-test/results/20260210-2045/handlers/6-handlers-001.md` ✓
- `work/20260210/scenario-test.md` ✓

### Example 2: Scenario Not Found

Input: `version=6`, `scenario_id=6-invalid-999`

Flow:
1. Try to load from JSON
2. Not found
3. Display error:
```
Error: Scenario '6-invalid-999' not found.

Available scenarios:
6-adapters-001
6-code-analysis-001
6-code-analysis-002
6-handlers-001
6-libraries-001
...
```

---

## Common Mistakes to Avoid

1. ❌ Answering the scenario question yourself instead of calling Skill tool
2. ❌ Summarizing or filtering the skill output instead of capturing it completely
3. ❌ Forgetting to create result files using Write tool
4. ❌ Creating result files but forgetting work log
5. ❌ Not using absolute paths for file operations
6. ❌ Not verifying files were actually created

## Success Checklist (Final)

Before reporting completion, verify:

✅ Test session directory created
✅ Scenario loaded from JSON
✅ Skill tool invoked (not direct answer)
✅ Skill output captured completely
✅ Evaluation performed (sections, keywords, status)
✅ Result file created using Write tool
✅ Work log created using Write tool
✅ Summary displayed to user

If all checkboxes are checked, the test run was successful.
