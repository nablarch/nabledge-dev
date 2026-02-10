# Run Scenarios Workflow

## Mission Success Criteria

You PASS this workflow if and only if:
1. Result file exists at `.claude/skills/nabledge-test/results/{timestamp}/{category}/{scenario_id}.md`
2. Work log exists at `work/{YYYYMMDD}/scenario-test.md`

If either file is missing when you finish, you FAILED.

---

## Input Parameters

- **version**: e.g., "6"
- **scenario_id**: e.g., "6-handlers-001"

---

## STEP 1: Setup

Create timestamp and directories:

```bash
timestamp=$(date '+%Y%m%d-%H%M') && \
mkdir -p .claude/skills/nabledge-test/results/${timestamp} && \
mkdir -p work/$(date '+%Y%m%d') && \
echo "${timestamp}" > /tmp/test_timestamp.txt && \
echo "TIMESTAMP: ${timestamp}"
```

Save the timestamp value.

---

## STEP 2: Load Scenario

Load scenario metadata using jq:

```bash
jq --arg id "6-handlers-001" '.scenarios[] | select(.id == $id)' .claude/skills/nabledge-test/scenarios/6/keyword-search.json
```

Extract these values:
- `id` → scenario_id
- `category` → category
- `question` → question
- `expected_keywords` → expected_keywords (array)

---

## STEP 3: Execute nabledge-6 Skill

⚠️ **Use Skill tool to invoke nabledge-6**

```
Skill tool:
  skill: "nabledge-6"
  args: "keyword-search

Question: {question from step 2}"
```

**Capture the COMPLETE output** from the Skill tool. Do not summarize.

---

## STEP 4: Evaluate Output

Check each keyword in `expected_keywords` against skill output (case-insensitive):
- Found → matched list
- Not found → missing list

Calculate:
- `matched_count` = matched list length
- `total_count` = expected_keywords length
- `match_percentage` = (matched_count / total_count) * 100

Determine status:
- If output contains "error" → `FAIL`
- Else if match_percentage >= 80 → `PASS`
- Else → `PARTIAL`

---

## STEP 5: CREATE RESULT FILE

⚠️ **DO THIS NOW. Use Write tool.**

Create directory:

```bash
timestamp=$(cat /tmp/test_timestamp.txt) && \
mkdir -p .claude/skills/nabledge-test/results/${timestamp}/{category}
```

Call Write tool:

**file_path**: `.claude/skills/nabledge-test/results/{timestamp}/{category}/{scenario_id}.md`

**content**:

```markdown
# Scenario Result: {scenario_id}

## Metadata

| Item | Value |
|------|-------|
| Scenario ID | {scenario_id} |
| Category | {category} |
| Test Date | {YYYY-MM-DD} |
| Status | {PASS/PARTIAL/FAIL} |

## Test Input

**Question**: {question}

## Evaluation

### Expected Keywords: {matched_count}/{total_count} ({match_percentage}%)

**Matched**:
- {keyword1}
- {keyword2}
...

**Missing**:
- {keyword1}
...

## Skill Output

```
{PASTE COMPLETE SKILL OUTPUT - DO NOT TRUNCATE}
```

## Status: {PASS/PARTIAL/FAIL}
```

Verify immediately:

```bash
timestamp=$(cat /tmp/test_timestamp.txt) && \
ls -lh .claude/skills/nabledge-test/results/${timestamp}/{category}/{scenario_id}.md
```

If ls fails, you FAILED. Stop and report error.

---

## STEP 6: CREATE WORK LOG

⚠️ **DO THIS NOW. Use Write tool.**

Call Write tool:

**file_path**: `work/{YYYYMMDD}/scenario-test.md` (e.g., work/20260210/scenario-test.md)

**content**:

```markdown
# Scenario Test: Nablarch {version}

## Metadata

- Date: {YYYY-MM-DD}
- Test Session: {timestamp}
- Total Scenarios: 1

## Results

| Status | Count |
|--------|-------|
| Pass   | {1 if PASS, else 0} |
| Fail   | {1 if FAIL, else 0} |
| Partial | {1 if PARTIAL, else 0} |

## Scenarios Executed

- {scenario_id}: {PASS/PARTIAL/FAIL}

## Details

Full test results: `.claude/skills/nabledge-test/results/{timestamp}/`

## Next Steps

Use `/nabledge-test evaluate-results {timestamp}` for detailed review.
```

Verify immediately:

```bash
ls -lh work/$(date '+%Y%m%d')/scenario-test.md
```

If ls fails, you FAILED. Stop and report error.

---

## STEP 7: Success Report

Verify both files exist:

```bash
timestamp=$(cat /tmp/test_timestamp.txt) && \
echo "=== RESULT FILE ===" && \
ls -lh .claude/skills/nabledge-test/results/${timestamp}/{category}/{scenario_id}.md && \
echo "=== WORK LOG ===" && \
ls -lh work/$(date '+%Y%m%d')/scenario-test.md && \
echo "=== SUCCESS ==="
```

Display:

```
## Test Execution Complete

✓ Test session: {timestamp}
✓ Scenario: {scenario_id}
✓ Status: {PASS/PARTIAL/FAIL}
✓ Keyword match: {matched_count}/{total_count} ({match_percentage}%)

**Files created**:
- Result: .claude/skills/nabledge-test/results/{timestamp}/{category}/{scenario_id}.md
- Work log: work/{YYYYMMDD}/scenario-test.md

**Next step**:
/nabledge-test evaluate-results {timestamp}
```

---

## Failure Recovery

If you reach this section without completing steps 5 and 6, you FAILED.
Report which files are missing and why.
