---
name: nabledge-test
description: Benchmark framework for nabledge skills. Runs scenarios in isolated sub-agent contexts to eliminate bias. Supports baseline mode for improvement verification.
---

# Nabledge-Test

Benchmark framework for nabledge skills. Detects expected keywords/components and measures performance metrics.
Each scenario runs in an isolated sub-agent context (Task tool) to eliminate cross-scenario bias.

## Usage

```bash
nabledge-test 6 qa-001                          # Single scenario (1 trial)
nabledge-test 6 --all                           # All scenarios (1 trial each)
nabledge-test 6 --list                          # List all scenarios
nabledge-test 6 qa-001 --trials 3               # Single scenario (3 trials)
nabledge-test 6 --all --trials 5                # All scenarios (5 trials each)
nabledge-test 6 "知識検索系を全部実行して"        # Free-form instruction
nabledge-test 6 --baseline                      # Baseline mode: run all, save baseline, generate comparison report
```

**Trial count**: Use `--trials N` to run each scenario N times (default: 1). In `--baseline` mode, `--trials` is ignored — coverage scenarios run 1 trial, benchmark scenarios run 3 trials (fixed).

## Key Principles

- **Measure everything, judge nothing**: Report detection rates and measured values without arbitrary targets
- **Isolated execution**: Each scenario runs in a separate Task tool context to prevent cross-contamination
- **Measurement discipline**: You are a measurement instrument, not a helper

### Measurement Discipline Rules

- Follow target skill workflows exactly — do NOT improvise
- Record actual execution — do NOT fabricate steps
- Let failures be failures — do NOT mask with workarounds
- Always complete the measurement — do NOT stop execution early
- No self-imposed limits — token usage and execution time may vary significantly (3,000-70,000+)

## When invoked

### Step 1: Parse arguments

Format: `nabledge-test <version> [<scenario-id> | --all | --list | --baseline | "<free-form>"] [--trials N]`

**If no arguments provided**: Display usage and exit.

```
Usage: nabledge-test <version> [<scenario-id> | --all | --list | --baseline | "<free-form>"] [--trials N]

Examples:
  nabledge-test 6 qa-001                          # Single scenario (1 trial)
  nabledge-test 6 --all                           # All scenarios (1 trial each)
  nabledge-test 6 --list                          # List all available scenarios
  nabledge-test 6 --baseline                      # Baseline mode (all scenarios, save + compare)
  nabledge-test 6 qa-001 --trials 3               # Single scenario (3 trials)
  nabledge-test 6 --all --trials 5                # All scenarios (5 trials each)
  nabledge-test 6 "知識検索系を全部実行して"        # Free-form instruction

Arguments:
  <version>              Required. Version number (6 or 5)
  <scenario-id>          Optional. Specific scenario to test (e.g., qa-001, ca-001)
  --all                  Optional. Test all scenarios
  --list                 Optional. List all available scenarios
  --baseline             Optional. Baseline mode: run all scenarios, save to baseline/, generate comparison
  "<free-form>"          Optional. Free-form instruction for test selection
  --trials N             Optional. Number of trials per scenario (default: 1)
```

**If `--list` is provided**: Display scenario list and exit.

1. Read scenarios file: `.claude/skills/nabledge-test/scenarios/nabledge-<version>/scenarios.json`
2. Group scenarios by type (qa-* for qa, ca-* for code-analysis)
3. Display formatted list:

```
Available scenarios for nabledge-<version>:

QA - <count> scenarios:
  - qa-001: <question>
  - qa-002: <question>

Code Analysis (CA) - <count> scenarios:
  - ca-001: <question>
  - ca-002: <question>

Total: <total_count> scenarios
```

**Parse modes**:

| Argument | Mode | Scenarios | Baseline |
|----------|------|-----------|----------|
| `qa-001` | single | 1個 | No |
| `--all` | all | 全件 | No |
| `--baseline` | baseline | 全件 | Yes |
| `"free text"` | free-form | AI判断 | No |

**`--baseline` execution plan** (fixed, `--trials` ignored):
- **Coverage scenarios** (`"benchmark": false/absent`): 1 trial each — coverage run, regression detection
- **Benchmark scenarios** (`"benchmark": true`): 3 trials each — quality measurement with statistical rigor

### Step 2: Resolve issue number

Issue番号は作業記録の保存先 `.work/xxxxx/` を決定するために必要。

**Resolve from current branch name**:

```bash
# Get current branch name
branch=$(git rev-parse --abbrev-ref HEAD)

# Extract issue number from branch name pattern: <number>-<description>
# Examples: 125-improve-search-performance → 00125
#           88-redesign-index-hints → 00088
issue_number=$(echo "$branch" | grep -oP '^\d+' | xargs printf '%05d')

# Verify .work directory exists
if [ ! -d ".work/${issue_number}" ]; then
  mkdir -p ".work/${issue_number}"
fi
```

**If branch is `main` or has no number prefix**: Use `00000` as fallback and warn the user.

Store as `$ISSUE_NUMBER` (5-digit zero-padded string) for use in subsequent steps.

### Step 3: Load scenarios

From `.claude/skills/nabledge-test/scenarios/nabledge-<version>/scenarios.json`:

`expectations` is an object with aspect keys. Each item in an aspect is either a string (AND: must appear) or an array of strings (OR: any one must appear). A single aspect can mix both types — each item is evaluated independently.

```json
{
  "id": "qa-001",
  "question": "コード値のプルダウン入力を実装するには？",
  "expectations": {
    "code_select_tag": ["n:codeSelect", "codeId"],
    "general_select_tag": ["n:select", ["elementValueProperty", "elementLabelProperty"]],
    "concepts": ["コード値"]
  }
}
```

For code-analysis scenarios (ca-*), additional fields:
```json
{
  "id": "ca-001",
  "question": "ExportProjectsInPeriodActionの実装を理解したい",
  "target_file": "path/to/file.java",
  "expectations": {
    "overview": ["ClassName1", "concept1"],
    "class_diagram": {
      "classes": ["ClassName1", "ClassName2"],
      "relationships": ["ClassA --|> ClassB"]
    },
    "component_summary": ["ClassName1", "ClassName2"],
    "processing_flow": ["methodName1", "keyword1"],
    "sequence_diagram": {
      "objects": ["ObjectName1", "ObjectName2"],
      "messages": ["methodCall1", "methodCall2"]
    },
    "nablarch_usage": ["NablarchClass1", "NablarchClass2"],
    "output": ["Component Summary", "Nablarch Framework Usage", ".nabledge/"]
  }
}
```

**Build detection items**:

For qa (qa-*):
```
detection_items = []
for aspect, items in scenario.expectations.items():
    for item in items:
        if isinstance(item, list):
            # OR condition: any one of these must appear in response
            detection_items.append(f"Response includes one of: {', '.join(repr(k) for k in item)}")
        else:
            detection_items.append(f"Response includes '{item}'")
```

For code-analysis (ca-*):
```
detection_items = []
for keyword in scenario.expectations.overview:
    detection_items.append(f"Overview includes '{keyword}'")
for class_name in scenario.expectations.class_diagram.classes:
    detection_items.append(f"Class diagram includes class '{class_name}'")
for relationship in scenario.expectations.class_diagram.relationships:
    detection_items.append(f"Class diagram includes relationship '{relationship}'")
for component in scenario.expectations.component_summary:
    detection_items.append(f"Component Summary includes '{component}'")
for keyword in scenario.expectations.processing_flow:
    detection_items.append(f"Processing Flow includes '{keyword}'")
for object_name in scenario.expectations.sequence_diagram.objects:
    detection_items.append(f"Sequence diagram includes object '{object_name}'")
for message in scenario.expectations.sequence_diagram.messages:
    detection_items.append(f"Sequence diagram includes message '{message}'")
for class_name in scenario.expectations.nablarch_usage:
    detection_items.append(f"Nablarch Framework Usage includes '{class_name}'")
for item in scenario.expectations.output:
    detection_items.append(f"Output includes '{item}'")
```

### Step 4: Execute scenarios via sub-agents

**Before launching sub-agents**, capture the run timestamp once:

```bash
RUN_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
WORKSPACE=".tmp/nabledge-test/run-${RUN_TIMESTAMP}"
mkdir -p "${WORKSPACE}"
```

Use `$RUN_TIMESTAMP` and `$WORKSPACE` consistently in all subsequent steps (Step 5, Step 9c).

**CRITICAL**: Each scenario MUST run in a separate Task tool invocation. This ensures:
- No context bleeding between scenarios (bias elimination)
- Each scenario starts from a clean state
- Metrics reflect true isolated performance

**For each scenario**, spawn a Task tool with the following prompt:

```
You are a measurement instrument executing a nabledge skill test.

## Rules
- Follow target skill workflows EXACTLY — do NOT improvise
- Record actual execution — do NOT fabricate steps
- Let failures be failures — do NOT mask with workarounds
- Complete all steps without stopping
- No self-imposed limits on token usage or execution time

## Task
1. Read `.claude/skills/nabledge-<version>/SKILL.md` and follow its instructions
2. Execute the following question: "<scenario.question>"
3. Record timing for each step (use `date '+%Y-%m-%dT%H:%M:%S'`)

## Output
When complete, output the following clearly delimited sections:

### RESPONSE_START
<paste the complete response/answer from nabledge-<version> here>
### RESPONSE_END

### METRICS_START
```json
{
  "total_duration_seconds": <number>,
  "steps": [
    {
      "step": <number>,
      "name": "<step name>",
      "duration_seconds": <number>,
      "in_tokens_estimate": <number>,
      "out_tokens_estimate": <number>
    }
  ],
  "tool_calls": {
    "Read": <count>,
    "Bash": <count>,
    "Grep": <count>,
    "Write": <count>
  },
  "total_tool_calls": <number>,
  "response_chars": <number>
}
```
### METRICS_END

### OUTPUT_FILES_START
<list any files created by the skill, with their full paths, one per line>
<if no files created, write "none">
### OUTPUT_FILES_END
```

**Execution strategy — parallel batches**:

Run scenarios in two parallel batches to minimize total execution time:

**Batch 1 — Coverage run** (all coverage scenarios in parallel):
- Launch ALL coverage scenarios (`"benchmark": false/absent`) simultaneously as separate Task tools
- Wait for all to complete, then save results and run detection checks

**Batch 2 — Benchmark run** (all benchmark trials in parallel):
- Launch ALL trials for ALL benchmark scenarios simultaneously
  - e.g., qa-001 trial 1, qa-001 trial 2, qa-001 trial 3, ca-003 trial 1, ca-003 trial 2, ca-003 trial 3 — all 6 at once
- Wait for all to complete, then save results and compute statistics

**In `--baseline` mode — execution order**:

1. Run all **coverage scenarios** × 1 trial (parallel batch)
2. Run all **benchmark scenarios** × 3 trials (parallel batch — all trials for all benchmark scenarios at once)

Trial 1 of each benchmark scenario serves as the canonical result (grading.json / metrics.json). All 3 trials are used for benchmark statistics.

**For multiple trials** (`--trials N`):

- Launch all N trials for a scenario simultaneously as separate Task tools
- Wait for all to complete, then collect results

**After all Tasks in a batch complete**:

1. For each Task result: parse the delimited output sections (RESPONSE, METRICS, OUTPUT_FILES)
2. Save results to the workspace (see Step 5)
3. Run detection check (see Step 6)

### Step 5: Save workspace results

**Workspace location**: `$WORKSPACE` (`.tmp/nabledge-test/run-<RUN_TIMESTAMP>/`, captured in Step 4 before execution)

For each completed scenario:

```
.tmp/nabledge-test/run-<RUN_TIMESTAMP>/
  <scenario-id>/
    response.md          # Full response text from RESPONSE section
    metrics.json         # Parsed from METRICS section
    grading.json         # Detection check results (Step 6)
    output/              # Output files (ca-* only, copied from paths in OUTPUT_FILES)
```

**Save response.md**: Extract text between `### RESPONSE_START` and `### RESPONSE_END`.

**Save metrics.json**: Parse JSON from between `### METRICS_START` and `### METRICS_END`. If parsing fails (sub-agent didn't output clean JSON), extract what's available and note the error.

**Save output files** (ca-* scenarios only): Copy files listed in OUTPUT_FILES section to `output/` directory. For benchmark trials, also copy to `trials/<N>/output/` directory.

**For benchmark scenarios** (in `--baseline` mode): After saving the canonical grading.json and metrics.json (trial 1):

1. Save each trial under `trials/<N>/`:
   ```
   .tmp/nabledge-test/run-<RUN_TIMESTAMP>/<scenario-id>/
     grading.json          # trial 1 (canonical for wide comparison)
     metrics.json          # trial 1 (canonical for wide comparison)
     trials/
       1/grading.json
       1/metrics.json
       1/output/           # ca-* only: output files for this trial
       2/grading.json
       2/metrics.json
       2/output/           # ca-* only: output files for this trial
       3/grading.json
       3/metrics.json
       3/output/           # ca-* only: output files for this trial
   ```

2. Compute and save `benchmark.json`:
   - Collect per-trial detection rate: `rate_i = grading[i]["summary"]["detection_rate"]`
   - Compute statistics (t-distribution, df=2, t=4.303 for 95% CI):
   ```json
   {
     "scenario_id": "<id>",
     "trials": 3,
     "detection_rates": [0.875, 1.0, 0.875],
     "mean": 0.xxx,
     "std": 0.xxx,
     "ci_95_low": 0.xxx,
     "ci_95_high": 0.xxx
   }
   ```
   Formula: `margin = 4.303 × std / sqrt(3)`, `ci_95_low = mean - margin`, `ci_95_high = mean + margin` (clamp to [0, 1])

### Step 6: Check detection items

For each scenario, evaluate detection items against the response:

**QA (qa-*)**:

```python
for item in detection_items:
    if "includes one of:" in item:
        # OR condition: extract all quoted keywords, detected if any match
        # Format: "Response includes one of: 'kw1', 'kw2'"
        keywords = re.findall(r"'([^']+)'", item)
        detected = any(k in response_text for k in keywords)
    elif "includes" in item:
        keyword = extract_keyword(item)  # e.g., "DataReadHandler"
        detected = keyword in response_text
    elif "references" in item:
        section = extract_section(item)  # e.g., "request-path"
        detected = section in response_text
```

**Code-analysis (ca-*)**:

Each detection item is checked by examining response text and output files. **CRITICAL**: For section-based checks, always read from the actual output Markdown files (e.g., `code-analysis-*.md`), NOT just `response.md`. This ensures accurate detection even when the agent writes to external files.

Search order:
1. Read all `.md` files in the output directory (e.g., `code-analysis-*.md`)
2. Fall back to `response.md` only if output files don't exist
3. Concatenate all sources before performing detection

Detection logic:
- "Overview includes 'X'" → check if keyword X appears within the `## Overview` section (read from output files first)
- "Class diagram includes class 'X'" → check if class name X appears within a `classDiagram` block (read from output files first)
- "Class diagram includes relationship 'X'" → check if relationship string X appears within a `classDiagram` block (read from output files first)
- "Component Summary includes 'X'" → check if component name X appears within the `### Component Summary` section (read from output files first)
- "Processing Flow includes 'X'" → check if keyword X appears within the `### Processing Flow` section (read from output files first)
- "Sequence diagram includes object 'X'" → check if participant/object X appears within a `sequenceDiagram` block (read from output files first)
- "Sequence diagram includes message 'X'" → check if message/method call X appears within a `sequenceDiagram` block (read from output files first)
- "Nablarch Framework Usage includes 'X'" → check if class name X appears as a heading within the `## Nablarch Framework Usage` section (read from output files first)
- "Output includes 'X'" → check output files or response for X

**Implementation for Code-Analysis scenarios**:

When checking CA detection items:
1. List all files in the output directory (e.g., `output/code-analysis-*.md`)
2. If output files exist, read them; otherwise fall back to `response.md`
3. For section-based items (Overview, Class diagram, etc.), extract the relevant section and perform keyword search
4. Example extraction:
   ```python
   # Read all .md files from output directory
   output_dir = Path(workspace) / scenario_id / "output"
   output_text = ""
   if output_dir.exists():
       for f in sorted(output_dir.glob("*.md")):
           with open(f) as file:
               output_text += file.read() + "\n"
   else:
       # Fall back to response.md
       with open(Path(workspace) / scenario_id / "response.md") as f:
           output_text = f.read()
   
   # Extract section and check for keyword
   # Example: for "Overview includes 'X'", extract text between "## Overview" and next heading
   ```

**Write grading.json**:

```json
{
  "scenario_id": "<id>",
  "detection_items": [
    {
      "text": "Overview includes 'BusinessDateUtil'",
      "detected": true,
      "evidence": "Found in ## Overview section of code-analysis-*.md"
    },
    {
      "text": "Nablarch Framework Usage includes 'ParameterizedSqlPStatement'",
      "detected": false,
      "evidence": "Not found as heading in ## Nablarch Framework Usage section"
    }
  ],
  "summary": {
    "detected": 5,
    "not_detected": 1,
    "total": 6,
    "detection_rate": 0.833
  }
}
```

### Step 7: Generate individual scenario reports and aggregate report

Compute `RUN_TIMESTAMP_SHORT` from `RUN_TIMESTAMP` (remove the hyphen, take the first 12 characters):
- Example: `20260307-120822` → `202603071208`

Run the report generation script:

```bash
python .claude/skills/nabledge-test/scripts/generate_reports.py \
  --workspace "${WORKSPACE}" \
  --scenarios ".claude/skills/nabledge-test/scenarios/nabledge-${VERSION}/scenarios.json" \
  --output-dir ".tmp/nabledge-test/.work/${ISSUE_NUMBER}/${RUN_TIMESTAMP_SHORT}/" \
  --report-path ".tmp/nabledge-test/.work/${ISSUE_NUMBER}/report-${RUN_TIMESTAMP_SHORT}.md" \
  --version "${VERSION}" \
  --branch "$(git rev-parse --abbrev-ref HEAD)" \
  --commit "$(git rev-parse --short HEAD)" \
  --run-timestamp "${RUN_TIMESTAMP}" \
  --trials "${TRIALS}"
```

This generates:
- Individual reports: `.work/<ISSUE_NUMBER>/nabledge-test/<YYYYMMDDHHMM>/<scenario-id>.md`
  - All fields populated from grading.json and metrics.json
  - 目視判定 table left blank (for manual review by kiyohome)
- Aggregate report: `.work/<ISSUE_NUMBER>/nabledge-test/report-<YYYYMMDDHHMM>.md`
  - All numerical sections populated from source data
  - `<!-- AGENT: ... -->` placeholders for the 💡 and 🔬 analysis sections

### Step 8: Fill analysis sections in aggregate report

**This step runs for `--all` mode and `--baseline` mode.**

The aggregate report was generated by the script in Step 7.
Open the report file and replace `<!-- AGENT: ... -->` placeholders with actual analysis:

1. **💡 主要な発見**: Read all grading.json and metrics.json from the workspace. Identify patterns, anomalies, and bottlenecks. Write 2–3 subsections.
2. **🔬 仮説と改善提案**: Based on findings above, propose hypotheses with evidence, verification method, and expected outcome.

### Step 9: Baseline mode — save baseline

**This step runs ONLY when `--baseline` flag is provided.**

#### 9a: Create baseline directory

```bash
BASELINE_DIR=".claude/skills/nabledge-test/baseline"
# Use RUN_TIMESTAMP (captured in Step 4) for the baseline directory name
# This ensures the baseline timestamp matches the workspace timestamp
TARGET_DIR="${BASELINE_DIR}/v${VERSION}/${RUN_TIMESTAMP}"
mkdir -p "${TARGET_DIR}"
```

#### 9b: Save meta.json

```json
{
  "timestamp": "2026-03-06T14:30:00Z",
  "run_id": "20260306-143000",
  "version": 6,
  "branch": "<branch_name>",
  "commit": "<full_git_commit_sha>",
  "commit_short": "<7-char_sha>",
  "scenarios_count": 10,
  "trials": 1,
  "scenarios": {
    "qa": ["qa-001", "qa-002", "qa-003", "qa-004", "qa-005"],
    "code-analysis": ["ca-001", "ca-002", "ca-003", "ca-004", "ca-005"]
  }
}
```

#### 9c: Copy per-scenario data

For each scenario, copy from workspace to baseline:

```bash
for scenario_id in $(ls "${WORKSPACE}/"); do
  mkdir -p "${TARGET_DIR}/${scenario_id}"

  # Copy metrics
  cp "${WORKSPACE}/${scenario_id}/metrics.json" \
     "${TARGET_DIR}/${scenario_id}/metrics.json"

  # Copy response
  cp "${WORKSPACE}/${scenario_id}/response.md" \
     "${TARGET_DIR}/${scenario_id}/response.md"

  # Copy grading
  cp "${WORKSPACE}/${scenario_id}/grading.json" \
     "${TARGET_DIR}/${scenario_id}/grading.json"

  # Copy output files to scenario directory (ca-* only)
  if [ -d "${WORKSPACE}/${scenario_id}/output" ]; then
    cp "${WORKSPACE}/${scenario_id}/output"/* \
       "${TARGET_DIR}/${scenario_id}/"
  fi

  # Copy benchmark data (benchmark scenarios only)
  if [ -f "${WORKSPACE}/${scenario_id}/benchmark.json" ]; then
    cp "${WORKSPACE}/${scenario_id}/benchmark.json" \
       "${TARGET_DIR}/${scenario_id}/benchmark.json"
    if [ -d "${WORKSPACE}/${scenario_id}/trials" ]; then
      cp -r "${WORKSPACE}/${scenario_id}/trials" \
            "${TARGET_DIR}/${scenario_id}/trials"
    fi
  fi

  # Copy per-trial output files (ca-* benchmark scenarios only)
  if [ -d "${WORKSPACE}/${scenario_id}/trials" ]; then
    for trial_dir in "${WORKSPACE}/${scenario_id}/trials"/*/; do
      trial_num=$(basename "${trial_dir}")
      if [ -d "${trial_dir}output" ]; then
        mkdir -p "${TARGET_DIR}/${scenario_id}/trials/${trial_num}/output"
        cp "${trial_dir}output"/* \
           "${TARGET_DIR}/${scenario_id}/trials/${trial_num}/output/"
      fi
    done
  fi
done
```

#### 9d: Update latest symlink

```bash
mkdir -p "${BASELINE_DIR}/v${VERSION}"
cd "${BASELINE_DIR}/v${VERSION}"
rm -f latest
ln -s "${RUN_TIMESTAMP}" latest
```

#### 9e: Generate comparison report

**Determine previous baseline**:

```bash
# Count baseline directories for this version (excluding 'latest' symlink)
BASELINE_COUNT=$(ls -d ${BASELINE_DIR}/v${VERSION}/2* 2>/dev/null | wc -l)

if [ "${BASELINE_COUNT}" -le 1 ]; then
  PREV=""
else
  # Get second-to-last (= previous) baseline directory for this version
  PREV=$(ls -d ${BASELINE_DIR}/v${VERSION}/2* | sort | tail -2 | head -1)
fi
```

**Run the comparison report script**:

```bash
python .claude/skills/nabledge-test/scripts/generate_comparison_report.py \
  --current "${TARGET_DIR}" \
  ${PREV:+--previous "${PREV}"} \
  --output "${TARGET_DIR}/comparison-report.md"
```

If `PREV` is empty (initial baseline), omit `--previous`. The script generates an initial baseline report with no comparison data.

**Fill analysis sections** (only when previous baseline exists):

After the script completes, open `${TARGET_DIR}/comparison-report.md` and replace `<!-- AGENT: ... -->` placeholders:

1. **前回からの変更点**: Read `${PREV}/meta.json` and `${TARGET_DIR}/meta.json` to get full `commit` SHAs. Run `git log --oneline <prev_commit>..<curr_commit>`. For each user-facing commit (skip tests/CI/infra/dev tools), write a bullet: `- <change description> (nablarch/nabledge-dev#xx)`. Extract issue/PR numbers from commit messages (e.g. `(#123)` patterns). Use `(issue不明)` if none found.
2. **総合評価**: Evaluate improvement effects from a third-party perspective. State what improved and what did not, citing specific numbers.
3. **実測データからの分析**: Analyze overall trends, type-specific patterns (QA vs CA), anomalous scenarios, and variability.
4. **分析を受けた仮説**: Propose hypotheses based on the data analysis, with data evidence, relevant implementation reference, and predictions.

### Step 10: Display summary

**For single/all mode**:

```
✓ qa-001: 5/5 expectations detected | 48s | 7,019 tokens
✓ qa-002: 5/5 expectations detected | 14s | 15,200 tokens
✗ ca-004: 8/12 expectations detected | 64s | 8,820 tokens

Aggregate report: .work/<ISSUE_NUMBER>/nabledge-test/report-<YYYYMMDDHHMM>.md
Workspace: .tmp/nabledge-test/run-<YYYYMMDD-HHMMSS>/
```

**For baseline mode** (append to above):

```
Baseline saved: .claude/skills/nabledge-test/baseline/v<VERSION>/<TIMESTAMP>/
Latest symlink: .claude/skills/nabledge-test/baseline/v<VERSION>/latest → <TIMESTAMP>/
Comparison report: .claude/skills/nabledge-test/baseline/v<VERSION>/<TIMESTAMP>/comparison-report.md
```

## Dependencies

- **Task tool**: Required for sub-agent execution (Claude Code Task tool)
- **nabledge-6 / nabledge-5**: Target skill to be tested
- **git**: For branch name and commit SHA resolution

Does NOT depend on skill-creator. nabledge-test v2 is self-contained.
