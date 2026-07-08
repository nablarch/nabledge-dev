Rn version: 0.8.0
Design: .rn/20260708-issue-395/design.md

# Goal

Add section-level links to cited knowledge MD files in skill output. Currently QA answers show bare `参照: file.json:sN` citations and code-analysis Nablarch usage shows file-level-only links; users cannot jump directly to the cited section without manual lookup.

# Acceptance criteria

- QA (SC and QA mode) answer `参照:` lines are rendered as `[セクションタイトル](docs/path.md#anchor)` links pointing to the exact section
- code-analysis Nablarch usage `**詳細**:` fields include a section-level link for each knowledge section read during Step 3
- Linked anchors are reachable: following a link opens the correct section in the knowledge MD (anchor matches GitHub Markdown heading anchor for that section's title)
- Benchmark scores do not degrade compared to pre-change baseline (a benchmark run before and after shows no regression)
- Change is applied to all 5 skill versions (nabledge-1.2, 1.3, 1.4, 5, 6)

# Assumptions

- GitHub Markdown anchor generation rule: lowercase the heading text, remove `[^\w -]` characters (keeping CJK, alphanumeric, hyphens, underscores, spaces), replace runs of spaces with single hyphens — verified empirically against existing docs
- Section titles in JSON match the heading text in the corresponding MD file exactly — confirmed for sampled files
- QA output is rendered in GitHub Markdown (Claude Code chat) where `[text](path.md#anchor)` links are clickable
- code-analysis output is written to `.nabledge/YYYYMMDD/` — relative path prefix `../../` is already used for file-level links; section links use the same prefix + `#anchor`
- All 5 versions share identical `qa.md` structure (processing-type list differs but citation format is the same); `code-analysis.md` differs only in version-specific path names

# Rules

- commit and push every change; one completion marker per task
- Cross-version rule: apply the same change to all 5 versions in a single commit per artifact type (per `.claude/rules/nabledge-skill.md`)
- No manual edits to RBKC-generated files (knowledge JSON, docs MD)
- Benchmark run: `bash tools/tests/test-setup.sh` or equivalent per the existing benchmark tooling

# Tasks

### #1: Design sign-off

**Purpose**: Confirm the anchor-generation approach, link format for QA and code-analysis, and scope before implementation begins.

**Prerequisites**: none

**Steps**:

- [ ] Present `design.md` to the user
- [ ] Take verdict via `/rn:ty` (approve) or `/rn:gm` (revise)

**Completion criteria**:

- `design.md` is approved by the user
- No open structural questions remain about link format or anchor algorithm

### #2: Implement QA section links — all 5 versions

**Purpose**: Update `qa.md` in all 5 versions so the `参照:` line emits `[セクションタイトル](docs/path.md#anchor)` links instead of bare `file.json:sN` citations.

**Prerequisites**: #1 approved

**Steps**:

- [ ] Identify exact line(s) to change in `.claude/skills/nabledge-6/workflows/qa.md`
- [ ] Draft the new instruction text (anchor algorithm, link format, where section title comes from)
- [ ] Apply change to nabledge-6/workflows/qa.md
- [ ] Apply same change to nabledge-5, 1.4, 1.3, 1.2 (verify diff identical except version-specific parts)
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-2.md)
- [ ] Prompt Engineer expert review (subagent)
- [ ] Verification expert review (subagent)

**Completion criteria**:

- `参照:` instruction in all 5 `qa.md` files specifies Markdown link format `[title](path#anchor)` for each cited section
- Anchor algorithm matches GitHub Markdown spec (lowercase, strip non-word except hyphens/spaces, spaces→hyphens)
- No existing QA instruction content removed or altered beyond the citation format change
- The 5 files differ only in processing-type lists, not in the citation format instruction

### #3: Implement code-analysis section links — all 5 versions

**Purpose**: Update `code-analysis.md` and `code-analysis/template-guide.md` in all 5 versions so `**詳細**:` in Nablarch usage includes a section-level link to each knowledge section read in Step 3.

**Prerequisites**: #1 approved

**Steps**:

- [ ] Identify exact line(s) to change in code-analysis.md (Step 3 read-section tracking) and template-guide.md (詳細 format)
- [ ] Draft the new instruction: Step 3 reads sections → workflow carries `{file, section_id, title}` forward to Step 4 → 詳細 link uses that info
- [ ] Apply change to nabledge-6 code-analysis.md and template-guide.md
- [ ] Apply same change to nabledge-5, 1.4, 1.3, 1.2
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-3.md)
- [ ] Prompt Engineer expert review (subagent)
- [ ] Verification expert review (subagent)

**Completion criteria**:

- `**詳細**:` instruction in all 5 versions specifies section-level link format `[file title](docs/path.md) > [section title](docs/path.md#anchor)` (or equivalent)
- Workflow instruction explains how to carry section-id metadata from Step 3 to Step 4 for link generation
- No existing code-analysis instruction content removed or altered beyond the link format change

### #4: Benchmark verification

**Purpose**: Confirm benchmark scores do not degrade after the workflow changes.

**Prerequisites**: #2 and #3 completed

**Steps**:

- [ ] Confirm the benchmark command and interpret results
- [ ] Record pre-change baseline (from latest metrics report in `docs/metrics.md` or by running benchmark)
- [ ] Run benchmark after changes
- [ ] Compare scores; confirm no regression
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-4.md)

**Completion criteria**:

- Benchmark pass rate after change ≥ baseline pass rate (no regression)
- Any difference is explainable (e.g. format change improves citations) or within noise

### #5: Evaluation sign-off

**Purpose**: Final review of all changes against Acceptance criteria.

**Prerequisites**: #4 completed

**Steps**:

- [ ] Present Acceptance criteria run result to the user
- [ ] Take verdict via `/rn:ty` (approve) or `/rn:gm` (revise)

**Completion criteria**:

- All Acceptance criteria verified as met
- User approves the changes via `/rn:ty`

# State

- **Status**: not suspended
- **Date**: 2026-07-08
- **Last completed**: (none)
- **Next**: #1 Design sign-off
- **Notes**: Branch is `worktree-395-add-md-section-links` (existing worktree). Task #2 and #3 can proceed in parallel once #1 is approved.
