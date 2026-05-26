# Diff Check: PR #353 (Issue #352)

**Date**: 2026-05-26
**Branch**: 352-release-nabledge vs main

## Changed Files

| File | Category | Expected? |
|------|----------|-----------|
| `.claude/marketplace/.claude-plugin/marketplace.json` | Task 6: marketplace version bump | ✅ Yes |
| `.claude/marketplace/CHANGELOG.md` | Task 6: marketplace CHANGELOG row | ✅ Yes |
| `.claude/rules/release.md` | Rule improvement (changelog writing guideline) | ✅ Yes |
| `.claude/skills/nabledge-1.2/plugin/CHANGELOG.md` | Task 4: CHANGELOG update | ✅ Yes |
| `.claude/skills/nabledge-1.2/plugin/plugin.json` | Task 5: version bump | ✅ Yes |
| `.claude/skills/nabledge-1.3/plugin/CHANGELOG.md` | Task 4: CHANGELOG update | ✅ Yes |
| `.claude/skills/nabledge-1.3/plugin/plugin.json` | Task 5: version bump | ✅ Yes |
| `.claude/skills/nabledge-1.4/plugin/CHANGELOG.md` | Task 4: CHANGELOG update | ✅ Yes |
| `.claude/skills/nabledge-1.4/plugin/plugin.json` | Task 5: version bump | ✅ Yes |
| `.claude/skills/nabledge-5/plugin/CHANGELOG.md` | Task 4: CHANGELOG update | ✅ Yes |
| `.claude/skills/nabledge-5/plugin/plugin.json` | Task 5: version bump | ✅ Yes |
| `.claude/skills/nabledge-6/plugin/CHANGELOG.md` | Task 4: CHANGELOG update | ✅ Yes |
| `.claude/skills/nabledge-6/plugin/plugin.json` | Task 5: version bump | ✅ Yes |
| `.work/00352/notes.md` | Work log | ✅ Yes |
| `.work/00352/tasks.md` | Task list | ✅ Yes |

## Issue Found and Fixed

`nabledge-6/plugin/CHANGELOG.md` had a duplicate `[0.7]` tag link:

```
# Before (buggy)
[0.7]: https://github.com/nablarch/nabledge/releases/tag/0.7   ← original line remained
[0.8]: https://github.com/nablarch/nabledge/releases/tag/0.9
[0.7]: https://github.com/nablarch/nabledge/releases/tag/0.8   ← duplicate, incorrect
```

```
# After (fixed)
[0.8]: https://github.com/nablarch/nabledge/releases/tag/0.9
[0.7]: https://github.com/nablarch/nabledge/releases/tag/0.7
```

Rule: each version heading links to the marketplace tag where that plugin version was **first** included.
- nabledge-6 v0.7 was first included in marketplace 0.7 → `[0.7]: .../tag/0.7` ✅
- nabledge-6 v0.8 is being released in marketplace 0.9 → `[0.8]: .../tag/0.9` ✅

## Version Verification

| Plugin | Previous | New | Marketplace |
|--------|----------|-----|-------------|
| nabledge-6 | 0.7 | 0.8 | 0.9 |
| nabledge-5 | 0.2 | 0.3 | 0.9 |
| nabledge-1.4 | 0.1 | 0.2 | 0.9 |
| nabledge-1.3 | 0.1 | 0.2 | 0.9 |
| nabledge-1.2 | 0.1 | 0.2 | 0.9 |

## Conclusion

All changes are within expected scope (Task 4〜6). One bug fixed (duplicate tag link in nabledge-6 CHANGELOG).
No unexpected files changed.
