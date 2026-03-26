# Article Creation

Workflow for creating knowledge-sharing articles from nabledge development insights.

## Directory Structure

```
docs/articles/
├── review-guidelines.md           # General review criteria (maintained separately)
├── review-prompt-{series}.md      # Series-specific facts and check items
├── 01-{slug}.md                   # Article 1
├── 02-{slug}.md                   # Article 2
└── ...
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

**Output to `.pr/{issue_number}/notes.md`:**

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

Follow series-specific rules in `review-prompt-{series}.md` if applicable.
Open a PR for story review before writing the full article when the story is complex.

### Step 3: Self-Check

After article creation, review against `docs/articles/review-guidelines.md`.

Also apply series-specific check items from `review-prompt-{series}.md`.

**Output to `.pr/{issue_number}/notes.md`:**

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

Save result to `.pr/{issue_number}/review-by-technical-writer.md`.

### Step 5: PR Review Request

After all checks complete, create PR using `Skill(skill: "pr", args: "create")`.

PR body should include:
- Summary of articles created
- Self-check results summary
- Expert Review section with links to detailed review files
- Links to the articles

## Review Guidelines

General review criteria: `docs/articles/review-guidelines.md`

Series-specific facts and style notes: `docs/articles/review-prompt-{series}.md`

Both files are maintained separately and should be updated when review standards evolve.
