# Nabledge Test Skill

Testing framework for nabledge skills (versions 6, 5).

## Execution Flow

### 1. Parse Arguments

Extract workflow and parameters from invocation:

```
/nabledge-test                                     → No args → AskUserQuestion for workflow
/nabledge-test run-scenarios 6                     → workflow="run-scenarios", version="6", scenario_id=null (all)
/nabledge-test run-scenarios 6 6-handlers-001      → workflow="run-scenarios", version="6", scenario_id="6-handlers-001" (single)
/nabledge-test evaluate-results <session-dir>      → workflow="evaluate-results", session_dir=<session-dir>
```

**If no args**: Use AskUserQuestion to select workflow:
- Question: "Which testing workflow do you want to execute?"
- Options:
  1. "Run Scenarios (run-scenarios)" - Execute test scenarios for nabledge skill
  2. "Evaluate Results (evaluate-results)" - Evaluate test results and generate review

### 2. Execute Workflow

Delegate to specialized workflow via Task tool:

#### A. run-scenarios Workflow

```
Task
  subagent_type: "general-purpose"
  description: "Execute test scenarios workflow"
  prompt: "Follow the workflow to execute test scenarios for nabledge skill.

{Read and include workflows/run-scenarios.md}

## Input Context
- Version: {version}
- Scenario ID: {scenario_id} (if null, execute all scenarios)
"
```

#### B. evaluate-results Workflow

```
Task
  subagent_type: "general-purpose"
  description: "Execute results evaluation workflow"
  prompt: "Follow the workflow to evaluate test results.

{Read and include workflows/evaluate-results.md}

## Input Context
- Test session directory: {test_session_dir}
"
```

## Implementation Notes

1. **No args**: Use AskUserQuestion for user-friendly workflow selection
2. **Version required**: For run-scenarios, version must be specified or selected
3. **Session dir required**: For evaluate-results, session directory must be specified or selected
4. **Task tool usage**: Workflows execute in separate context with full workflow content
5. **Error handling**: Display clear error messages when parameters missing

## Error Handling

| Error | Response |
|-------|----------|
| Invalid workflow | Use AskUserQuestion for workflow selection |
| Missing version (run-scenarios) | List available versions, ask user to select |
| Scenario ID not found | Display error with available scenario IDs for the specified version |
| Missing session dir (evaluate-results) | List available sessions, ask user to select |
| Scenarios not found | Display error with available versions |
| Session not found | Display error with available sessions |

## Workflows

- **run-scenarios**: Execute test scenarios for specified nabledge skill version
- **evaluate-results**: Evaluate test results and generate review report

For detailed workflow documentation, see `workflows/` directory.
