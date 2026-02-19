# Issue Format

Use user story format with four sections: Situation, Pain, Benefit, Success Criteria.

## Template

**Title:** As a [role], I want [goal] so that [benefit]

**Body:**

### Situation
Current state and observable facts. What exists today?

### Pain
Who is affected and what problem do they face?

### Benefit
Who benefits and how? Use "[who] can [what]" format.

### Success Criteria
- [ ] Verifiable outcomes as checkboxes
- [ ] Each criterion directly relates to stated benefits

## Bug-Specific Success Criteria

For bugs (Critical/High: required, Medium: recommended, Low: optional), add:

```markdown
#### Investigation and Prevention

- [ ] Root cause identified with reproducible test
- [ ] Issue verified as resolved in test environment
- [ ] Workaround documented (if applicable)
- [ ] Horizontal check completed with method, results, and status
- [ ] Recurrence prevention measures implemented
- [ ] Post-mortem created in .pr/xxxxx/
```

## Example

**Title:** As a developer, I want standardized PR formats so that I can review changes efficiently

### Situation
PRs currently use ad-hoc formats with inconsistent context and documentation.

### Pain
Reviewers reconstruct context from commits. Developers lack clear documentation guidance. Quality standards are harder to maintain.

### Benefit
- Reviewers can understand changes without code archaeology
- Developers can follow a clear template
- Maintainers can enforce quality standards

### Success Criteria
- [ ] `.claude/skills/pr/workflows/create.md` includes PR template
- [ ] Template covers Approach, Tasks, Review, Success Criteria
- [ ] New PRs reference issue numbers and verify criteria
