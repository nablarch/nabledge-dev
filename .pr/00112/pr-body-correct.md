Closes #112

## Approach

Implemented a whitelist approach to exclude development infrastructure files from plugin distribution. Instead of copying the entire `.github/` directory, the sync workflow and setup scripts now explicitly copy only `.github/prompts/` (useful for GitHub Copilot users) while excluding `.github/workflows/` and `.github/scripts/` directories.

Added cleanup steps to remove existing development infrastructure files from both the distribution repository (nablarch/nabledge) and user installations. This ensures clean state for both new deployments and upgrades from previous versions.

Chose whitelist over blacklist approach for better security - only explicitly approved directories are distributed, preventing accidental inclusion of future development files.

## Tasks

- [x] Modify transform script to use whitelist approach (copy only `.github/prompts/`)
- [x] Add cleanup step to sync workflow to remove existing infrastructure directories
- [x] Update setup script to use whitelist approach and clean up previously installed files
- [x] Verify shell script syntax for all modified scripts
- [x] Execute expert reviews (Software Engineer and DevOps Engineer)

## Expert Review

AI-driven expert reviews conducted before PR creation (see `.claude/rules/expert-review.md`):

- [Software Engineer](../.pr/00112/review-by-software-engineer.md) - Rating: 4/5
- [DevOps Engineer](../.pr/00112/review-by-devops-engineer.md) - Rating: 4/5

## Success Criteria Check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Sync workflow uses whitelist approach | ✅ Met | `.github/scripts/transform-to-plugin.sh:66-74` - copies only `.github/prompts/` |
| Whitelist includes `.github/prompts/` | ✅ Met | Explicitly copied in transform script |
| Whitelist excludes `.github/workflows/` | ✅ Met | Removed from copy operation in transform script |
| Whitelist excludes `.github/scripts/` | ✅ Met | Removed from copy operation in transform script |
| Setup scripts use whitelist approach | ✅ Met | `scripts/setup-6-ghc.sh:51-72` - installs only `.github/prompts/` |
| Sync workflow deletes existing directories | ✅ Met | `.github/workflows/sync-to-nabledge.yml:29-41` - cleanup step added |
| Setup scripts remove previously installed files | ✅ Met | `scripts/setup-6-ghc.sh:55-62` - cleanup before installation |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
