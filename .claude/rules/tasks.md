# Task Creation

Rules for writing tasks in `.work/xxxxx/tasks.md`.

## Granularity

One task = one commit. Each step must be a concrete instruction that can be executed without ambiguity.

- Avoid vague verbs ("re-apply", "clean up", "confirm" → use specific commands and file names)
- Git operations: specify commit hash or exact command (e.g. `git cherry-pick 46893d39f`, `git checkout main -- path/to/file`)
- Test verification: specify the exact command (e.g. `pytest tools/tests/ -x`)
- "All tests" or "all items" is forbidden — enumerate targets or give a specific command

## Impact analysis

Before defining tasks, investigate the impact scope and list affected files in the task.

- Use grep to confirm actual references (do not guess impact scope)
- Cover all versions (v6/v5/v1.4/v1.3/v1.2)
- Document "no impact" cases too, with evidence (e.g. `simulate_*.py` does not reference read-sections.sh — section loading reads JSON directly)

## Order

1. **Update the design doc** — finalize the target state before implementing
2. **Write the test** (RED) — per TDD, add a test before any code change that lacks one
3. **Implement** (GREEN) — implement to match the design doc and test
4. **Verify tests pass** — before each commit

If you find a change target with no test, insert a test-addition task before the implementation task.

## Incremental execution

Never run all at once. Do one, verify, then batch the rest.

- File move: move 1 → update references → verify tests → batch the rest
- Revert: revert 1 → verify tests → batch the rest
- New implementation: verify 1 scenario → run all

## Dependencies

Make dependencies between tasks explicit and enforce order strictly.

- If a task depends on another, state it: "Do after B-1 is complete"
- Irreversible operations (e.g. baseline capture → code change) must be called out explicitly (e.g. "baseline cannot be taken after this change")
- Do not mix scopes (e.g. do not touch Phase B code during Phase A)

## Verification steps

Every verification step must state: the **intent** (what guarantee is being made) and an **acceptance criterion** (a condition that can be evaluated mechanically — exit code, file content, command output).

**Intent**: one sentence — "X is not broken", "Y is working correctly".
**Acceptance criterion**: exit code, file existence/content, or command output. Not subjective observation.

Bad examples:
- `answer.md` is not empty — does not guarantee the intent (normal response present); an error message also passes
- Completes without BASH errors — "BASH error" depends on the reader's judgment

Good examples:
- `answer.md` contains a `参照:` section — proves the workflow cited a knowledge file
- `python3 -m ... --scenario-ids pre-01` exits 0 and `metrics.json` has `model_usage` non-empty

## Intermediate state safety

Every commit must leave all tests passing.

- File move: copy → update references → verify tests → delete old file (never delete first)
- Do not revert and move simultaneously — always keep referenced paths resolvable
