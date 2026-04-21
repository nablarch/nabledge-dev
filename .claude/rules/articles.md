# Article Creation

Workflow for creating knowledge-sharing articles from nabledge development insights.

## Directory Structure

```
docs/articles/
├── 01-{slug}.md                   # Article 1
├── 02-{slug}.md                   # Article 2
└── ...

.claude/rules/
└── article-review.md              # General review criteria

.work/{issue_number}/
└── review-prompt-{series}.md      # Series-specific facts and check items (work log)
```

## Workflow

### Step 1: Story Proposal

Interview the user and create a story outline in the work log.

**Interview questions:**
- What topic/insight do you want to share?
- Who is the target reader?
- What is the main "困りごと" (pain point) the reader will relate to?
- What is the key takeaway?
- Are there concrete numbers, links, or examples to include?

**Output to `.work/{issue_number}/notes.md`:**

```markdown
## Story: {Article Title}

### Target reader
{Who and what they already know}

### Story arc
- **Entry**: {Reader's relatable pain point}
- **Approach**: {What you did}
- **Know-how**: {Key insights to share}
- **Closing**: {Honest reflection + call to action}

### Key facts
- {Concrete numbers, links}

### Series position (if applicable)
- Previous: {title + summary}
- Next: {title + summary}
```

Propose to user and wait for approval before proceeding.

### Step 2: Article Creation

After story approval, create the article in `docs/articles/{NN}-{slug}.md`.

Follow series-specific rules in `.work/{issue_number}/review-prompt-{series}.md` if applicable.
Open a PR for story review before writing the full article when the story is complex.

### Step 3: Self-Check

After article creation, review against `.claude/rules/article-review.md`.

Also apply series-specific check items from `.work/{issue_number}/review-prompt-{series}.md`.

**Output to `.work/{issue_number}/notes.md`:**

```markdown
## Self-Check: {Article Title}

### 1. Facts
{Findings or "問題なし"}

### 2. Style violations
{Findings or "問題なし"}

### 3. Structure / readability
{Findings or "問題なし"}

### 4. Navigation
{Findings or "問題なし"}

### 5. Verbosity / gaps
{Findings or "問題なし"}

### 6. Series consistency (if applicable)
{Findings or "問題なし"}

### Proposed improvements
| # | Priority | Issue | Proposed fix |
|---|----------|-------|--------------|
| 1 | 🔴/🟡/🟢 | {description} | {fix} |
```

Apply approved improvements to the article.

### Step 4: Expert Review

Launch expert review using `.claude/rules/expert-review.md`.

Select **Technical Writer** as the primary expert for article content.

Save result to `.work/{issue_number}/review-by-technical-writer.md`.

### Step 5: PR Review Request

After all checks complete, create PR using `Skill(skill: "pr", args: "create")`.

PR body should include:
- Summary of articles created
- Self-check results summary
- Expert Review section with links to detailed review files
- Links to the articles

## Review Guidelines

General review criteria: `.claude/rules/article-review.md`

Series-specific facts and style notes: `.work/{issue_number}/review-prompt-{series}.md` (work log)

The general review guidelines are maintained in `.claude/rules/` and should be updated when review standards evolve. Series-specific prompts live in the PR work log as they are tied to a specific article creation task.
