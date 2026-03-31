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

### Investigation: Overview class list gap (v1.2 vs v1.3)

**Symptom**: ca-001 Overview misses `MailRequester`, `MessageSender`, `ValidatableFileDataReader`, `BusinessDateUtil`, `UserInfoTempEntity` in v1.2, but v1.3 correctly includes some of them.

**Key findings**:
- v1.2 and v1.3 use identical `code-analysis.md` (only path substitution differs)
- v1.3 ca-001 scores 34/36 vs v1.2's 28/36 — both miss `checkLoginId` and some Sequence diagram items
- For Overview specifically: v1.3 includes MailRequester/MessageSender (the service classes) while v1.2 does not

**Hypothesis (unverified)**: Input context differs between versions:
1. Knowledge search hits differ — v1.3 knowledge files may reference MailRequester/MessageSender in a more prominent way, causing the agent to surface them in Overview
2. Source file content: v1.2 and v1.3 source files for W11AC02Action may differ in comments/structure, affecting LLM comprehension

**Why not fixed now**: Reproducing this deterministically requires:
- Running both v1.2 and v1.3 CA on same file with same seed
- Diffing knowledge search results for both runs
- Identifying which knowledge file causes the gap

This investigation is deferred to a follow-up issue. The current PR focuses on the structural/prompt-fixable issues (output_path, doRW format, helper methods).
