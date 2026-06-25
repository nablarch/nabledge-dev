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

### #1: Confirm existing benchmark baseline

**Purpose**: Identify which existing benchmark result to use as the pre-change reference,
so no re-run is needed and the comparison is anchored to a real prior measurement.

**Prerequisites**: none

**Steps**:

- [ ] Review `tools/benchmark/results/` — identify the most recent completed run with crossrun-summary or baseline.json
- [ ] Record the label, scenario pass count, p50 cost, and p50 execution time in `.rn/issue-382/baseline.md`
- [ ] Commit and push `.rn/issue-382/baseline.md`
- [ ] Self-check: baseline.md names the exact run label and contains pass count, p50 cost, p50 execution time

**Completion criteria**:

- `.rn/issue-382/baseline.md` exists and names the run label used as baseline
- It contains pass count (out of 34), p50 cost per query, and p50 execution time from that run

---

### #2: Select BM25 library and design the BM25 pre-search step for qa.md

**Purpose**: Select a BM25 library, get user approval on the choice and any setup impact,
then define the exact wording and placement of the new BM25 step in `qa.md` before writing
any code. The existing `keyword-search.sh` (substring matching, no scoring) is not BM25 and
will not be used as the BM25 engine.

**Prerequisites**: none (can run parallel to #1)

**Steps**:

- [ ] Survey candidate BM25 libraries (e.g. rank-bm25, bm25s, Whoosh): license, pip install size, Python version compatibility, maintenance status
- [ ] Identify the user setup impact: which library to `pip install`, whether it must be added to a requirements file, whether setup scripts need updating
- [ ] Present library comparison and recommended choice to user; get approval before proceeding
- [ ] Draft the BM25 step as a standalone markdown block: index build, term extraction by LLM from question, BM25 query, answer generation from hits, Step-6 verifier reuse, PASS/FAIL branching into semantic-search fallback
- [ ] Consult Software Engineer expert (subagent) to review for correctness and edge cases
- [ ] Revise based on findings
- [ ] Save final draft to `.rn/issue-382/bm25-step-draft.md`
- [ ] User review — present full draft and get approval before implementation
- [ ] Self-check: library choice approved, all branches (no hits, PASS, FAIL→fallback) specified, setup steps documented

**Completion criteria**:

- BM25 library selected and user-approved, with setup steps documented
- `.rn/issue-382/bm25-step-draft.md` exists with the full step text
- All branches (no BM25 hits, PASS, FAIL→fallback) are explicitly specified
- User has approved the draft

---

### #3: Implement BM25 step in v6 qa.md and verify incrementally

**Purpose**: Insert the approved BM25 step into v6 `qa.md` and verify correctness
incrementally — single scenario first, then path-coverage sample, then full 3-run benchmark
— following the HOW-TO-RUN.md procedure.

**Prerequisites**: #1 (baseline), #2 (approved draft)

**Steps**:

- [ ] Insert the approved BM25 step into `.claude/skills/nabledge-6/workflows/qa.md` before the current Step 3; renumber subsequent steps if needed
- [ ] **Phase A (1 scenario)**: run `pre-01` via `run_qa --scenario-ids pre-01`; confirm exit 0, answer.md non-empty, BM25 path exercised; delete tmp dir after
- [ ] **Path-coverage sample (3–5 scenarios)**: select scenarios that cover BM25-complete path, BM25-FAIL→fallback path, and no-hits path; run them; inspect `workflow_details.json` to confirm each path behaved as designed; fix qa.md if any path misbehaves
- [ ] **Phase B/C full benchmark**: 3 runs × 34 scenarios per HOW-TO-RUN.md; generate per-run reports and crossrun-summary; commit each run immediately after completion
- [ ] Phase E regression check: compare against baseline from #1
- [ ] Save comparison summary to `.rn/issue-382/benchmark-result.md`
- [ ] Software Engineer expert review (subagent)
- [ ] User review
- [ ] Commit and push `qa.md` change + benchmark results

**Completion criteria**:

- `.claude/skills/nabledge-6/workflows/qa.md` contains the BM25 pre-search step
- Phase A: single-scenario run exits 0 and BM25 path is exercised
- Path-coverage sample: all three paths (BM25-complete, BM25-FAIL→fallback, no-hits) confirmed working
- Full benchmark (3 runs): regression check CLEAN vs baseline from #1
- Full benchmark: p50 cost per query lower than baseline p50
- `.rn/issue-382/benchmark-result.md` documents the comparison

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
