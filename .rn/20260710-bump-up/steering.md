Rn version: 0.8.0

# Goal

Release the improvements merged to main since marketplace 0.10 (2026-06-18): specifically the `code-analysis.md` rewrite across all 5 versions (`c1a37ad7`). The release follows `.claude/rules/release.md` step by step.

# Acceptance criteria

- All 5 plugin CHANGELOGs have a new versioned section (e.g. `## [0.9.1] - 2026-07-10`) with one entry for the code-analysis.md improvement
- All 5 `plugin.json` files reflect the new version
- `marketplace.json` version is bumped to `0.10.1`
- `marketplace/CHANGELOG.md` has a new row for `0.10.1` in the version table
- No deployed-content file is missing (verified against the 0.10 release PR file set)
- PR is open against `main`

# Assumptions

- Only `c1a37ad7` (code-analysis.md rewrite) has user-facing impact since 0.10; all other commits since 2026-06-18 are dev-only (confirmed by grepping sync-manifest paths)
- The change is a PATCH (quality improvement, no new features) → version increment is PATCH across all plugins
- Version scheme: nabledge-6 0.9→0.9.1, nabledge-5 0.4→0.4.1, nabledge-1.4/1.3/1.2 0.3→0.3.1, marketplace 0.10→0.10.1

# Rules

- commit and push every change; one completion marker per task
- Follow `.claude/rules/release.md` step 3 (update files) to step 5 (create PR)
- Stage files individually, never `git add -A`
- Commit messages: `chore: release nabledge improvements as marketplace 0.10.1 (#399)`

# Tasks

### #1: Confirm commit analysis and propose CHANGELOG entry

**Purpose**: Present the findings from commit analysis to the user and get approval for the CHANGELOG wording before touching any files.

**Prerequisites**: none

**Steps**:

- [ ] Present commit analysis summary (which commits have user impact, which are dev-only)
- [ ] Propose CHANGELOG entry text for all 5 plugins
- [ ] Propose version numbers for all 5 plugins and marketplace
- [ ] Self-check: proposal covers all deployed-content commits
- [ ] Wait for user approval (`/rn:ty` or `/rn:gm`)

**Completion criteria**:

- User has approved the CHANGELOG wording and version numbers via `/rn:ty`
- No deployed-content commit is left unaccounted for in the proposal

### #2: Update 4 versioning files

**Purpose**: Apply the approved CHANGELOG entries and version bumps to all 4 required files per `.claude/rules/release.md` step 3.

**Prerequisites**: #1 approved

**Steps**:

- [ ] Update `nabledge-6/plugin/CHANGELOG.md`: add versioned section, add tag link at bottom
- [ ] Update `nabledge-6/plugin/plugin.json`: bump version to 0.9.1
- [ ] Update `nabledge-5/plugin/CHANGELOG.md`: add versioned section, add tag link at bottom
- [ ] Update `nabledge-5/plugin/plugin.json`: bump version to 0.4.1
- [ ] Update `nabledge-1.4/plugin/CHANGELOG.md`: add versioned section, add tag link at bottom
- [ ] Update `nabledge-1.4/plugin/plugin.json`: bump version to 0.3.1
- [ ] Update `nabledge-1.3/plugin/CHANGELOG.md`: add versioned section, add tag link at bottom
- [ ] Update `nabledge-1.3/plugin/plugin.json`: bump version to 0.3.1
- [ ] Update `nabledge-1.2/plugin/CHANGELOG.md`: add versioned section, add tag link at bottom
- [ ] Update `nabledge-1.2/plugin/plugin.json`: bump version to 0.3.1
- [ ] Update `marketplace.json`: bump version to 0.10.1
- [ ] Update `marketplace/CHANGELOG.md`: add row for 0.10.1
- [ ] Verify against previous release PR file set (step 4 in release.md)
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-2.md)

**Completion criteria**:

- All 5 plugin CHANGELOGs contain the new versioned section matching the approved text
- All 5 `plugin.json` files show the new version
- `marketplace.json` shows `0.10.1`
- `marketplace/CHANGELOG.md` shows a `0.10.1` row in the table
- Verified against the previous release PR: no core file is missing

### #3: Commit, push, and create PR

**Purpose**: Commit the release files, push the branch, and open a PR per `.claude/rules/pr.md`.

**Prerequisites**: #2 complete

**Steps**:

- [ ] Stage and commit release files (individual `git add`)
- [ ] Push branch
- [ ] Create work log files (tasks.md, notes.md) in `.work/00399/`
- [ ] Create PR using `Skill(skill: "pr", args: "create")`
- [ ] Self-check (OK/NG per completion criterion, record in checks/task-3.md)

**Completion criteria**:

- Branch is pushed and PR is open against `main`
- PR title follows `<type>: <description> (#399)` format
- PR body links to tasks.md per `.claude/rules/pr.md`

### #4: Evaluation sign-off

**Purpose**: Present the acceptance criteria run to the user and take sign-off.

**Prerequisites**: #3 complete

**Steps**:

- [ ] Run acceptance criteria check against all criteria
- [ ] Present results to user
- [ ] Take verdict via `/rn:ty` (approve) or `/rn:gm` (revise)

**Completion criteria**:

- All Acceptance criteria are met (verified with evidence)
- User has approved via `/rn:ty`

# State

- **Status**: not suspended
- **Date**: 2026-07-10
- **Last completed**: (none)
- **Next**: #1 — present commit analysis and CHANGELOG proposal
- **Notes**: branch is `worktree-bump-up` (worktree base branch). Feature branch will be created at task #3 per git-workflow.md rules. Current worktree is `bump-up`.
