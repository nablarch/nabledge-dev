# Expert Review: Technical Writer

**Date**: 2026-08-07
**Reviewer**: AI Agent as Technical Writer
**Files Reviewed**: 1 file

## Summary

0 Findings

## Findings

None. All aspects of the added インストール section are technically accurate, structurally sound, and consistent with the codebase.

## Observations

1. **"プロジェクトルートで" instruction is slightly conservative but not wrong.** The setup scripts auto-detect the project root via `git rev-parse --show-toplevel`, so the command works from any directory within the git repo, not only from the root. Telling users to run from the project root is a safe simplification — it will never cause failure — but a user who happens to run it from a subdirectory will get identical results. Non-blocking.

2. **No prerequisites note.** The scripts require `jq`. The review brief explicitly marks prerequisites as out-of-scope for this PR, so this is recorded only for awareness. If a future PR adds a prerequisites section, `jq` and `git` should both be listed.

3. **Example version in code blocks defaults to `6`.** The commands show `-v 6` as the example value. This is a reasonable default (latest Nablarch version), but users of older versions must substitute manually. An inline comment could reduce friction. Non-blocking.

## Positive Aspects

- **Accuracy**: All command URLs correctly resolve to where the sync manifest deploys the scripts (`nablarch/nabledge` repo root). The `-v` value list (`6 5 1.4 1.3 1.2`) exactly matches `ALL_VERSIONS` in both setup scripts.
- **Completeness**: Both supported agent types (Claude Code and GitHub Copilot) have dedicated commands. Multi-version and all-version install syntax is documented.
- **Clarity**: The explanation of `-v` values is anchored directly to the plugin table above ("上記表の `nabledge-` に続く値"), eliminating any guesswork about what values are valid.
- **Navigation**: The closing sentence points readers to per-plugin guide links already present in the table, avoiding redundant content and keeping the section concise.
- **Structure**: The new `## インストール` section fits logically between `## プラグイン` and `## 変更履歴`, matching the natural user journey: discover → install → track changes.

## Files Reviewed

- `.claude/marketplace/README.md` (documentation)
