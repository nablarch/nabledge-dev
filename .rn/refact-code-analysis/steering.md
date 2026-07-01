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
- Representative test cases (at least 3 scenarios drawn from the current file's step
  descriptions) confirm the AI correctly follows the rewritten instructions
- `qa.md` (243 lines) is not changed — it is used as a style reference only

# Assumptions

- The 5 versions of `code-analysis.md` are currently identical in content (verified:
  all are 685 lines); version-specific differences, if any, will be discovered during
  the rewrite
- Prompt engineering best practices in this context means: single authoritative location
  per rule, progressive disclosure (overview → detail), explicit step boundaries, no
  contradictory guidance
- `qa.md` is the canonical style reference for workflow files in this repo
- The test cases will be drawn from the existing file's step descriptions, not from
  actual Nablarch projects (no live code execution needed)
- Changes to `code-analysis.md` do not require corresponding changes to scripts,
  templates, or other workflow files unless a rule references them incorrectly

# Rules

- commit and push every change; one completion marker per task
- Apply the CLAUDE.md cross-version consistency rule: v6 is the source of truth;
  port the same rewrite to all 5 versions in a single commit
- Do not change `qa.md` — it is a reference, not a target
- Do not change scripts, templates, or other files unless a specific rule in
  `code-analysis.md` is factually wrong about them (investigate before changing)
- Every step in the rewrite must be independently verifiable against the original
  685-line file

# Tasks

### #0: Baseline — record current behavior before any changes

**Purpose**: Document what the current 685-line `code-analysis.md` produces for
representative scenarios, so Task #4 can compare before/after and confirm the rewrite
did not regress.

**Prerequisites**: none

**Steps**:

- [ ] Select 3 representative scenarios from the current workflow steps (e.g., target
      not specified → ask user; dependency classification; output budget enforcement)
- [ ] For each scenario, trace the current instructions step-by-step and record:
      input, the instruction path followed, and the expected AI behavior
- [ ] Note any scenarios where the current instructions are ambiguous, contradictory,
      or require reading the entire file to locate the relevant rule
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-0.md)
- [ ] QA expert review (subagent)
- [ ] User review

**Completion criteria**:

- Baseline document exists at `.rn/refact-code-analysis/baseline.md`
- At least 3 scenarios are documented with: input, instruction path traced, expected
  behavior, and any ambiguity/problem found in the current file
- Document is committed before any change to `code-analysis.md`

### #1: Audit — identify all redundancies, conflicts, and structural problems in the current file

**Purpose**: Produce a written audit of `code-analysis.md` that catalogs every
redundancy, conflict, misplaced rule, and structural issue — the evidence base for
the rewrite.

**Prerequisites**: Task #0 complete

**Steps**:

- [ ] Read `code-analysis.md` (nabledge-6 version) in full
- [ ] Read `qa.md` as a style reference
- [ ] Identify and list: duplicate rules (same instruction stated ≥2 times), conflicting
      rules (two instructions that contradict each other), structural issues (rules buried
      in wrong sections, no clear entry point, etc.), and verbose passages that can be
      stated more concisely without loss
- [ ] For each finding, record: location (line range), category (duplicate / conflict /
      misplaced / verbose), and a one-line description of the problem
- [ ] Count total findings by category
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-1.md)
- [ ] QA expert review (subagent)
- [ ] User review

**Completion criteria**:

- Audit document exists at `.rn/refact-code-analysis/audit.md`
- Every finding cites a specific line range in the 685-line file
- Findings are grouped by category (duplicate / conflict / misplaced / verbose)
- Total count per category is stated
- No finding is stated without a line reference

### #2: Design — propose the rewritten structure

**Purpose**: Produce a structural design for the rewritten `code-analysis.md` — section
headings, ordering rationale, and a mapping of every current rule to its target location
— so the rewrite in Task #3 has a verified blueprint.

**Prerequisites**: Task #1 complete

**Steps**:

- [ ] Read the audit from Task #1
- [ ] Draft a section outline (headings and 1-sentence purpose per section)
- [ ] For each rule in the audit, map: current location → target section in the new
      structure (or "drop" if it is a pure duplicate with no unique content)
- [ ] Identify any rules that are currently missing from the file but required by the
      workflow logic (gaps)
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-2.md)
- [ ] QA expert review (subagent)
- [ ] User review

**Completion criteria**:

- Design document exists at `.rn/refact-code-analysis/design.md`
- Section outline has ≥ 4 sections, each with a stated purpose
- Every finding from the audit is mapped to a target section or marked "drop"
- Any gaps identified are listed
- The projected line count for the rewritten file is stated and is ≤ 400

### #3: Rewrite — apply the design to produce the new code-analysis.md

**Purpose**: Produce the rewritten `code-analysis.md` for nabledge-6 following the
approved design, then port it to all 5 versions.

**Prerequisites**: Task #2 complete and approved by user

**Steps**:

- [ ] Read the design from Task #2
- [ ] Rewrite nabledge-6's `code-analysis.md` following the approved section structure
- [ ] Verify: line count ≤ 400, no duplicate rules, no conflicting instructions
- [ ] Port the rewrite to nabledge-1.2, 1.3, 1.4, 5 — applying only version-specific
      differences (e.g., script paths, version-specific step names)
- [ ] Verify all 5 versions are consistent in structure
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-3.md)
- [ ] QA expert review (subagent)
- [ ] User review

**Completion criteria**:

- nabledge-6 `code-analysis.md` is ≤ 400 lines
- All 5 versions exist and are structurally identical (diff shows only version-specific
  path/name differences)
- No rule appears more than once in any single version
- No two instructions in any single version contradict each other

### #4: Verify — compare rewritten instructions against the baseline

**Purpose**: Confirm the rewritten instructions produce equal or better behavior than
the baseline recorded in Task #0 — using the same 3 scenarios so before/after is
directly comparable.

**Prerequisites**: Task #3 complete

**Steps**:

- [ ] Read the baseline from Task #0 (same 3 scenarios, same inputs)
- [ ] For each scenario, trace the rewritten instructions step-by-step and record:
      instruction path followed and expected AI behavior
- [ ] Compare against the baseline: did ambiguities get resolved? did contradictions
      disappear? can the relevant rule be found without reading the entire file?
- [ ] Record verdict per scenario: pass (behavior preserved or improved) / fail
      (regression)
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-4.md)
- [ ] QA expert review (subagent)
- [ ] User review

**Completion criteria**:

- Verification document exists at `.rn/refact-code-analysis/verification.md`
- All 3 baseline scenarios are re-traced against the rewritten file
- Each scenario states: input, instruction path (before and after), verdict
- All 3 scenarios pass (no regression from baseline)
- Any problem identified in the baseline that is now resolved is explicitly noted
- Any scenario that fails is linked to a specific line in the rewritten file

# Decisions

(none yet)

# State

- **Status**: not suspended
- **Date**: 2026-07-01
- **Last completed**: (none)
- **Next**: #0 Baseline
- **Notes**: Branch is `worktree-refact-code-analysis`. Session PR to be created after steering is approved.
