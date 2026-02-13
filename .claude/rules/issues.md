# Issue Format

All issues should follow a consistent structure that clearly articulates the problem, who is affected, and what success looks like.

## Title Format

Use the user story format:

```
As a [role], I want [goal] so that [benefit]
```

**Examples:**
- As a developer, I want standardized issue formats so that I can create consistent documentation
- As a user, I want keyboard shortcuts so that I can navigate more efficiently
- As a maintainer, I want automated tests so that I can catch regressions early

## Body Format

Issues should include four sections:

### 1. Situation

Concrete facts and observed circumstances. What is the current state?

- Describe what exists today
- Include relevant technical details
- State observable facts, not opinions
- Reference specific files, systems, or behaviors

### 2. Pain

Who is affected and what problem do they face?

- Identify the affected stakeholders (developers, users, maintainers, etc.)
- Describe the specific problem or friction they experience
- Explain why the current situation is problematic
- Include impact or severity if relevant

### 3. Benefit

Who benefits and how? Use the form "[who] can [what]".

- State clear benefits for each stakeholder
- Use active voice with "can" statements
- Be specific about capabilities gained
- Avoid vague improvements like "better" or "easier"

**Examples:**
- Developers can create branches with consistent naming
- Users can understand feature status at a glance
- Maintainers can onboard new contributors faster

### 4. Success Criteria

Checkboxes that verify benefit achievement. Each criterion should be:

- Measurable or verifiable
- Directly related to stated benefits
- Written as observable outcomes
- Formatted as GitHub checkboxes `- [ ]`

**Example:**
```markdown
- [ ] `.claude/rules/issues.md` exists and documents the format
- [ ] New issues follow the Situation/Pain/Benefit/Success Criteria structure
- [ ] Success criteria are written as verifiable checkboxes
```

## Complete Example

```markdown
**Title:** As a developer, I want standardized PR formats so that I can review changes efficiently

**Body:**

### Situation

Currently, PRs are created with an ad-hoc format. Some include detailed context, others provide minimal information. There is no standard structure for documenting the approach, testing, or linking to related issues.

### Pain

Reviewers waste time reconstructing context from commit messages and code changes. Developers don't know what information to include in PR descriptions. The lack of consistency makes it harder to maintain quality standards across the project.

### Benefit

- Reviewers can understand changes quickly without extensive code archaeology
- Developers can follow a clear template for documenting their work
- Maintainers can enforce quality standards through structured PR requirements

### Success Criteria

- [ ] `.claude/skills/pr/workflows/create.md` includes comprehensive PR template
- [ ] Template includes sections for Approach, Tasks, Expert Review, and Success Criteria
- [ ] All new PRs reference the related issue number
- [ ] PRs include verification of issue success criteria
```

## Usage Guidelines

When creating issues:

1. **Start with the title** - Frame it as a user story
2. **Describe the situation** - State facts about current state
3. **Identify the pain** - Who hurts and why
4. **Articulate benefits** - Use "[who] can [what]" format
5. **Define success criteria** - Write verifiable checkboxes
6. **Review for clarity** - Ensure someone unfamiliar with the context can understand

## Rationale

This format ensures:

- **Shared understanding** - Everyone knows why work matters
- **Clear scope** - Success criteria prevent scope creep
- **Stakeholder focus** - Benefits are explicit and measurable
- **Verification** - Checkboxes provide clear completion signal
- **Traceability** - Format supports issue-driven development workflow
