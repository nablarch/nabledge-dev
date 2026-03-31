# Notes

## 2026-03-31

### Root cause analysis: v1.2 vs v1.3 CA gap

v1.2 and v1.3 share identical `code-analysis.md` (path substitution only), yet v1.3 scores 34/36 on ca-001 vs v1.2's 28/36.
This confirms root cause is NOT purely prompt-side — input context differences also determine output.

15 miss items classified:
- Context-dependent (Overview): 5 items → defer investigation (v1.3 succeeds with same prompt, root cause unclear)
- Prompt-fixable (Processing Flow helper methods): ~2 items
- Skeleton format (Sequence diagram `POST RW` → `doRW`): 2 items
- Structural (template `.nabledge/` path): 2 items
- Other (call depth 2, parent class method, knowledge search miss): ~4 items (not all fixable)

### Decision: Defer Overview class list fix

v1.3 correctly includes MailRequester/MessageSender etc. with the same prompt.
The difference must be input context (source file content differences, knowledge search hits).
Fixing requires understanding what context v1.3 has that v1.2 doesn't — document here as investigation is done.
