# Design and Implementation Decisions

When making a design or implementation judgment call, consult the appropriate expert
and present the findings to the user before proceeding. Do not decide unilaterally.

## Expert by Artifact Type

| Artifact | Expert |
|----------|--------|
| Source code (*.py, *.js, *.java, etc.) | Software Engineer |
| Prompts / workflows (.claude/*, workflows/*.md) | Prompt Engineer |
| Test code / test cases (*test*.*, *spec*.*) | QA Engineer |

## Process

1. **Identify the decision** — describe the options and their trade-offs
2. **Consult the expert** — launch a subagent in a separate context with the expert persona
3. **Present to the user** — summarize the expert's recommendation and ask for a decision
4. **Proceed only after approval** — implement the chosen option

## Subagent Prompt Template

```
You are a {Expert Role}. A design decision needs your input.

## Context
{Brief description of the feature or component}

## Options
{Option A}: {description and trade-offs}
{Option B}: {description and trade-offs}

## Your Task
Evaluate each option from a {Expert Role} perspective and recommend one.
Provide specific reasoning. Keep your response concise (under 300 words).
```

## Notes

- Expert consultation is required for non-trivial decisions where multiple approaches exist
- Skip consultation for mechanical changes with no real alternatives (e.g., fixing a typo, renaming a variable to match a spec)
- When the decision affects multiple artifact types, consult the most relevant expert (source code decisions take priority over test/doc decisions)
