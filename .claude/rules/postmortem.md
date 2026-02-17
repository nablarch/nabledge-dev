# Post-mortem Format

A post-mortem is a blameless analysis of an incident, bug, or failure that documents what happened, why it happened, and how to prevent similar issues in the future.

## Purpose

Post-mortems serve to:
- **Learn from failures** without assigning blame to individuals
- **Document root causes** for future reference
- **Prevent recurrence** through systematic analysis
- **Share knowledge** across the team
- **Improve processes** based on real incidents

## When to Write a Post-mortem

Create a post-mortem for:
- **Significant bugs** that affected users or blocked development
- **Production incidents** that impacted service availability or data integrity
- **Critical issues** that required multiple investigation rounds
- **Complex failures** with non-obvious root causes
- **System-level problems** revealing architectural or process gaps

Do NOT write post-mortems for:
- Trivial bugs (typos, single-line fixes)
- Expected failures (known limitations)
- Individual mistakes without systemic implications

## File Location

Post-mortems are stored in the work log directory:

```
work/YYYYMMDD/postmortem-<topic>.md
```

**Examples:**
- `work/20260217/postmortem-issue-27-plugin-recognition.md`
- `work/20260215/postmortem-marketplace-race-condition.md`
- `work/20260220/postmortem-ci-deployment-failure.md`

## Required Sections

### 1. Incident Summary

A concise overview (2-3 sentences) covering:
- What happened
- Who was affected
- Impact severity

**Example:**
```markdown
## Incident Summary

The nabledge-6 plugin was not recognized on first Claude Code startup after running setup-6-cc.sh. All new users experienced this issue, requiring a manual restart to access the skill. This affected onboarding experience and created support burden.
```

### 2. Timeline

Chronological sequence of events from initial observation to resolution.

- Use absolute timestamps or relative times (Day 1, Day 2)
- Include key milestones: detection, investigation, root cause identification, fix implementation, verification
- Note important discoveries or decisions
- Keep it factual, not interpretive

**Example:**
```markdown
## Timeline

**2026-02-15 10:30** - Issue reported by user: skill not available after setup
**2026-02-15 11:00** - Reproduction confirmed in test environment
**2026-02-15 14:30** - Initial hypothesis: settings.json not loaded correctly
**2026-02-16 09:00** - Root cause identified: marketplace async fetch vs sync skill loading race condition
**2026-02-16 15:00** - Solution designed: switch to direct skill copy pattern
**2026-02-17 11:00** - Fix implemented and tested
**2026-02-17 14:00** - All verification completed
```

### 3. Root Cause Analysis

Deep technical explanation of why the incident occurred.

- Explain the underlying system behavior
- Identify contributing factors (not just immediate cause)
- Use diagrams or code examples if helpful
- Distinguish between symptoms and root cause
- Apply "5 Whys" or similar systematic analysis

**Structure:**
- **Immediate Cause**: What directly triggered the failure
- **Contributing Factors**: Conditions that enabled the failure
- **Systemic Issues**: Deeper problems in architecture, process, or assumptions

**Example:**
```markdown
## Root Cause Analysis

### Immediate Cause

Claude Code's marketplace plugin system has a two-layer storage architecture:
1. Project-level settings (`.claude/settings.json`)
2. User-level cache (`~/.claude/plugins/`)

The setup script configured layer 1, but skills are loaded from layer 2.

### Contributing Factors

- Marketplace fetching is asynchronous (background process)
- Skill loading is synchronous (startup blocking)
- Race condition: async fetch completes AFTER sync skill loading on first startup

### Systemic Issues

- Insufficient understanding of Claude Code's plugin architecture
- No test coverage for first-startup scenarios
- Setup script based on incomplete marketplace behavior assumptions
```

### 4. Resolution

Detailed description of how the issue was fixed.

- **Approach Chosen**: What solution was implemented
- **Changes Made**: Specific files and modifications
- **Why This Approach**: Advantages and trade-offs
- **Alternatives Considered**: Other options and why they were rejected

Include code examples or diffs for clarity.

**Example:**
```markdown
## Resolution

### Approach Chosen

Switched from marketplace/plugin configuration to direct skill copy (same pattern as setup-6-ghc.sh).

### Changes Made

**scripts/setup-6-cc.sh**:
- Removed marketplace configuration code
- Added git sparse-checkout download
- Copy skill files directly to `.claude/skills/nabledge-6/`

**plugin/GUIDE-CC.md**:
- Removed marketplace/plugin prompt references
- Updated installation instructions for direct copy
- Clarified immediate availability without restart

### Why This Approach

**Advantages:**
- Eliminates race condition completely
- Proven pattern (GitHub Copilot setup already uses it)
- Immediate recognition without restart
- Not dependent on Claude Code's marketplace behavior

**Trade-offs:**
- Larger repo size (skill files committed)
- Manual updates needed (re-run setup for new versions)
- No automatic marketplace updates

### Alternatives Considered

1. **Add delay/retry logic**: Rejected - fragile, timing-dependent
2. **Prompt user to restart**: Rejected - poor user experience
3. **Hybrid approach**: Rejected - increased complexity
```

### 5. Horizontal Check

Reference to separate horizontal check document with summary of findings.

- Document the method used to find similar issues
- Summarize what was checked (files, patterns, configurations)
- List key findings with resolution status
- Link to detailed horizontal check document

**Example:**
```markdown
## Horizontal Check

**Method**: Systematic grep for marketplace/plugin patterns across repository

**Checked**:
- All setup scripts (setup-6-*.sh)
- Documentation files (GUIDE-*.md, README.md)
- GitHub Actions workflows
- Settings.json templates

**Key Findings**:
- setup-6-cc.sh: ❌ Uses marketplace (fixed in this issue)
- setup-6-ghc.sh: ✅ Uses direct copy (correct pattern)
- GUIDE-CC.md: ❌ References plugin prompts (fixed in this issue)
- Other files: ✅ No issues found

**Details**: See `work/20260217/horizontal-check-plugin-marketplace-issues.md`
```

### 6. Prevention Measures

Concrete actions taken to prevent recurrence.

- **Tests Added**: Automated verification
- **Documentation Updated**: Knowledge captured
- **Process Improvements**: Workflow changes
- **Architecture Changes**: System-level fixes
- **Monitoring Added**: Detection mechanisms

**Example:**
```markdown
## Prevention Measures

1. **Test Script Created**
   - `scripts/test-issue-27-reproduce.sh` verifies skill recognition on first startup
   - Runs in CI to catch regressions
   - Tests both old (broken) and new (fixed) approaches

2. **Documentation Updated**
   - GUIDE-CC.md now accurately describes direct skill installation
   - Removed all marketplace/plugin references
   - Added team sharing instructions

3. **Standards Established**
   - Created `.claude/rules/postmortem.md` for consistent analysis
   - Updated `.claude/rules/issues.md` with bug-specific success criteria
   - Established horizontal check process

4. **Pattern Library**
   - setup-6-ghc.sh documented as reference pattern
   - Direct skill copy approach preferred for both Claude Code and GitHub Copilot
```

### 7. Lessons Learned

Reflections on what worked well and what could improve.

- **What Went Well**: Positive aspects of detection, investigation, or resolution
- **What Could Improve**: Opportunities for better processes or tools
- **Technical Insights**: Deeper understanding gained
- **Process Improvements**: How to handle similar issues better

**Example:**
```markdown
## Lessons Learned

### What Went Well

- Pattern comparison with setup-6-ghc.sh quickly identified working solution
- Reproducible test environment caught the issue reliably
- Blameless analysis focused on system behavior, not individual errors

### What Could Improve

- Test on fresh environments earlier in development
- Document architecture assumptions explicitly
- Create test coverage for first-run scenarios proactively

### Technical Insights

- Claude Code's marketplace system is more complex than initially understood
- Auto-recognition from `.claude/skills/` is reliable and restart-free
- Two-layer storage (project + user cache) creates timing dependencies

### Process Improvements

- Establish horizontal check as standard bug investigation step
- Require post-mortems for issues affecting user onboarding
- Create architecture decision records (ADRs) for tool integration choices
```

## Template

Use this template as a starting point:

```markdown
# Post-mortem: [Brief Title]

**Related Issue**: #[issue-number]
**Date**: YYYY-MM-DD
**Severity**: [Critical | High | Medium | Low]
**Affected Users**: [Who was impacted]

## Incident Summary

[2-3 sentences: what happened, who affected, impact]

## Timeline

**YYYY-MM-DD HH:MM** - [Event]
**YYYY-MM-DD HH:MM** - [Event]
...

## Root Cause Analysis

### Immediate Cause

[What directly triggered the failure]

### Contributing Factors

[Conditions that enabled the failure]

### Systemic Issues

[Deeper problems in architecture, process, or assumptions]

## Resolution

### Approach Chosen

[What solution was implemented]

### Changes Made

[Specific files and modifications]

### Why This Approach

[Advantages and trade-offs]

### Alternatives Considered

[Other options and why rejected]

## Horizontal Check

**Method**: [How similar issues were identified]

**Checked**: [What was examined]

**Key Findings**:
- [Finding 1]: [Status]
- [Finding 2]: [Status]

**Details**: See `work/YYYYMMDD/horizontal-check-[topic].md`

## Prevention Measures

1. **[Category]**
   - [Specific action taken]
   - [Expected benefit]

2. **[Category]**
   - [Specific action taken]
   - [Expected benefit]

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

## Style Guidelines

### Blameless Culture

- Focus on systems and processes, not individuals
- Use passive voice or "the system" as subject
- Avoid phrases like "X failed to do Y" - instead "Y was not done because Z"
- Treat mistakes as learning opportunities

**Bad**: "Developer forgot to test on clean environment"
**Good**: "Testing on clean environment was not included in verification checklist"

### Systems Thinking

- Look for contributing factors, not just immediate causes
- Ask "why" multiple times to reach root cause
- Consider organizational and process factors
- Identify systemic patterns across incidents

### Concrete and Specific

- Use exact file paths, line numbers, timestamps
- Include code snippets or configuration examples
- Reference specific tools, versions, environments
- Provide reproducible steps

### Actionable Outcomes

- Every post-mortem should result in prevention measures
- Prevention measures should be concrete and verifiable
- Link to created tests, documentation, or process changes
- Define success criteria for prevention effectiveness

## Relationship to Other Documents

Post-mortems are part of the issue-driven development workflow:

1. **Issue** (`.claude/rules/issues.md`): Defines the problem and success criteria
2. **Work Log** (`.claude/rules/work-log.md`): Tracks daily implementation progress
3. **Post-mortem** (this document): Analyzes significant incidents for learning
4. **Horizontal Check**: Separate document identifying similar issues

## Rationale

This format ensures:

- **Blameless learning** - Focus on systems, not people
- **Knowledge preservation** - Insights captured for future reference
- **Systematic analysis** - Structured investigation prevents shallow fixes
- **Recurrence prevention** - Concrete measures documented and tracked
- **Continuous improvement** - Each incident improves processes
- **Team learning** - Shared understanding of complex system behavior

---

**Note**: Post-mortems are not about assigning fault. They are about understanding complex systems, learning from failures, and building resilience through systematic improvement.
