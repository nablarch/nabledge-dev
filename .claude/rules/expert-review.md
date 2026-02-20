# Expert Review

AI-driven expert review process for quality assurance before PR creation.

## When to Execute

Execute expert review in `/hi` command after testing (step 7) and before PR creation (step 8).

## Process

### 1. Analyze Changes and Select Experts

Analyze changed files to determine artifact types and select appropriate experts:

| Artifact Type | Expert Role | Review Focus |
|---------------|-------------|--------------|
| Source code (*.py, *.js, *.java, etc.) | Software Engineer | Architecture, code quality, best practices, maintainability |
| Prompts/workflows (.claude/*, *.md in workflows/) | Prompt Engineer | Clarity, completeness, agent behavior, example quality |
| Documentation (*.md, docs/) | Technical Writer | Structure, clarity, accuracy, consistency |
| Tests (*test*.*, *spec*.*) | QA Engineer | Coverage, edge cases, test design, assertions |
| Configuration (*.json, *.yaml, *.toml) | DevOps Engineer | Security, validation, environment compatibility |

**Expert Selection Logic:**
- Analyze all changed files in current branch vs base branch
- Group by artifact type
- Select 1-3 most relevant experts (avoid over-reviewing)
- If multiple types, prioritize by impact (source code > tests > docs)

### 2. Execute Expert Review

For each selected expert, launch Task agent with expert persona:

```
Task
  subagent_type: "general-purpose"
  description: "Expert review as {Expert Role}"
  prompt: "You are a {Expert Role} reviewing changes for quality assurance.

## Changes to Review
{List of changed files with diffs}

## Review Guidelines
{Expert-specific review guidelines from this document}

## Your Task
1. Review the changes thoroughly
2. Provide ratings (1-5 scale) for key aspects
3. List specific issues found (High/Medium/Low priority)
4. Suggest concrete improvements for High/Medium issues
5. Highlight positive aspects

## Output Format
Use markdown with sections:
- Overall Assessment (1-5 rating + summary)
- Key Issues (priority, description, suggestion)
- Positive Aspects
- Recommendations
"
```

### 3. Developer Agent Evaluates Improvements

Launch another Task agent as developer to evaluate improvement suggestions:

```
Task
  subagent_type: "general-purpose"
  description: "Evaluate improvement suggestions"
  prompt: "You are the developer who implemented these changes. Review the expert's improvement suggestions and decide which to implement.

## Expert Review
{Expert review output}

## Your Task
For each High/Medium priority issue:
1. Evaluate if the suggestion is valid and beneficial
2. Decide: Implement Now / Defer to Future / Reject
3. Provide reasoning for your decision

## Output Format
| Issue | Priority | Decision | Reasoning |
|-------|----------|----------|-----------|
| ... | ... | ... | ... |
"
```

### 4. Implement Approved Improvements

For issues marked "Implement Now":
- Use Edit/Write tools to apply improvements
- Run tests again to verify changes
- Document what was changed and why

### 5. Save Review Results

Save to `.pr/{pr_number}/review-by-{expert_role}.md`:

```markdown
# Expert Review: {Expert Role}

**Date**: {YYYY-MM-DD}
**Reviewer**: AI Agent as {Expert Role}
**Files Reviewed**: {count} files

## Overall Assessment

**Rating**: {1-5}/5
**Summary**: {1-2 sentence overall impression}

## Key Issues

### High Priority
1. **{Issue title}**
   - Description: {What's wrong}
   - Suggestion: {How to fix}
   - Decision: {Implement Now / Defer / Reject}
   - Reasoning: {Why this decision}

### Medium Priority
{Same format}

### Low Priority
{Same format}

## Positive Aspects

- {Strength 1}
- {Strength 2}

## Recommendations

{Future improvements or considerations}

## Files Reviewed

- {file1} ({artifact type})
- {file2} ({artifact type})
```

### 6. Update PR Template

Modify PR template's Expert Review section to link to detailed reviews:

```markdown
## Expert Review

{For each expert}
- [{Expert Role}](../.pr/{pr_number}/review-by-{expert_role}.md) - Rating: {X}/5
```

## Expert-Specific Guidelines

### Software Engineer

**Review Focus:**
- Architecture: Design patterns, separation of concerns, modularity
- Code Quality: Readability, naming, complexity, duplication
- Best Practices: Language idioms, framework conventions, error handling
- Maintainability: Documentation, testability, extensibility

**Rating Criteria:**
- 5: Excellent - Best practices followed, well-structured, maintainable
- 4: Good - Minor improvements possible, generally solid
- 3: Acceptable - Works but has issues to address
- 2: Needs Work - Significant issues affecting quality
- 1: Poor - Major architectural or quality problems

### Prompt Engineer

**Review Focus:**
- Clarity: Instructions are clear and unambiguous
- Completeness: All necessary context and steps provided
- Agent Behavior: Prompts guide agent to correct actions
- Examples: High-quality examples that illustrate concepts

**Rating Criteria:**
- 5: Excellent - Clear, complete, well-structured prompts
- 4: Good - Minor clarity improvements possible
- 3: Acceptable - Works but could be clearer
- 2: Needs Work - Ambiguous or incomplete instructions
- 1: Poor - Confusing or missing critical information

### Technical Writer

**Review Focus:**
- Structure: Logical organization, proper heading hierarchy
- Clarity: Easy to understand, jargon explained
- Accuracy: Information is correct and up-to-date
- Consistency: Terminology, formatting, style consistent

**Rating Criteria:**
- 5: Excellent - Clear, accurate, well-organized documentation
- 4: Good - Minor clarifications needed
- 3: Acceptable - Understandable but could be improved
- 2: Needs Work - Confusing or inconsistent
- 1: Poor - Inaccurate or poorly structured

### QA Engineer

**Review Focus:**
- Coverage: Tests cover main paths and edge cases
- Edge Cases: Boundary conditions, error cases tested
- Test Design: Well-structured, maintainable tests
- Assertions: Clear, specific, meaningful assertions

**Rating Criteria:**
- 5: Excellent - Comprehensive coverage, well-designed tests
- 4: Good - Good coverage, minor gaps
- 3: Acceptable - Basic coverage, some edge cases missing
- 2: Needs Work - Significant gaps in coverage
- 1: Poor - Minimal or ineffective tests

### DevOps Engineer

**Review Focus:**
- Security: No secrets exposed, secure configurations
- Validation: Input validation, error handling
- Environment: Works across different environments
- Dependencies: Version compatibility, security updates

**Rating Criteria:**
- 5: Excellent - Secure, validated, environment-aware
- 4: Good - Minor security/validation improvements
- 3: Acceptable - Works but has potential issues
- 2: Needs Work - Security or compatibility concerns
- 1: Poor - Critical security or compatibility issues

## Integration with /hi Command

Expert review is step 8 in the `/hi` workflow:

1. Get or create issue
2. Sync branch with main
3. Fetch issue details
4. Create branch
5. Analyze requirements
6. Implement changes
7. Run tests
8. **Execute expert review** ← Added here
9. Create PR (with review links in Expert Review section)
10. Request review from user

## Notes

- Expert reviews are AI-generated, not human reviews
- Focus on automated quality assurance before PR creation
- Developer agent makes final decisions on improvements
- Reviews are saved for future reference and learning
- PR templates link to detailed reviews instead of inline tables
