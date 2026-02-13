# PR Template: Without Issue Reference

Use this template when creating a PR that doesn't close a specific issue (e.g., chores, dependency updates, minor fixes).

## Template Structure

```markdown
## Summary
[Describe purpose and content of changes in 1-3 sentences]

## Changes
[List main changes as bullet points]
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Manual testing completed
- [ ] Tests added/updated (if needed)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Usage in Workflows

This template should be used when:
- The PR doesn't address a specific GitHub issue
- The change is minor (chores, dependency updates, documentation)
- No success criteria need to be verified

## Placeholder Replacement

When generating PR body from this template:
- `[Describe purpose...]` → Generated summary description
- `[List main changes...]` → Generated change list

## Example

```markdown
## Summary
Updated project dependencies to latest versions to address security vulnerabilities and improve performance.

## Changes
- Updated npm packages to address 3 security vulnerabilities
- Updated GitHub Actions to latest versions
- Updated TypeScript from 4.9 to 5.0

## Testing
- [x] All tests pass
- [x] Build succeeds
- [x] No breaking changes detected

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Common Use Cases

- Dependency updates (`chore: Update dependencies`)
- Documentation changes (`docs: Update README`)
- CI/CD improvements (`chore: Update GitHub Actions`)
- Minor bug fixes that don't warrant an issue
- Formatting/linting changes (`style: Apply prettier`)
