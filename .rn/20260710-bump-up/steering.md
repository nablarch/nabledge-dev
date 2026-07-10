Rn version: 0.8.0

# Goal

Release the latest nabledge improvements that have been merged to main since marketplace 0.10 (2026-06-18).

# Acceptance criteria

- Nablarch developers using nabledge can access all improvements merged since marketplace 0.10
- The release artifacts comply with `.claude/rules/release.md` (CHANGELOG entries, version files, PR)

# Assumptions

- "Since marketplace 0.10" means commits after `a9f05000` (the 0.10 release commit on 2026-06-18)

# Rules

- commit and push every change; one completion marker per task
- Stage files individually, never `git add -A`

# Tasks

### #1: Analyze commits since 0.10 and propose release content

**Purpose**: Determine which commits have user-facing impact, propose CHANGELOG entries and version numbers, and get user approval before touching any files.

**Prerequisites**: none

**Steps**:

- [ ] For each commit since `a9f05000`, check whether changed files fall under deployed content (per sync-manifest.txt)
- [ ] For each deployed-content commit, identify the full user impact (not just file names — read the actual diff to understand what changed for the user)
- [ ] Propose CHANGELOG entry text for each affected plugin, following `.claude/rules/changelog.md` writing guidelines
- [ ] Propose version numbers for affected plugins and marketplace per `.claude/rules/release.md` version scheme
- [ ] Self-check: no deployed-content commit left unaccounted for; CHANGELOG entries describe user impact, not implementation details
- [ ] Present analysis and proposal to user; wait for approval via `/rn:ty` or `/rn:gm`

**Completion criteria**:

- Every commit since 0.10 is classified as deployed-content or dev-only, with evidence (which files changed)
- User has approved the proposed CHANGELOG entries and version numbers via `/rn:ty`

### #2: Update release files

**Purpose**: Apply the approved CHANGELOG entries and version bumps to all required files per `.claude/rules/release.md` step 3.

**Prerequisites**: #1 approved

**Steps**:

- [ ] Update each affected plugin's CHANGELOG.md: add versioned section per approved text, add tag link at bottom
- [ ] Update each affected plugin's plugin.json: bump to approved version
- [ ] Update marketplace.json: bump to approved version
- [ ] Update marketplace/CHANGELOG.md: add row for new marketplace version
- [ ] Verify against previous release PR file set per `.claude/rules/release.md` step 4
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-2.md)

**Completion criteria**:

- All affected plugin CHANGELOGs and plugin.json files reflect the approved versions and entries
- marketplace.json and marketplace/CHANGELOG.md are updated consistently
- Verified against previous release PR: no required file is missing

### #3: Create feature branch, commit, and open PR

**Purpose**: Commit the release files on a feature branch and open a PR per `.claude/rules/pr.md`.

**Prerequisites**: #2 complete

**Steps**:

- [ ] Create feature branch `399-release-marketplace-0.10.1` from `worktree-bump-up`
- [ ] Stage and commit release files (individual `git add`)
- [ ] Push branch
- [ ] Create work log files (tasks.md, notes.md) in `.work/00399/`
- [ ] Create PR using `Skill(skill: "pr", args: "create")`
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-3.md)

**Completion criteria**:

- Feature branch is pushed and PR is open against `main`
- PR title and body follow `.claude/rules/pr.md`

### #4: Evaluation sign-off

**Purpose**: Confirm all acceptance criteria are met and take user sign-off.

**Prerequisites**: #3 complete

**Steps**:

- [ ] Verify each acceptance criterion with evidence
- [ ] Present results to user
- [ ] Take verdict via `/rn:ty` (approve) or `/rn:gm` (revise)

**Completion criteria**:

- All acceptance criteria are met with evidence
- User has approved via `/rn:ty`

# State

- **Status**: not suspended
- **Date**: 2026-07-10
- **Last completed**: (none)
- **Next**: #1 — analyze commits since 0.10 and propose release content
- **Notes**: worktree branch is `worktree-bump-up`. Feature branch created at task #3.
