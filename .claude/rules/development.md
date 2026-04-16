# Development Process

General rules for all source code changes in this repository.

## TDD

All source code changes must follow TDD:

1. Write a failing test that captures the expected behavior (RED)
2. Implement the minimum code to make it pass (GREEN)
3. Confirm all existing tests still pass

Never implement first and write tests after.

## Design Before Implementation

Before implementing, always design first. Before designing, investigate.

**Investigation rules:**
- Cover all cases exhaustively — do not rely on sampling alone
- Write scripts to verify findings empirically, not by reading code alone
- Always check the official reference/documentation to confirm how a construct behaves — never assume
- Base all decisions on facts, not inference; eliminate ambiguity before proceeding

**Design rules:**
- Design before writing any code
- Have the design reviewed by a Software Engineer expert before implementation
- The goal is to prevent rework: ambiguous or assumption-based designs cause costly mistakes

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

## Fix Problems Immediately

When a problem is found — test failure, bug, incorrect behavior, rule violation — fix it immediately. Do not defer it as "out of scope" or "tracked separately."

- No problem is too small to fix now
- Deferring problems creates debt that compounds; immediate fixes keep the codebase clean
- This applies to pre-existing failures discovered during work, not just new ones

## Tests Must Pass Before PR

All automated tests must pass before creating a PR. Fix all failures — including pre-existing ones — before requesting review.
