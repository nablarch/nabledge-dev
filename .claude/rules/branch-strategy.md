# Branch Strategy

This document defines the branch strategy for the repository. All AI agents and developers MUST follow these rules.

## Branch Structure

### Main Branches

| Branch | Purpose | Protection | Merge From |
|--------|---------|------------|------------|
| `main` | **Production/Release** - Reflects production state | Protected, requires PR | `develop` only |
| `develop` | **Integration** - Active development integration | Protected, requires PR | Feature branches |

### Working Branches

| Pattern | Purpose | Base Branch | Merge To |
|---------|---------|-------------|----------|
| `issue-<number>` | Feature/bug fix work | `develop` | `develop` |

## Branch Flow

```
develop (default branch for development)
  ├── issue-42 (feature work)
  ├── issue-123 (bug fix)
  └── issue-456 (refactoring)
       └── merge back to develop via PR

main (release branch)
  └── receives merges from develop when ready to release
```

## Rules for AI Agents

### When Creating Branches

**ALWAYS branch from `develop`**, never from `main`.

```bash
# Correct
git checkout develop
git pull origin develop
git checkout -b issue-42

# Wrong
git checkout main  # Never use main as base
```

### When Creating PRs

**ALWAYS target `develop`** as the base branch, never `main`.

```bash
# Correct
gh pr create --base develop --head issue-42

# Wrong
gh pr create --base main --head issue-42  # Never target main directly
```

### When Creating Worktrees

**ALWAYS create worktrees from `develop`**.

```bash
# Correct
git worktree add -b issue-42 ../issue-42 develop

# Wrong
git worktree add -b issue-42 ../issue-42 main  # Never use main
```

## Release Process

### Development Cycle

1. Developer creates issue in GitHub
2. Create branch from `develop`: `issue-<number>`
3. Implement changes
4. Create PR to `develop`
5. Review and merge to `develop`

### Release Cycle

1. When `develop` is stable and ready for release
2. Create PR from `develop` to `main`
3. Review and test thoroughly
4. Merge to `main`
5. Tag release on `main`

## Default Branch Configuration

The repository's default branch SHOULD be set to `develop` in GitHub settings. This ensures:
- PRs default to `develop`
- New clones checkout `develop` by default
- Branch creation workflows use correct base

## Exception Handling

### Hotfixes (Emergency Production Fixes)

For critical production issues that cannot wait for the normal development cycle:

1. Create branch from `main`: `hotfix-<description>`
2. Fix the issue
3. Create PR to `main`
4. After merging to `main`, also merge to `develop` to keep branches in sync

```bash
git checkout main
git pull origin main
git checkout -b hotfix-critical-bug
# Fix the issue
gh pr create --base main --head hotfix-critical-bug
# After merge:
git checkout develop
git merge main
```

### Repository Migration

If migrating from a `main`-only workflow:
1. Create `develop` branch from `main`
2. Set `develop` as default branch in GitHub
3. Update all workflows
4. Communicate change to team

## Verification Commands

### Check Current Base Branch

```bash
# Get the repository's default branch
gh repo view --json defaultBranchRef -q .defaultBranchRef.name
# Should return: develop
```

### Verify Branch Base

```bash
# Check what branch your current branch is based on
git merge-base --fork-point develop
git merge-base --fork-point main
```

The first command should succeed, the second should fail (or return older commit) for working branches.

## AI Agent Implementation

When implementing workflows that create branches or PRs:

1. **Never hardcode branch names** - Always get default branch dynamically
2. **For development work** - Use `develop` as base
3. **Validate branch strategy** - Check that base branch is `develop` before proceeding
4. **Display clear messages** - Tell user which branch is being used

Example:
```bash
# Dynamic branch detection
default_branch=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
echo "Repository default branch: ${default_branch}"

# For development workflows, enforce develop
if [[ "$default_branch" != "develop" ]]; then
  echo "WARNING: Default branch is ${default_branch}, but development should use 'develop'"
  echo "Using 'develop' as base branch..."
  base_branch="develop"
else
  base_branch="$default_branch"
fi
```

## Summary

| Operation | Base Branch | Target Branch | Command |
|-----------|-------------|---------------|---------|
| Create issue branch | `develop` | N/A | `git checkout -b issue-N develop` |
| Create issue PR | N/A | `develop` | `gh pr create --base develop` |
| Create worktree | `develop` | N/A | `git worktree add -b issue-N path develop` |
| Release PR | N/A | `main` | `gh pr create --base main --head develop` |
| Hotfix branch | `main` | N/A | `git checkout -b hotfix-X main` |
| Hotfix PR | N/A | `main` then `develop` | Two PRs required |

This strategy ensures clean separation between development and production, while maintaining clear integration points.
