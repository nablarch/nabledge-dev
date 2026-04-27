# Release Process

## Repository Responsibilities

**nabledge-dev** (this repository):
- Development of nabledge skills
- Automatic sync to `nablarch/nabledge:develop` on push to `main`
- No version management or tagging

**nablarch/nabledge**:
- Distribution repository for end users
- `develop` branch: Latest development state (auto-synced from nabledge-dev)
- `main` branch: Stable releases
- Version management, tagging, and release workflow

## Development Workflow (nabledge-dev)

1. Work on feature branches from `main`
2. Create PR and merge to `main` after review
3. Changes automatically sync to `nablarch/nabledge:develop`
4. Users can test unreleased features from develop branch

## Release Preparation Workflow (nabledge-dev)

This is the release work done in this repository before syncing to nablarch/nabledge.

### Version Format

There are two independent version schemes:

**Plugin version** (individual): Each plugin (`nabledge-6`, `nabledge-5`) has its own version.
- Format: **MINOR.PATCH** (e.g., 0.1, 0.2, 0.1.1)
- Stored in `plugin.json` and plugin `CHANGELOG.md`
- Tag links in plugin CHANGELOG follow Keep a Changelog format: each version heading `## [X.Y]` links to the marketplace release tag where that plugin version was first included (e.g., nabledge-5 v0.1 released in marketplace 0.6 → `releases/tag/0.6`)

**Marketplace version** (overall): Covers all plugins together.
- Set to the highest plugin version across all changed plugins
- Stored in `marketplace.json` and marketplace `CHANGELOG.md`
- Tags in nablarch/nabledge use the marketplace version

Example: nabledge-6 v0.6 + nabledge-5 v0.1 released together → marketplace v0.6

- **MINOR**: Feature additions (new knowledge, workflows, functionality)
- **PATCH**: Fixes and improvements only
- **User approval required** - AI suggests, user decides final version

### Step 1: Analyze Commits Since Last Release

Get all commits since the previous version tag:

```bash
git log --oneline --since="{last release date}"
```

For each commit, determine user impact by checking whether changed files fall under deployed content (per `.github/workflows/sync-to-nabledge/sync-manifest.txt`):

**Deployed content scope:**
- `.claude/skills/nabledge-6/` — skill content, knowledge files, workflows
- `.claude/skills/nabledge-5/` — skill content, knowledge files, workflows
- `.claude/marketplace/` — marketplace metadata
- `.claude/commands/n6.md`, `.claude/commands/n5.md`
- `.github/prompts/n6.prompt.md`, `.github/prompts/n5.prompt.md`
- `tools/setup/setup-6-cc.sh`, `tools/setup/setup-6-ghc.sh`
- `tools/setup/setup-5-cc.sh`, `tools/setup/setup-5-ghc.sh`

**Not deployed (no user impact):**
- `.github/workflows/`, `.github/scripts/` — CI/CD infra
- `.claude/rules/`, `.claude/skills/nabledge-test/` — dev-only
- `README.md`, `CLAUDE.md`, `docs/` — dev repo files

Output findings as a work log in `.work/{issue_number}/notes.md` and confirm with the user before proceeding.

### Step 2: Review and Revise CHANGELOG

Review current `[Unreleased]` section in `.claude/skills/nabledge-6/plugin/CHANGELOG.md` against confirmed user-impact commits. Apply changelog writing rules (see `.claude/rules/changelog.md`):

- Remove technical implementation details (architecture names, file names, internal metrics)
- Remove entries where user impact is not clearly demonstrable (case-by-case improvements without concrete numbers)
- Consolidate related changes into single user-facing statements
- Use past tense: "〜しました" not "〜します"

**Propose revised CHANGELOG content to user and confirm before updating files.**

### Step 3: Update Files

After user confirmation, update all 4 versioning files:

**`.claude/skills/nabledge-6/plugin/CHANGELOG.md`**

Replace `## [Unreleased]` with versioned section, and add tag link at bottom:

```markdown
## [0.5] - 2026-03-10

### 追加
- ...

[0.5]: https://github.com/nablarch/nabledge/releases/tag/0.5
[0.4]: https://github.com/nablarch/nabledge/releases/tag/0.4
```

**`.claude/skills/nabledge-6/plugin/plugin.json`**

```json
{
  "version": "0.5"
}
```

**`.claude/marketplace/.claude-plugin/marketplace.json`**

```json
{
  "metadata": {
    "version": "0.5"
  }
}
```

**`.claude/marketplace/CHANGELOG.md`**

Add a row at the top of the version table:

```markdown
| 0.5 | [0.5](plugins/nabledge-6/CHANGELOG.md#05---2026-03-10) | - | 2026-03-10 |
```

### Step 4: Verify Against Previous Release PR

Compare changed files with the previous release PR to confirm no core file is missing.

The 4 files above are the required set. Extra files in a previous release PR (rule updates, expert reviews, work logs) are not release-specific and can be ignored.

Document the comparison result in the work log.

### Step 5: Create PR

Use `/hi {issue_number}` or `/pr create` to create a PR to `main`.

---

## Release Workflow (nablarch/nabledge)

After merging to `main` in nabledge-dev, changes sync automatically to `nablarch/nabledge:develop`. The release itself is managed in that repository.

1. **Create release PR** — From `develop` to `main`
2. **Tag and release** — After merge, create Git tag and GitHub release

### Multiple Skills

If both nabledge-6 and nabledge-5 changed, marketplace version = highest skill version (compare MINOR first, then PATCH).
