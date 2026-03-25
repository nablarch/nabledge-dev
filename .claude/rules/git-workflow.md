# Git Workflow

## Branch Strategy

`work1`〜`work4` are base branches for each worktree. Never commit directly to these branches.

**Always create a feature branch before starting work:**

```bash
git checkout -b {issue-number}-{description}
# e.g., git checkout -b 234-fix-typo
```

Then commit and create PR from the feature branch.
