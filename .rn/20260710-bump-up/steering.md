Rn version: 0.8.0

# Goal

Release the latest nabledge improvements that have been merged to main since marketplace 0.10 (2026-06-18).

# Acceptance criteria

- A Nablarch developer who installs the new version can use all improvements merged since marketplace 0.10
- The CHANGELOG accurately describes what changed and why it matters to the user

# Assumptions

- "Since marketplace 0.10" means commits after `a9f05000` (the 0.10 release commit on 2026-06-18)

# Rules

- commit and push every change; one completion marker per task

# Tasks

### ~~#1: Analyze commits since 0.10 and propose release content~~

**Purpose**: Determine the release scope and content — what changed for the user and how to describe it.

**Prerequisites**: none

**Steps**:

- [ ] For each commit since `a9f05000`, check whether changed files fall under deployed content (per sync-manifest.txt)
- [ ] For each deployed-content commit, read the actual diff to understand the full user impact
- [ ] Propose CHANGELOG entry text for each affected plugin, following `.claude/rules/changelog.md` writing guidelines
- [ ] Propose version numbers for affected plugins and marketplace per `.claude/rules/release.md` version scheme
- [ ] Self-check: no deployed-content commit left unaccounted for; CHANGELOG entries describe user impact, not implementation details
- [ ] Present analysis and proposal to user; wait for approval via `/rn:ty` or `/rn:gm`

**Completion criteria**:

- The release scope is unambiguous: it is clear what is included, what is excluded, and why
- The CHANGELOG entries describe what the user can now do or what problem was fixed — not what files changed

### ~~#2: Update release files~~

**Purpose**: Apply the approved CHANGELOG entries and version bumps to all required files per `.claude/rules/release.md` step 3.

**Prerequisites**: #1 approved

**Steps**:

- [ ] Update each affected plugin's CHANGELOG.md: add versioned section per approved text, add tag link at bottom
- [ ] Update each affected plugin's plugin.json: bump to approved version
- [ ] Update marketplace.json: bump to approved version
- [ ] Update marketplace/CHANGELOG.md: add row for new marketplace version
- [ ] Compare changed file set against the previous release PR to confirm no required file is missing
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-2.md)

**Completion criteria**:

- A user reading the CHANGELOG would understand what improved and how it affects their work
- No improvement is silently omitted; no file required for distribution is missing

### #3: Create feature branch, commit, and open PR

**Purpose**: Make the release reviewable and mergeable.

**Prerequisites**: #2 complete

**Steps**:

- [ ] Create feature branch from `worktree-bump-up` using the approved version as slug
- [ ] Stage and commit release files (individual `git add`)
- [ ] Push branch
- [ ] Create work log files (tasks.md, notes.md) in `.work/00399/`
- [ ] Create PR using `Skill(skill: "pr", args: "create")`
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-3.md)

**Completion criteria**:

- A reviewer can understand the release scope and verify its correctness without asking the author for context

### #4: Evaluation sign-off

**Purpose**: Confirm all acceptance criteria are met and take user sign-off.

**Prerequisites**: #3 complete

**Steps**:

- [ ] Verify each acceptance criterion with evidence
- [ ] Present results to user
- [ ] Take verdict via `/rn:ty` (approve) or `/rn:gm` (revise)

**Completion criteria**:

- All acceptance criteria are met with evidence
- User has signed off via `/rn:ty`

# State

<!-- updated by /rn:up -->

