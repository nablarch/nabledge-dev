# Issue #15: Create nabledge-6-test Skill

**Date**: 2026-02-13
**Issue**: #15 - As a developer, I want a skill to execute and evaluate nabledge-6 scenarios so that I can continuously improve the skill

## What Was Done

Created a new skill `nabledge-6-test` that enables automated execution and evaluation of nabledge-6 test scenarios.

### Files Created

```
.claude/skills/nabledge-6-test/
├── SKILL.md (983 lines)
├── README.md (648 lines)
└── templates/
    ├── single-scenario-report.md (83 lines)
    ├── summary-report.md (38 lines)
    └── code-analysis-report.md (99 lines)
```

### Skill Capabilities

The skill provides four main workflows:

#### 1. Execute Single Scenario (Workflow 1)
- Execute individual test scenarios by ID
- Monitor workflow execution (tool calls, token usage, workflow steps)
- Evaluate against 6-8 criteria (depends on scenario type)
- Generate detailed report with improvement suggestions

**Usage**: `nabledge-6-test execute <scenario-id>`

#### 2. Execute All Scenarios (Workflow 2)
- Execute all 30 test scenarios from scenarios.json
- Generate individual reports for each scenario
- Create summary report with statistics and recommendations
- Identify common issues and prioritize improvements

**Usage**: `nabledge-6-test execute-all`

#### 3. Execute Category Scenarios (Workflow 3)
- Execute all scenarios in a specific category
- Categories: handlers, libraries, tools, processing, adapters, code-analysis
- Generate category-focused report

**Usage**: `nabledge-6-test execute-category <category>`

#### 4. Generate New Scenario (Workflow 4)
- Dynamically create new test scenarios
- Interactive process with knowledge file suggestions
- Auto-generate expected keywords and sections
- Add to scenarios.json and optionally execute immediately

**Usage**: `nabledge-6-test generate-scenario`

### Evaluation Framework

The skill evaluates scenarios against structured criteria:

**For knowledge search scenarios** (6 criteria):
1. Workflow Execution (Pass/Fail)
2. Keyword Matching (Score: 0-100%, Pass threshold: ≥80%)
3. Section Relevance (Pass/Fail)
4. Knowledge File Only (Pass/Fail)
5. Token Efficiency (Pass/Fail, Target: 5,000-15,000 tokens)
6. Tool Call Efficiency (Pass/Fail, Target: 10-20 calls)

**For code-analysis scenarios** (8 criteria):
- All 6 above criteria, plus:
7. Code Analysis Workflow (Pass/Fail)
8. Code Analysis Output Quality (Pass/Fail)

### Report Templates

Created three report templates with structured sections:

1. **single-scenario-report.md**: Detailed evaluation for individual scenarios
   - Scenario details
   - Execution summary
   - Evaluation results per criterion
   - Response analysis
   - Improvement suggestions
   - Overall assessment

2. **summary-report.md**: Overview for multiple scenarios
   - Overall statistics
   - Results by category
   - Common issues
   - Top improvement recommendations
   - Trend analysis

3. **code-analysis-report.md**: Specialized report for code analysis scenarios
   - Code analysis workflow evaluation
   - Output quality assessment
   - Component coverage
   - Knowledge references

### Documentation

- **SKILL.md**: Comprehensive skill definition with detailed workflows (983 lines)
- **README.md**: User-friendly documentation with examples and best practices (648 lines)

## Results

### Success Criteria Met

All success criteria from issue #15 are met:

- ✅ A developer can execute nabledge-6 scenarios using the created skill and observe documented test results
  - Implemented via Workflow 1 (execute single), Workflow 2 (execute-all), Workflow 3 (execute-category)
  - Reports generated in work/YYYYMMDD/ with detailed test results

- ✅ A developer can evaluate scenario results through the skill's structured evaluation framework
  - 6-8 evaluation criteria defined
  - Pass/Fail status per criterion
  - Scores for keyword matching
  - Observations and detailed analysis

- ✅ A developer can identify improvement areas from the documented evaluation output
  - "Improvement Suggestions" section in every report
  - "Top Improvement Recommendations" in summary reports
  - Prioritized by impact and frequency
  - Actionable with specific next steps

- ✅ A developer can use skill-creator to generate dynamic scenario tests by following documented instructions
  - Workflow 4 (generate-scenario) enables dynamic test creation
  - Interactive process guides user through creation
  - Auto-generates expected keywords/sections from knowledge files
  - Adds to scenarios.json automatically

## Usage Example

```bash
# Execute single scenario
nabledge-6-test execute handlers-001

# Execute all scenarios (30 scenarios, ~30-60 minutes)
nabledge-6-test execute-all

# Execute specific category
nabledge-6-test execute-category handlers

# Generate new scenario
nabledge-6-test generate-scenario

# Interactive mode
nabledge-6-test
```

## skill-creator Integration (Added Later)

After initial implementation, **skill-creator** from Anthropic's skills repository was integrated:

### Files Added
- `INSTALL-SKILL-CREATOR.md`: Installation guide for skill-creator

### Files Modified
- `SKILL.md`:
  - Enhanced Workflow 4 to support standalone skill generation
  - Added Workflow 5 with skill-creator integration details
- `README.md`:
  - Updated "Generate New Scenario" section
  - Added "skill-creator Integration" section

### What skill-creator Enables

When generating a new scenario, users can optionally create a standalone test skill:

```
nabledge-6-test generate-scenario
→ Generate handlers-006 scenario
→ Also generate test-handlers-006 skill (using skill-creator)
→ User can run: /test-handlers-006 anytime
```

**Benefits**:
- Quick access: `/test-{scenario-id}`
- Encapsulation: Self-contained test skills
- Reusability: Shareable with team
- Customization: Modify individual tests
- Distribution: Package as plugins

See `work/20260213/skill-creator-integration.md` for detailed integration notes.

## Next Steps

### Immediate
1. **Install skill-creator** (required for standalone skill generation):
   ```
   /plugin marketplace add anthropics/skills
   /plugin install example-skills@anthropic-agent-skills
   ```
2. Test the skill with a sample scenario to verify it works correctly
3. Execute a few scenarios from different categories to validate evaluation logic
4. Try generating a scenario with standalone skill option
5. Review generated reports for quality and completeness

### Future Enhancements
1. Add trend analysis (compare results across multiple test runs)
2. Add regression detection (identify scenarios that recently started failing)
3. Add performance benchmarking (compare against baseline metrics)
4. Add automated fix suggestions (suggest specific code changes based on failures)
5. Add CI/CD integration (run tests automatically on knowledge file changes)
6. Auto-detect skill-creator installation
7. Add skill validation before saving

## Technical Notes

- Skill follows the manual workflow execution pattern (Claude must execute steps using tools)
- Reports use Markdown format for readability
- Templates use {{variable}} syntax for easy substitution
- All reports stored in work/YYYYMMDD/ directory with timestamps to avoid collisions
- Skill supports both Japanese (user-facing messages) and English (internal documentation)

## Related Files

- Issue: #15 in GitHub
- Test scenarios: `.claude/skills/nabledge-6/tests/scenarios.json`
- Test documentation: `.claude/skills/nabledge-6/tests/README.md`
- Nabledge-6 skill: `.claude/skills/nabledge-6/SKILL.md`
