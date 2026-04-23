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

## Project Quality Standard

Nabledge provides knowledge about Nablarch, a mission-critical enterprise framework used in
large-scale financial systems. The same quality standard applies here.

- If there is even a 1% risk, eliminate it — do not accept it
- "Good enough" does not exist; quality is binary: correct or not correct
- verify is the quality gate for RBKC output — never weaken it to make output pass
- 100% content coverage is the target; missing content is a bug to fix, not a reason to lower thresholds

## Changes to Review
{List of changed files with diffs}

## Non-Negotiable Constraints
{List constraints that must not be compromised — e.g., existing design decisions, project invariants.
Example: 'verify must catch all content gaps — skipping unresolvable references is not acceptable'}

## Review Guidelines
{Expert-specific review guidelines from this document}

## Your Task

Under ゼロトレランス, quality is binary. Do not emit a 3-tier severity (High/Medium/Low) —
that invites triage and deferral. Emit only two categories:

- **Finding** — violates the spec, a project rule, or the ゼロトレランス standard.
  Every Finding MUST quote the specific spec clause / rule line / standard clause it violates.
  If you cannot quote one, it is not a Finding — downgrade it to an Observation.
  Findings are non-negotiable fix items.
- **Observation** — a note that does NOT violate any spec / rule / standard clause
  (e.g. cosmetic wording, optional diagnostic enrichment, future refactor idea).
  Observations are recorded for context only; the developer is not required to act.

Steps:
1. Review the changes thoroughly against the spec, project rules, and ゼロトレランス standard.
2. List every Finding with the quoted clause it violates and a concrete fix.
3. List Observations separately (no fix required).
4. Highlight positive aspects.
5. Do not use High/Medium/Low. Do not emit a numeric rating — under binary quality,
   the only meaningful result is "zero Findings" or "N Findings remaining".

## Output Format
Use markdown with sections:
- Summary (one line: "0 Findings" or "N Findings — not shippable")
- Findings (each: violated clause quoted, description, fix)
- Observations (non-blocking notes)
- Positive Aspects
"
```

### 3. Developer Agent Evaluates Findings

Findings are non-negotiable — all must be fixed before proceeding.
The developer agent's role is to plan the fix, not to triage severity.

```
Task
  subagent_type: "general-purpose"
  description: "Plan fixes for review Findings"
  prompt: "You are the developer who implemented these changes. The expert review produced Findings (all must be fixed under ゼロトレランス) and Observations (non-blocking).

## Expert Review
{Expert review output}

## Your Task
For each Finding, describe the fix you will apply. You cannot defer or reject a Finding —
if you believe a Finding is invalid, you must quote the spec clause that sanctions the
current behaviour, which would prove the reviewer's quoted clause was misapplied.

For Observations, note whether you will address them (optional) or skip them (default).

## Output Format
### Findings (all must be fixed)
| # | Violated clause | Fix plan |
|---|-----------------|----------|

### Observations (optional)
| # | Note | Action |
|---|------|--------|
"
```

### 4. Implement Approved Improvements

For issues marked "Implement Now":
- Use Edit/Write tools to apply improvements
- Run tests again to verify changes
- Document what was changed and why

### 5. Save Review Results

Save to `.work/{issue_number_5digit}/review-by-{expert_role}.md`:

```markdown
# Expert Review: {Expert Role}

**Date**: {YYYY-MM-DD}
**Reviewer**: AI Agent as {Expert Role}
**Files Reviewed**: {count} files

## Summary

{one line: "0 Findings" or "N Findings — not shippable"}

## Findings

Each Finding MUST quote the specific spec / rule / standard clause it violates.
All Findings are non-negotiable fix items under ゼロトレランス.

1. **{Finding title}**
   - Violated clause: {quoted clause from spec / rule / standard}
   - Description: {what is wrong}
   - Fix: {how to address it}

## Observations

Non-blocking notes that do not violate any clause.

- {note} — {optional context}

## Positive Aspects

- {Strength 1}
- {Strength 2}

## Files Reviewed

- {file1} ({artifact type})
- {file2} ({artifact type})
```

### 6. Update PR Template

Modify PR template's Expert Review section to link to detailed reviews using absolute GitHub URLs:

**URL Format**:
```
https://github.com/{owner}/{repo}/blob/{current_branch}/.work/{issue_number_5digit}/review-by-{expert_role}.md
```

Where:
- `{owner}/{repo}`: From `gh repo view --json nameWithOwner -q .nameWithOwner`
- `{current_branch}`: Current branch name
- `{issue_number_5digit}`: Issue number, 5-digit zero-padded (e.g., "00042")
- `{expert_role}`: Expert role in lowercase with hyphens

Example:
```markdown
## Expert Review

{For each expert}
- [{Expert Role}](https://github.com/nablarch/nabledge-dev/blob/42-add-auth/.work/00042/review-by-{expert-role}.md) - {N Findings / 0 Findings}
```

## Expert-Specific Guidelines

Under ゼロトレランス, quality is binary. Each expert reviews against a spec / rule
set and emits Findings (clause-violating, non-negotiable) and Observations
(non-violating notes). No numeric ratings, no severity tiers.

### Software Engineer

**Review Focus:**
- Architecture: Design patterns, separation of concerns, modularity
- Code Quality: Readability, naming, complexity, duplication
- Best Practices: Language idioms, framework conventions, error handling
- Maintainability: Documentation, testability, extensibility

### Prompt Engineer

**Review Focus:**
- Clarity: Instructions are clear and unambiguous
- Completeness: All necessary context and steps provided
- Agent Behavior: Prompts guide agent to correct actions
- Examples: High-quality examples that illustrate concepts

### Technical Writer

**Review Focus:**
- Structure: Logical organization, proper heading hierarchy
- Clarity: Easy to understand, jargon explained
- Accuracy: Information is correct and up-to-date
- Consistency: Terminology, formatting, style consistent

### QA Engineer

**Review Focus:**
- Coverage: Tests cover main paths and edge cases
- Edge Cases: Boundary conditions, error cases tested
- Test Design: Well-structured, maintainable tests
- Assertions: Clear, specific, meaningful assertions

### DevOps Engineer

**Review Focus:**
- Security: No secrets exposed, secure configurations
- Validation: Input validation, error handling
- Environment: Works across different environments
- Dependencies: Version compatibility, security updates

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
