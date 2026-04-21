# Notes

## 2026-03-10

### Commit History Review: v0.4 → v0.5

Reviewed all 15 commits since v0.4 (2026-03-04) against the sync manifest to assess user impact.

Deployed content scope (per `sync-manifest.txt`):
- `.claude/skills/nabledge-6/` — skill content, knowledge files, workflows
- `.claude/marketplace/` — marketplace metadata
- `.claude/commands/n6.md`
- `.github/prompts/n6.prompt.md`
- `tools/setup/setup-6-cc.sh`, `tools/setup/setup-6-ghc.sh`

---

#### User Impact: YES

| Commit | Title | Deployed Files Changed | Impact |
|--------|-------|----------------------|--------|
| `fe8acd3` | Improved search workflow performance (#101) | `.claude/skills/nabledge-6/SKILL.md`, knowledge files (new files added) | New search architecture deployed; knowledge files added for broader coverage |
| `e08c04c` | Address ca-004 token anomaly and ks-003 detection gap (#125) | `.claude/skills/nabledge-6/knowledge/.../handlers-data_read_handler.json` | Fixes two bugs: token spike in code analysis, `createReader` not detected |
| `166cfc5` | Regenerate all nabledge-6 knowledge files (#120) | `.claude/skills/nabledge-6/knowledge/` (full set) | All knowledge files regenerated in new format; expands coverage across entire Nablarch 6 doc set |
| `a346b98` | Move setup scripts to tools/setup (#139) | `tools/setup/setup-6-cc.sh`, `tools/setup/setup-6-ghc.sh` (path change only) | Scripts moved to path expected by sync manifest; content unchanged, no functional change for users |

---

#### User Impact: NO (dev-only)

| Commit | Title | Reason |
|--------|-------|--------|
| `21dce7f` | Manifest-driven sync workflow (#147) | `.github/` CI/CD infra only; no plugin content |
| `6becacf` | nabledge-test baseline workflow (#129) | `.claude/skills/nabledge-test/` — different skill, not in manifest |
| `50c382e` | Restructure knowledge-creator directory (#141) | `tools/knowledge-creator/` dev tool only |
| `b7b4c0f` | Rename doc/ to docs/ (#140) | `CLAUDE.md`, `README.md` dev repo files only |
| `072897d` | Support all RST files with no_knowledge_content flag (#134) | `tools/knowledge-creator/` dev tool only |
| `f1e33bb` | Prevent stray directories from knowledge-creator agent (#133) | `tools/knowledge-creator/` dev tool only |
| `a09faf7` | Improve execution logs with run_id and reports (#118) | `tools/knowledge-creator/` dev tool only |
| `4822147` | Track source doc commit versions (#119) | `tools/knowledge-creator/` dev tool only |
| `e85ea6b` | Draft tobe vision (#90) | `README.md` dev doc only |
| `ec366aa` | Build nabledge-creator tool (#106) | `tools/knowledge-creator/` dev tool only |
| `919d658` | Update CHANGELOG references (#117) | CHANGELOG admin; content already captured in [Unreleased] |

---

### Assessment Summary

CHANGELOG [Unreleased] accurately reflects the 3 meaningful user-facing changes:

1. **知識検索アーキテクチャの刷新** — `fe8acd3` (search architecture overhaul)
2. **バグ修正 x2** — `e08c04c` (token anomaly + detection gap)
3. **知識ファイル全量再生成** — `166cfc5` (regenerated in new format)

The setup script path change (`a346b98`) is infrastructure-level and requires no CHANGELOG entry.

Pending user confirmation before proceeding with file updates.

---

### Comparison with v0.4 Release PR (#115)

Verified that PR #156 covers all required release files by comparing against PR #115.

**Core release files (4 files):**

| File | PR #115 (v0.4) | PR #156 (v0.5) | Status |
|------|----------------|----------------|--------|
| `.claude/skills/nabledge-6/plugin/CHANGELOG.md` | ✅ | ✅ | No missing |
| `.claude/skills/nabledge-6/plugin/plugin.json` | ✅ | ✅ | No missing |
| `.claude/marketplace/.claude-plugin/marketplace.json` | ✅ | ✅ | No missing |
| `.claude/marketplace/CHANGELOG.md` | ✅ | ✅ | No missing |

**Extra files in PR #115 not in PR #156:**

| File | Reason not needed |
|------|-------------------|
| `.claude/rules/changelog.md` | Rule file improvement bundled in same PR; not release-specific |
| `.claude/rules/expert-review.md` | Rule file improvement bundled in same PR; not release-specific |
| `.claude/skills/pr/workflows/create.md` | Workflow improvement bundled in same PR; not release-specific |
| `.pr/00114/changes.diff` | Old work log format; replaced by `notes.md` convention |
| `.pr/00114/review-by-*.md` | Expert reviews; not conducted for this PR (release prep only) |

**Conclusion: No missing changes.** All 4 core versioning files are updated. Differences are non-release files incidentally bundled in #115.
