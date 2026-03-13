You are creating improvement Issue proposals for the Nabledge knowledge file pipeline.

## Input: File-level Evaluations

```json
{FILE_EVALUATIONS}
```

## Input: Findings Summary

```json
{FINDINGS_SUMMARY}
```

## Task

Group files needing improvement by PURPOSE. For each group create an Issue proposal with title, purpose, target_files, user_impact, body (all in English).

Do NOT propose improvements for `needs_improvement: false` files.

## Output

Respond with JSON matching the provided schema.
