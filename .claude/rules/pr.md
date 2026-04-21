# PR Format

## Creation

Always use `Skill(skill: "pr", args: "create")` to create PRs. Never use `gh pr create` directly.

## Template

PRs follow the standard template from `.claude/skills/pr/templates/pr-template.md`:

```markdown
Closes #{issue_number}

## Approach
[Why this approach was chosen, alternatives considered, trade-offs made]

## Tasks

See [tasks.md](.work/{00000}/tasks.md).

## Expert Review

AI-driven expert reviews conducted before PR creation (see `.claude/rules/expert-review.md`):

- [Expert Role](https://github.com/{owner}/{repo}/blob/{branch}/.work/{00000}/review-by-{expert-role}.md) - Rating: X/5

## Success Criteria Check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Criterion from issue | ✅ Met / ❌ Not Met | File path or description |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Title Format

`<type>: <description> (#{issue_number})`

- Max 70 characters
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- Issue number appended automatically from branch name

## Labels

Apply labels matching the issue (see `.claude/rules/issues.md` for label definitions).

## Expert Review Requirement

Expert review (`.claude/rules/expert-review.md`) must be completed before PR creation.
Save results to `.work/{00000}/review-by-{expert-role}.md` and link from PR body.

## Markdown in gh CLI Commands

Use single-quoted heredoc to avoid backtick escaping issues (see `.claude/rules/issues.md`).
