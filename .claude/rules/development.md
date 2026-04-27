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

## Observe Real Output Before Claiming Success

Prompt changes and LLM-driven logic cannot be validated by reading the
prompt. The design may look right on paper and still produce broken
output — wrong field types, over-extracted lists, truncated streams,
off-spec JSON, over-granular fact extraction. Always observe real
output before declaring a change "working".

**When this rule fires:**
- Any change to an AI prompt (skill workflow, benchmark prompt, judge prompt, etc.)
- Any change to code that parses LLM structured output
- Any change to scoring / grading / verification logic that consumes LLM output

**Required procedure:**
1. After the change, run ONE real case end-to-end.
2. Dump the full structured output — every field, every list — and
   read it. Do not stop at the summary statistic or the level number.
3. Check for shape anomalies: array lengths outside expected range,
   fields that should be objects arriving as strings, truncation,
   missing required fields, over-extraction (e.g., a "required facts"
   list that has 15 items when 6–8 is the reasonable range).
4. Only after the single case is clean, run on a small batch (3-5 cases)
   and read their full outputs too. Do not scale to 30+ cases until
   3-5 pass inspection.

**Why:** In the 2026-04-23 benchmark judge rewrite, the mean level
looked plausible but per-case inspection revealed a 1314-element
`a_facts` array (truncated JSON parsed into a char-by-char list) and
over-granular fact extraction (15 "required" facts where the real
required set was 6–8). Both slipped past the summary statistic.
Per-case output inspection would have caught them immediately.

## Expert Review for Prompt Changes

Any change to an AI prompt — whether as part of a skill, benchmark, workflow, or one-off script — must pass **Prompt Engineer** expert review before the change is adopted.

**Scope (applies to):**
- `.claude/skills/*/workflows/*.md`
- `.claude/skills/*/assets/*.md` (user-facing prompts)
- `tools/benchmark/prompts/*.md`
- Any new prompt template or schema used with `claude -p` / Agent tool

**When this rule fires:**
- If the trigger for the change is itself an expert review (e.g., Round 1 prompt change was already recommended by a Prompt Engineer review), no additional review is required for that change.
- If the trigger is anything else — new hypothesis, user request, own judgment, refactor — Prompt Engineer review is **required** before the prompt goes live.
- Save the review to `.work/xxxxx/review-by-prompt-engineer-{round or topic}.md` and link from tasks.md / round log.

**Attach real execution output to the review.** Reviewing the prompt
text alone will miss behavior that only shows up in output — field
shape, list granularity, truncation patterns. When the prompt has been
run even once, include a representative full output (one case, every
field) in the review input. If the prompt is new and has not been
executed yet, run it once first, then send the review.

**Purpose:** Prompt quality is load-bearing for downstream accuracy. A change that looks obvious may degrade behavior in ways the author cannot see without an independent read.

## Fix Problems Immediately

When a problem is found — test failure, bug, incorrect behavior, rule violation — fix it immediately. Do not defer it as "out of scope" or "tracked separately."

- No problem is too small to fix now
- Deferring problems creates debt that compounds; immediate fixes keep the codebase clean
- This applies to pre-existing failures discovered during work, not just new ones

## Test Writing: Required Coverage

Every test class must include:

- **Bug-revealing cases**: Input that exercises each specific failure mode (wrong output, missed detection, false alarm). If a bug can occur, write a test that catches it.
- **Edge cases**: Boundary values, empty inputs, single-element collections, whitespace/encoding edge cases, overlapping patterns, and any input the spec explicitly lists as allowed or disallowed.

A test suite that only covers the happy path is incomplete. The question to ask when writing tests: *"What input would make this function produce wrong output?"* — write that as a test.

## Tests Must Pass Before PR

All automated tests must pass before creating a PR. Fix all failures — including pre-existing ones — before requesting review.

## No Test Skipping

Do not use `pytest.mark.skip`, `pytest.mark.skipif`, or `pytest.importorskip` to bypass tests.

- If a test requires an external resource that may be absent, either make it a proper conditional skip with a comment explaining the exact condition, or restructure the test to not depend on the resource
- `pytest.importorskip` on internal modules is not allowed — if the module path changes, fix the import, do not skip
- Tests that are skipped silently hide regressions; every skip must be treated as a failure to investigate
