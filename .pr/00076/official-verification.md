# Official Verification: Git Fetch Behavior

**Date**: 2026-02-20
**Issue**: User pointed out we didn't verify against official Git documentation
**Result**: Implementation is correct; expert review suggestion was incorrect

## Investigation

### Git Official Documentation (git-scm.com)

**From `git fetch` documentation:**

> When no refspec is provided, `git fetch origin` uses the configured `remote.origin.fetch` refspec as a mapping.
> When explicit refspecs are provided (`git fetch origin main`), the command-line refspec determines what's fetched, and the configured `remote.origin.fetch` acts as a **mapping** for where to store the fetched refs.

**Key insight**: `git fetch origin main` relies on `remote.origin.fetch` configuration to determine where to store the tracking branch.

### Actual Repository Configuration

**Checked**: `/home/tie303177/work/nabledge/.bare/config`

```ini
[core]
    repositoryformatversion = 0
    filemode = true
    bare = true
[remote "origin"]
    url = https://github.com/nablarch/nabledge-dev.git
    # NO fetch refspec configured!
```

**Expected configuration** (normal repository):
```ini
[remote "origin"]
    url = https://github.com/...
    fetch = +refs/heads/*:refs/remotes/origin/*
```

**Finding**: This worktree environment uses a bare repository without `remote.origin.fetch` refspec configured.

## Root Cause

1. **Environment**: Worktrees created from bare repository (`.bare/`)
2. **Configuration**: `remote.origin.fetch` refspec not configured in bare repository
3. **Behavior**: Without fetch refspec, `git fetch origin main` does not update `refs/remotes/origin/main`
4. **Solution**: Explicit refspec `main:refs/remotes/origin/main` bypasses configuration and directly specifies destination

## Expert Review Re-evaluation

### Original Review Suggestion (Medium Priority)

**Prompt Engineer suggested**:
- Remove "(bare repositories)" from note
- Reason: "Worktrees and bare repositories are distinct concepts"

### Verdict: **Incorrect**

**Reality**:
- This worktree environment **IS** based on a bare repository
- The issue affects "worktree environments (bare repositories)" specifically
- The terminology was accurate

### Corrected Documentation

**Updated note**:
```markdown
**Note**: The explicit refspec `main:refs/remotes/origin/main` ensures that the tracking branch `origin/main` is updated in worktree environments (bare repositories). In bare repository configurations, `remote.origin.fetch` refspec is typically not configured, so `git fetch origin main` will not update the tracking reference without the explicit destination, leaving `origin/main` at an old commit position.
```

**Changes**:
- ✅ Restored "(bare repositories)" terminology
- ✅ Added explanation of WHY: bare repos lack fetch refspec configuration
- ✅ Connected to Git official documentation behavior

## Lessons Learned

1. **Always verify against official documentation** before implementing fixes
2. **Investigate actual environment configuration** to understand root cause
3. **Expert reviews can be wrong** - validate suggestions against facts
4. **Terminology precision matters** - "worktree environments (bare repositories)" accurately describes the scenario

## References

- Git fetch documentation: https://git-scm.com/docs/git-fetch
- Git worktree documentation: https://git-scm.com/docs/git-worktree
- Repository config: `/home/tie303177/work/nabledge/.bare/config`
