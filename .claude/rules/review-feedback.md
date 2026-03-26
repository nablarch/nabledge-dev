# Review Feedback

Applies to all forms of review, check, and evaluation (self-check, expert review, QA, etc.).

## Output Format

Always output feedback and improvement proposals together:

```markdown
**[Priority] Issue**
- Description: {what is wrong}
- Proposed fix: {how to address it}
```

Never report a finding without a proposed fix.

## Response to Findings

**Default: fix immediately**

Address found issues right away without waiting for user approval.

**Consult user first when:**

- User-facing impact is large (behavior change, output format change, user-visible text change)
- Backward compatibility breaks (API changes, file format changes, breaking existing workflows)
- Scope is ambiguous (the fix requires decisions beyond the current task)

When consulting, present:
1. What the issue is
2. Proposed fix
3. Why user input is needed (impact or trade-off)
