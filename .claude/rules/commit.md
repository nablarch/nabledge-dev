# Commit Rules

## Split by Purpose

Each commit must have a single purpose. Never bundle multiple purposes into one commit.

**Examples of correct splitting:**

```
docs: add article rules (.claude/rules/articles.md)
docs: add 3 initial knowledge articles
docs: add review guidelines
```

**Wrong — multiple purposes in one commit:**

```
docs: add knowledge article infrastructure and initial 3 articles  ← NG
```

## Format

```
<type>: <description>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

- First line: max 70 characters
- Describe **why**, not just what
- Always push immediately after commit

## Staging

Never use `git add -A` or `git add .`. Stage files individually by purpose.
