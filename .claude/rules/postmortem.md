# Post-mortem Format

Create post-mortems for significant bugs, production incidents, or systemic failures. Not for trivial bugs or expected failures.

## Location

```
.pr/xxxxx/postmortem-<topic>.md
```

Where xxxxx is 5-digit PR number (e.g., `.pr/00027/postmortem-plugin-recognition.md`)

## Required Sections

1. **Incident Summary** - 2-3 sentences: what happened, who affected, impact severity
2. **Timeline** - Chronological events with timestamps
3. **Root Cause Analysis** - Immediate cause, contributing factors, systemic issues
4. **Resolution** - Approach chosen, changes made, advantages/trade-offs, alternatives considered
5. **Horizontal Check** - Method, what checked, key findings, link to detailed document
6. **Prevention Measures** - Tests added, documentation updated, process improvements
7. **Lessons Learned** - What went well, what could improve, technical insights, process improvements

## Template

```markdown
# Post-mortem: [Brief Title]

**Related Issue**: #[issue-number]
**Date**: YYYY-MM-DD
**Severity**: [Critical | High | Medium | Low]

## Incident Summary
[2-3 sentences: what happened, who affected, impact]

## Timeline
**YYYY-MM-DD HH:MM** - [Event]
**YYYY-MM-DD HH:MM** - [Root cause identified]
**YYYY-MM-DD HH:MM** - [Fix deployed]

## Root Cause Analysis

### Immediate Cause
[What directly triggered the failure]

### Contributing Factors
[Conditions that enabled the failure]

### Systemic Issues
[Architecture, process, or assumption problems]

## Resolution

### Approach Chosen
[Solution implemented]

### Changes Made
[Specific files and modifications]

### Why This Approach
**Advantages**: [Benefits]
**Trade-offs**: [Costs]

### Alternatives Considered
1. [Option]: [Why rejected]

## Horizontal Check

**Method**: [How similar issues found]
**Checked**: [Files, patterns examined]
**Key Findings**:
- [Finding]: ✅/❌ [Status]

**Details**: See `.pr/xxxxx/horizontal-check-[topic].md`

## Prevention Measures

1. **[Category]** - [Specific action and benefit]
2. **[Category]** - [Specific action and benefit]

## Lessons Learned

### What Went Well
- [Positive aspect]

### What Could Improve
- [Improvement opportunity]

### Technical Insights
- [Understanding gained]

### Process Improvements
- [How to handle similar issues better]
```
