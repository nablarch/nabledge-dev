# Goal

Add BM25 full-text search as a pre-filter stage before the semantic search in the QA workflow,
so that queries containing Nablarch-specific terms (class names, annotations, method names) can
complete without invoking the LLM-backed semantic search, reducing per-query cost.
Remove the `keyword-search` workflow from all skill versions (v6, v5, v1.4, v1.3, v1.2)
because it overlaps in naming and purpose with the new BM25 stage.

The design source is `docs/reports/cost-optimization-nabledge.md` §4.
The mechanism is: run BM25 (existing `keyword-search.sh`) first; generate an answer from its
results; run the Step-6 hallucination verifier; if PASS complete without semantic search;
if FAIL fall back to semantic search and proceed as today.
The BM25 query terms are extracted by the LLM from the user's question.

---

# Acceptance criteria

- `workflows/qa.md` in v6 has a BM25 pre-search step before Step 3 (semantic search):
  - LLM extracts Nablarch-specific terms from the question
  - `keyword-search.sh` is invoked with those terms
  - If hits exist, an answer is generated and verified with Step 6 logic
  - PASS → return answer without running semantic search
  - FAIL or no hits → fall through to semantic search (existing Step 3–8)
- v6 benchmark: all 34 scenarios pass (zero regression vs current baseline)
- v6 benchmark: cost per query is lower than the previous run baseline
- The same `qa.md` change is applied identically to v5, v1.4, v1.3, v1.2
- `workflows/keyword-search.md` is removed from all five versions
- `scripts/keyword-search.sh` is retained (it is the BM25 engine used by the new step)
- `SKILL.md` routing for `keyword-search` command is removed from all five versions
- `docs/search-design.md` is updated to reflect the new QA flow and removal of keyword-search workflow
- CHANGELOG `[Unreleased]` updated in v6 (and v5 if applicable) per `.claude/rules/changelog.md`

---

# Assumptions

- `keyword-search.sh` already implements BM25-style keyword scanning and is the right engine
  (confirmed: it does case-insensitive substring AND/OR matching over all knowledge JSON)
- The Step-6 verifier in `qa.md` is reusable as-is for BM25 results — no structural change needed
- v5, v1.4, v1.3, v1.2 skills have identical `qa.md` structure (step numbers, step-6 verifier)
  and need only the same BM25 block inserted at the same position
- Benchmark tooling (`tools/tests/` or equivalent) can measure v6 cost and accuracy
- `keyword-search` command routing in SKILL.md must be removed; the `keyword-search.sh` script stays
- No change to `semantic-search.md` or `read-sections.sh`

---

# Rules

- commit and push every change; one completion marker per task
- Apply qa.md changes to all five versions in one commit (not split by version) per `.claude/rules/nabledge-skill.md`
- Never edit RBKC-generated files (knowledge JSON, index.md, classes.md)
- Run benchmark before and after v6 qa.md change; record both numbers
- verify is the quality gate — if benchmark shows regression, fix qa.md, never weaken verify

---

# Tasks

### #1: Establish v6 benchmark baseline

**Purpose**: Record current v6 benchmark pass count and cost so post-change results have a
comparison point.

**Prerequisites**: none

**Steps**:

- [ ] Locate the benchmark runner command for v6 (check `tools/tests/` or project docs)
- [ ] Run the benchmark and capture: scenario pass count, total cost, execution time
- [ ] Save results to `.rn/issue-382/baseline.md`
- [ ] Commit and push `.rn/issue-382/baseline.md`
- [ ] Self-check: baseline.md contains pass count, cost, and execution time for all 34 scenarios

**Completion criteria**:

- `.rn/issue-382/baseline.md` exists and contains v6 benchmark pass count, cost per query (or total), and execution time
- The recorded pass count is the pre-change reference used in task #3 comparison

---

### #2: Design the BM25 pre-search step for qa.md

**Purpose**: Define the exact wording and placement of the new BM25 step in `qa.md` before
writing any code, following the design-before-implementation rule.

**Prerequisites**: none (can run parallel to #1)

**Steps**:

- [ ] Draft the BM25 step as a standalone markdown block: term extraction logic, script invocation, answer generation, verifier reuse, PASS/FAIL branching
- [ ] Consult Software Engineer expert (subagent) to review the draft for correctness and edge cases
- [ ] Revise based on findings
- [ ] Save final draft to `.rn/issue-382/bm25-step-draft.md`
- [ ] User review — present draft and ask for approval before implementation
- [ ] Self-check: draft covers all branches (no hits, PASS, FAIL), reuses Step-6 verifier, does not duplicate existing steps

**Completion criteria**:

- `.rn/issue-382/bm25-step-draft.md` exists with the full step text
- User has approved the draft
- All branches (no BM25 hits, PASS, FAIL→fallback) are explicitly specified

---

### #3: Implement BM25 step in v6 qa.md and verify benchmark

**Purpose**: Insert the approved BM25 step into v6 `qa.md` and confirm no benchmark regression
and cost reduction.

**Prerequisites**: #1 (baseline), #2 (approved draft)

**Steps**:

- [ ] Insert the approved BM25 step into `.claude/skills/nabledge-6/workflows/qa.md` before the current Step 3
- [ ] Renumber subsequent steps if needed
- [ ] Run v6 benchmark; record pass count, cost, execution time
- [ ] Compare against baseline: all 34 scenarios pass, cost is lower
- [ ] Save comparison to `.rn/issue-382/benchmark-result.md`
- [ ] Software Engineer expert review (subagent)
- [ ] User review
- [ ] Commit and push `qa.md` change + benchmark result

**Completion criteria**:

- `.claude/skills/nabledge-6/workflows/qa.md` contains the BM25 pre-search step
- v6 benchmark: 34/34 scenarios pass
- v6 benchmark: cost per query lower than baseline
- `.rn/issue-382/benchmark-result.md` documents both numbers

---

### #4: Roll out qa.md change to v5, v1.4, v1.3, v1.2

**Purpose**: Apply the same BM25 step to the remaining four skill versions.

**Prerequisites**: #3 (v6 change verified and approved)

**Steps**:

- [ ] Confirm each version's `qa.md` step structure matches v6 (same step numbers, same Step-6 verifier)
- [ ] Apply identical BM25 block to v5, v1.4, v1.3, v1.2 `qa.md` files
- [ ] Note any version-specific differences (e.g. processing type list) and adjust accordingly
- [ ] Software Engineer expert review (subagent)
- [ ] User review
- [ ] Commit and push all four files in one commit

**Completion criteria**:

- `.claude/skills/nabledge-{5,1.4,1.3,1.2}/workflows/qa.md` each contain the BM25 pre-search step
- The BM25 block is structurally identical to v6 (path/version substitutions only)

---

### #5: Remove keyword-search workflow and routing from all versions

**Purpose**: Delete `workflows/keyword-search.md` and its SKILL.md routing entry from all five
versions, as the workflow is superseded and confusingly named.

**Prerequisites**: #3 (v6 qa.md verified — confirms keyword-search.sh is retained, only the workflow is removed)

**Steps**:

- [ ] Delete `workflows/keyword-search.md` from v6, v5, v1.4, v1.3, v1.2
- [ ] Remove the `keyword-search "<terms>"` routing line from each version's `SKILL.md`
- [ ] Confirm `scripts/keyword-search.sh` is NOT deleted (it is used by the new BM25 step)
- [ ] Software Engineer expert review (subagent)
- [ ] User review
- [ ] Commit and push all deletions and SKILL.md edits in one commit

**Completion criteria**:

- `workflows/keyword-search.md` does not exist in any of the five skill directories
- Each version's `SKILL.md` has no routing for `keyword-search` command
- `scripts/keyword-search.sh` still exists in v6 (and other versions if present)

---

### #6: Update docs/search-design.md and CHANGELOG

**Purpose**: Keep documentation in sync with the implementation changes.

**Prerequisites**: #3, #5

**Steps**:

- [ ] Update `docs/search-design.md`: remove keyword-search workflow entry from the workflow table and workflow section; add description of the BM25 pre-search step in the QA workflow section
- [ ] Add entry to `[Unreleased]` in `.claude/skills/nabledge-6/plugin/CHANGELOG.md` per `.claude/rules/changelog.md`
- [ ] Add entry to `[Unreleased]` in `.claude/skills/nabledge-5/plugin/CHANGELOG.md` if applicable
- [ ] Technical Writer expert review (subagent)
- [ ] User review
- [ ] Commit and push

**Completion criteria**:

- `docs/search-design.md` no longer references `keyword-search` workflow; QA workflow section describes BM25 pre-search
- `CHANGELOG [Unreleased]` has a user-facing entry for the BM25 addition and keyword-search removal

---

# Decisions

(none yet)

---

# State

- **Status**: not suspended
- **Date**: 2026-06-25
- **Last completed**: (none)
- **Next**: #1 Establish v6 benchmark baseline
- **Notes**: baseline (#1) and design (#2) can run in parallel
