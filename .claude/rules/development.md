# Development Process

General rules for all source code changes in this repository.

## TDD

All source code changes must follow TDD:

1. Write a failing test that captures the expected behavior (RED)
2. Implement the minimum code to make it pass (GREEN)
3. Confirm all existing tests still pass

Never implement first and write tests after.

## Design and Implementation Decisions

When multiple approaches exist, consult the appropriate expert before proceeding.
See `.claude/rules/design-decisions.md` for the expert consultation process.

## Expert Review After Each Source Change

After completing a source code change (implement → GREEN), run expert review before moving to the next task. Do not batch reviews to the end — catching issues early avoids rework.

**Required experts for source code changes:**
- **Software Engineer** — architecture, code quality, correctness
- **QA Engineer** — test coverage, edge cases, assertion quality

Launch both as subagents in separate contexts (see `.claude/rules/design-decisions.md` for the prompt template). Report findings to the user before proceeding to the next task.

If either review returns **Needs Fix**, address the issues before continuing.

## Tests Must Pass Before PR

All automated tests must pass before creating a PR. Fix all failures — including pre-existing ones — before requesting review.
