# Goal

`code-analysis.md` (all 5 versions: nabledge-1.2/1.3/1.4/5/6) has grown to 685 lines —
approximately 3× the size of comparable workflow files such as `qa.md` (243 lines). The
file was extended incrementally in response to observed AI errors, resulting in repetitive
rules, structural ambiguity, and instructions that may conflict or be skipped by the AI.

The goal is to review and rewrite `code-analysis.md` following prompt engineering best
practices: eliminate redundancy, establish a clear and navigable structure, resolve
conflicts, and ensure every rule appears in exactly one authoritative location. The
outcome is a file that prompt engineers can maintain with confidence and that the AI
follows consistently.

# Acceptance criteria

- `code-analysis.md` for nabledge-6 is ≤ 400 lines (the 685 → ~400 target, matching the
  structural complexity of `qa.md` scaled for this workflow's larger scope)
- Every rule appears in exactly one location (no duplicated instructions)
- The file has a clear, scannable structure: a prompt engineer can locate any rule by
  section heading without reading the entire file
- No conflicting instructions exist (e.g., two sections that give opposite guidance for
  the same scenario)
- The same rewrite is applied to all 5 versions (nabledge-1.2/1.3/1.4/5/6); the v6
  rewrite is the source of truth and is ported to the other versions with only
  version-specific differences preserved
- Task #6 DeepEval scores for all scenarios are ≥ Task #2 baseline scores (no regression)
- `qa.md` (243 lines) is not changed — it is used as a style reference only

# Assumptions

- The 5 versions of `code-analysis.md` are currently identical in content (verified:
  all are 685 lines); version-specific differences, if any, will be discovered during
  the rewrite
- Prompt engineering best practices in this context means: single authoritative location
  per rule, progressive disclosure (overview → detail), explicit step boundaries, no
  contradictory guidance
- `qa.md` is the canonical style reference for workflow files in this repo
- The existing `tools/benchmark/` infrastructure (runner, evaluate.py, DeepEval) is
  reusable as the model for the code-analysis test harness
- A known Nablarch code sample (e.g., from `.lw/nab-official/`) is available as test
  input with verifiable expected facts

# Rules

- commit and push every change; one completion marker per task
- Apply the CLAUDE.md cross-version consistency rule: v6 is the source of truth;
  port the same rewrite to all 5 versions in a single commit
- Do not change `qa.md` — it is a reference, not a target
- Do not change scripts, templates, or other files unless a specific rule in
  `code-analysis.md` is factually wrong about them (investigate before changing)
- Task #2 baseline must be committed before any change to `code-analysis.md`

# Tasks

### #1: Build test harness — runner, scenarios, and format checker for code-analysis

**Purpose**: Build the evaluation infrastructure that Tasks #2 and #6 both use: a
runner that executes the code-analysis workflow end-to-end, scenarios with known inputs
and `must` facts, and a format checker script.

**Prerequisites**: none

**Steps**:

- [x] Read `tools/benchmark/scripts/run_qa.py` and `evaluate.py` to understand the
      existing runner/evaluator pattern
- [x] Identify a known Nablarch source file (from `.lw/nab-official/v6/`) with
      verifiable expected outputs (dependency classes, Nablarch components used)
      **NOTE: 初回実装は `.lw` ではなく nabledge-1.4 のクラスを使っており無効。v6 のクラスに作り直す。**
- [x] Define ≥ 3 scenarios in `tools/benchmark/scenarios/code-analysis.json`:
      each scenario has `when.input` (target class name) and `then.must`
      (facts that must appear in the output, e.g., specific dependency names,
      Nablarch component references)
      **NOTE: 上記と同じ理由で作り直し。**
- [x] Implement `tools/benchmark/scripts/run_code_analysis.py` following the
      `run_qa.py` pattern: invoke `claude -p` with the code-analysis workflow,
      capture output, run evaluate.py for DeepEval scoring
- [x] Implement `tools/benchmark/scripts/check_format_code_analysis.py`: verify
      placeholder replacement (no `{{...}}` remaining), section presence
      (all 7 template sections exist), Mermaid syntax (`classDiagram`,
      `sequenceDiagram` present)
- [x] Create `tools/benchmark/HOW-TO-RUN-CODE-ANALYSIS.md` documenting how to run
      `run_code_analysis.py` and `check_format_code_analysis.py`
      (execution commands, expected outputs, result directory structure)
- [x] Self-check (OK/NG per completion criterion, record in checks/task-1.md)
- [x] QA expert review (subagent)
- [x] Language expert review (subagent)
- [x] Software-engineering expert review (subagent)
- [x] User review

**Completion criteria**:

- `tools/benchmark/scenarios/code-analysis.json` exists with ≥ 3 scenarios, each
  with ≥ 2 `must` facts
- `tools/benchmark/scripts/run_code_analysis.py` exists and exits 0 on a dry-run
  (argument parsing, file loading — no actual claude invocation required)
- `tools/benchmark/scripts/check_format_code_analysis.py` exists and correctly
  detects at least: unreplaced placeholders, missing sections, absent Mermaid blocks
  (verified by unit tests or manual check with a crafted fixture)
- `tools/benchmark/HOW-TO-RUN-CODE-ANALYSIS.md` exists with commands sufficient
  to run a code-analysis benchmark independently without reading the source code

### #2: Capture baseline — run current workflow and record scores

**Purpose**: Execute the current 685-line `code-analysis.md` against the Task #1
scenarios and record DeepEval scores and format-check results as the baseline that
Task #6 will compare against.

**Prerequisites**: Task #1 complete

**Steps**:

- [x] Run `run_code_analysis.py` against all scenarios using the current
      `code-analysis.md`
- [x] Run `check_format_code_analysis.py` on each output
- [x] Save all results to `tools/benchmark/results/YYYYMMDD-HHMM-code-analysis-baseline/`
- [x] Record a summary table (scenario, DeepEval score, format check pass/fail) in
      `.rn/refact-code-analysis/baseline.md`
- [x] Self-check (OK/NG per completion criterion, record in checks/task-2.md)
- [x] QA expert review (subagent) — objective scores, no subjective review needed
- [x] User review

**Completion criteria**:

- `tools/benchmark/results/code-analysis-baseline/` exists with output files for
  all scenarios
- `.rn/refact-code-analysis/baseline.md` exists with a summary table covering all
  scenarios
- Baseline is committed before any change to `code-analysis.md`

### #3: Audit — identify all redundancies, conflicts, and structural problems

**Purpose**: Produce a written audit of `code-analysis.md` that catalogs every
redundancy, conflict, misplaced rule, and structural issue — the evidence base for
the rewrite.

**Prerequisites**: Task #2 complete

**Steps**:

- [x] Read `code-analysis.md` (nabledge-6 version) in full
- [x] Read `qa.md` as a style reference
- [x] Identify and list: duplicate rules (same instruction stated ≥2 times), conflicting
      rules (two instructions that contradict each other), structural issues (rules buried
      in wrong sections, no clear entry point, etc.), and verbose passages that can be
      stated more concisely without loss
- [x] For each finding, record: location (line range), category (duplicate / conflict /
      misplaced / verbose), and a one-line description of the problem
- [x] Count total findings by category
- [x] Self-check (OK/NG per completion criterion, record in checks/task-3.md)
- [x] QA expert review (subagent) — audit findings are objective; no separate QA needed
- [x] User review

**Completion criteria**:

- Audit document exists at `.rn/refact-code-analysis/audit.md`
- Every finding cites a specific line range in the 685-line file
- Findings are grouped by category (duplicate / conflict / misplaced / verbose)
- Total count per category is stated
- No finding is stated without a line reference

### #4: Design — propose the rewritten structure

**Purpose**: Produce a structural design for the rewritten `code-analysis.md` — section
headings, ordering rationale, and a mapping of every current rule to its target location
— so the rewrite in Task #5 has a verified blueprint.

**Prerequisites**: Task #3 complete

**Steps**:

- [x] Read the audit from Task #3
- [x] Draft a section outline (headings and 1-sentence purpose per section)
- [x] For each rule in the audit, map: current location → target section in the new
      structure (or "drop" if it is a pure duplicate with no unique content)
- [x] Identify any rules that are currently missing from the file but required by the
      workflow logic (gaps)
- [x] Self-check (OK/NG per completion criterion, record in checks/task-4.md)
- [x] QA expert review (subagent) — design is structural; objective mapping, no separate QA needed
- [x] User review

**Completion criteria**:

- Design document exists at `.rn/refact-code-analysis/design.md`
- Section outline has ≥ 4 sections, each with a stated purpose
- Every finding from the audit is mapped to a target section or marked "drop"
- Any gaps identified are listed
- The projected line count for the rewritten file is stated and is ≤ 400

### #5: Rewrite — apply the design to produce the new code-analysis.md

**Purpose**: Produce the rewritten `code-analysis.md` for nabledge-6 following the
approved design, then port it to all 5 versions.

**Prerequisites**: Task #4 complete and approved by user

**Steps**:

- [x] Read the design from Task #4
- [x] Rewrite nabledge-6's `code-analysis.md` following the approved section structure
- [x] Verify: line count ≤ 400, no duplicate rules, no conflicting instructions
- [x] Port the rewrite to nabledge-1.2, 1.3, 1.4, 5 — applying only version-specific
      differences (e.g., script paths, version-specific step names)
- [x] Verify all 5 versions are consistent in structure
- [x] Self-check (OK/NG per completion criterion, record in checks/task-5.md)
- [x] QA expert review (subagent) — 2 Findings fixed (read-sections.sh path, verify string)
- [ ] User review

**Completion criteria**:

- nabledge-6 `code-analysis.md` is ≤ 400 lines
- All 5 versions exist and are structurally identical (diff shows only version-specific
  path/name differences)
- No rule appears more than once in any single version
- No two instructions in any single version contradict each other

### #6: Verify — re-run scenarios against rewritten file and compare with baseline

**Purpose**: Confirm the rewritten instructions produce equal or better scores than
the baseline recorded in Task #2, using the same runner, scenarios, and evaluator.

**Prerequisites**: Task #5 complete

**Steps**:

- [ ] Run `run_code_analysis.py` against all scenarios using the rewritten
      `code-analysis.md`
- [ ] Run `check_format_code_analysis.py` on each output
- [ ] Save results to `tools/benchmark/results/code-analysis-verify/`
- [ ] Compare scores against baseline: produce a before/after table (scenario,
      baseline score, verify score, delta)
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-6.md)
- [ ] QA expert review (subagent)
- [ ] User review

**Completion criteria**:

- `tools/benchmark/results/code-analysis-verify/` exists with output files for
  all scenarios
- Before/after comparison table exists in `.rn/refact-code-analysis/verification.md`
- All DeepEval scores in verify ≥ corresponding baseline scores (no regression)
- All format checks pass in verify

# Decisions

(none yet)

# State

- **Status**: awaiting user review
- **Date**: 2026-07-03
- **Last completed**: #5 rewrite complete (685→339 lines, all 5 versions, QA 2 Findings fixed)
- **Next**: User review of Task #5, then #6 — Verify
- **Notes**: |
    Design in .rn/refact-code-analysis/design.md (153 lines).
    Structure: Steps renumbered 0–4 (target → start → deps → knowledge → doc gen).
    Key changes: Best practices + Output template sections dropped; class/sequence
    diagram instructions merged into unified blocks; Example execution moved to top.
    3 gaps added (G-01/02/03).
    Projected: ~395–405 lines (within ≤400 target).
