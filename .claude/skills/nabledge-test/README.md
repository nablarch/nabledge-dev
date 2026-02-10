# Nabledge Test Skill

Testing framework for nabledge skills (nabledge-6, nabledge-5, nabledge-1.4).

## Overview

This skill provides automated testing capabilities for nabledge skills:
- Execute test scenarios
- Evaluate results against criteria
- Generate improvement recommendations

## Usage

### Run Test Scenarios

Execute test scenarios for a specific nabledge skill version:

```
/nabledge-test run-scenarios <version>
```

Examples:
```
/nabledge-test run-scenarios nabledge-6
/nabledge-test run-scenarios nabledge-5
```

This will:
1. Load scenarios from `scenarios/<version>/`
2. Execute each scenario using the target skill
3. Record results in `results/YYYYMMDD-HHMM/`
4. Create work log summary in `work/YYYYMMDD/`

### Evaluate Results

Evaluate test results and generate review report:

```
/nabledge-test evaluate-results <test-session-dir>
```

Example:
```
/nabledge-test evaluate-results results/20260210-1430
```

This will:
1. Analyze all scenario results
2. Evaluate against criteria
3. Identify common issues
4. Generate improvement recommendations
5. Create review report

## Directory Structure

```
.claude/skills/nabledge-test/
├── skill.json                          # Skill definition
├── README.md                           # This file
├── workflows/
│   ├── run-scenarios.md                # Scenario execution workflow
│   └── evaluate-results.md             # Results evaluation workflow
├── templates/
│   ├── scenario-result.md              # Scenario result template
│   └── review.md                       # Review report template
├── scenarios/
│   ├── nabledge-6/
│   │   ├── code-analysis-scenarios.json
│   │   └── keyword-search-scenarios.json
│   ├── nabledge-5/                     # Future
│   └── nabledge-1.4/                   # Future
└── results/
    └── YYYYMMDD-HHMM/                  # Test session results
        ├── code-analysis/
        ├── keyword-search/
        └── *-scenarios-review.md
```

## Workflows

### 1. run-scenarios

Executes test scenarios for specified nabledge skill version.

**Input**: Nabledge version (e.g., "nabledge-6")

**Output**:
- Scenario results in `results/YYYYMMDD-HHMM/`
- Work log summary in `work/YYYYMMDD/`

### 2. evaluate-results

Evaluates test results and generates review report.

**Input**: Test session directory (e.g., "results/20260210-1430")

**Output**:
- Review reports in test session directory
- Improvement recommendations

## Templates

### scenario-result.md

Template for recording individual scenario execution results:
- Metadata (ID, category, date, time)
- Test input (question, target, expectations)
- Execution results (workflow, resource usage, tool calls)
- Generated output
- Evaluation against criteria
- Issues found
- Status (PASS/FAIL/PARTIAL)

### review.md

Template for test session review report:
- Test session metadata
- Summary and pass rates
- Detailed results by scenario
- Common issues (by priority)
- Improvement recommendations
- Action items
- Next steps

## Test Scenarios

### nabledge-6

**code-analysis-scenarios.json** (5 scenarios):
- Full batch action structure analysis
- Initialization process analysis
- Database read process analysis
- File write process analysis
- Test code implementation analysis

**keyword-search-scenarios.json** (5 scenarios):
- Handlers: Data read handler
- Libraries: UniversalDao paging
- Tools: NTF test data preparation
- Processing: Batch basic structure
- Adapters: SLF4J adapter configuration

## Evaluation Criteria

Each scenario is evaluated against:
- Workflow execution correctness
- Output quality (structure, completeness)
- Knowledge integration (proper citation)
- Token efficiency (target range)
- Tool call efficiency (target range)

## Language

All test content is in English, following repository language rules.
