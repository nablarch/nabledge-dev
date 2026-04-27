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

## Root-cause horizontal check (mandatory)

Do NOT fix only the specific items a reviewer flagged. Before applying any
fix, perform a horizontal check to find every other instance of the same
root cause in the codebase.

### Why

Reviewers flag symptoms they happened to notice. The same class of bug
usually exists elsewhere. Fixing only the flagged items means the next
review round surfaces more instances of the same root cause ("the
problem keeps coming back in a different form"), wasting review cycles
and signalling that the author is not thinking systemically.

### Process

For each reviewer finding, before writing a fix:

1. **Identify the root cause class** — what general pattern does this
   finding represent? (e.g. "silent skip without spec backing", "regex
   boundary misses self-closing form", "test pins implementation output
   rather than spec requirement")

2. **Horizontal search** — grep/scan the whole codebase for other
   instances of the same class. Examples:
   - Silent skip candidates: every `continue` / `if X: return []` /
     early-return in the affected module
   - Regex coverage gaps: every module-level regex cross-checked against
     the spec it should enforce
   - AST node coverage: every `findall` / visitor dispatch against the
     spec's node → behaviour table
   - Circular tests: every test whose assertion mirrors the
     implementation rather than an independent spec-derived oracle

3. **Enumerate all matches** — list every file:line that fits the
   pattern, not just the one the reviewer cited.

4. **Fix the whole class in one pass** — the flagged instance + every
   horizontal match. Do not defer horizontal matches to "next time".

5. **Document the class in the commit message** — name the root cause,
   list the horizontal matches you found, and confirm they are all fixed.

### When horizontal check finds nothing

If the reviewer's finding is genuinely one-off (no other instance of
the same class exists), state that explicitly in the commit message:
"Horizontal check: searched for X pattern, no other instances found."
This proves the check was done rather than skipped.

### Anti-patterns (avoid)

- Fixing only the exact file:line the reviewer named and stopping there.
- Saying "I'll handle other instances when they come up" — they will
  come up in the next review round, which is exactly the waste this
  rule prevents.
- Treating the reviewer as an exhaustive oracle — reviewers sample, they
  do not enumerate. Horizontal check is the author's job.
