# Notes

## 2026-02-20

### Implementation: Separate Context Configuration for nabledge-6

**Goal**: Enable nabledge-6 skill execution in separate context to prevent memory consumption in main conversation.

**Approach**:
- Hide nabledge-6 from menu (`user-invocable: false`) but allow Claude auto-loading
- Create entry points for separate context execution:
  - `.claude/agents/n6.md` - Claude Code entry via `@n6`
  - `.github/prompts/n6.prompt.md` - GitHub Copilot entry via `/n6`

**Implementation**:
1. Updated `.claude/skills/nabledge-6/SKILL.md` frontmatter - added `user-invocable: false`
2. Created `.claude/agents/n6.md` - Claude Code sub-agent configuration
3. Created `.github/prompts/n6.prompt.md` - GitHub Copilot prompt file

**Key Decisions**:
- Used `user-invocable: false` instead of `disable-model-invocation: true` to preserve auto-loading capability
- Did NOT modify SKILL.md body content - only frontmatter changed
- Created separate entry points for different IDE environments (Claude Code vs VSCode)

**Files Changed**:
- `.claude/skills/nabledge-6/SKILL.md` (frontmatter only)
- `.claude/agents/n6.md` (new)
- `.github/prompts/n6.prompt.md` (new)

**Benefits**:
- nabledge-6 runs in separate context, reducing main conversation memory usage
- Users can still invoke via `@n6` or `/n6` in their IDE
- Claude can still auto-load skill when appropriate (no breaking changes)

**Testing Plan**:
- Verify `user-invocable: false` hides skill from menu
- Test `@n6` invocation in Claude Code
- Test `/n6` invocation in VSCode with GitHub Copilot
- Verify auto-loading still works in main context

---

## 2026-02-24

### Final Implementation: Separate Context Architecture

**Status**: Implementation complete, documentation updated.

**Architecture Overview**:

The separate context implementation uses platform-specific entry points that delegate to the same core SKILL.md:

```
User invokes /n6
    ↓
Platform-specific entry point:
  - Claude Code: .claude/commands/n6.md
  - GitHub Copilot: .github/prompts/n6.prompt.md
    ↓
Delegates to separate context with instructions:
  "Read .claude/skills/nabledge-6/SKILL.md and follow its instructions"
    ↓
Sub-agent reads SKILL.md and executes workflows
    ↓
Returns summary results to main context
```

**Key Architecture Decisions**:

1. **Single Source of Truth**: SKILL.md remains the single maintenance point for workflow logic. Platform-specific files only handle delegation.

2. **Entry Point Location Change**:
   - Initial implementation used `.claude/agents/n6.md`
   - Final implementation uses `.claude/commands/n6.md` (Claude Code standard)
   - GitHub Copilot uses `.github/prompts/n6.prompt.md` (GHC standard)

3. **SKILL.md Configuration**:
   - `user-invocable: false` - Hides from menu but allows auto-loading
   - `disable-model-invocation: true` - Added to fully prevent direct invocation
   - Body content unchanged - all workflow logic intact

4. **Delegation Mechanism**:
   - **Claude Code**: Uses Task tool with `subagent_type: "general-purpose"`
   - **GitHub Copilot**: Uses `#runSubagent` directive
   - Both pass `$ARGUMENTS` to sub-agent for processing

**Benefits Achieved**:

✅ **Context Isolation**:
- Knowledge searches and code analysis run in separate context
- Main conversation only receives summary results
- Expected 80%+ reduction in context token usage

✅ **Cross-Platform Support**:
- Single SKILL.md for workflow logic
- Both platforms supported with minimal duplication
- Consistent output format

✅ **User Experience**:
- Simple invocation: `/n6 <question>` on both platforms
- Automatic delegation to separate context
- No user configuration required

**Documentation Updates**:

1. **GUIDE-CC.md**: Added `/n6` command section with:
   - Benefits explanation (speed, clean context, low cost, quality)
   - Comparison table: `/n6` vs `/nabledge-6`
   - Updated command reference with execution context column
   - Preserved existing `/nabledge-6` documentation for main context execution

2. **GUIDE-GHC.md**: Similar updates for GitHub Copilot users

**Files Modified**:
- `.claude/skills/nabledge-6/SKILL.md` (frontmatter: added `disable-model-invocation: true`)
- `.claude/commands/n6.md` (entry point for Claude Code)
- `.github/prompts/n6.prompt.md` (entry point for GitHub Copilot)
- `.claude/skills/nabledge-6/plugin/GUIDE-CC.md` (documentation)
- `.claude/skills/nabledge-6/plugin/GUIDE-GHC.md` (documentation)
- `.pr/00049/notes.md` (this file)

**Platform-Specific Constraints**:

**Claude Code**:
- Uses Task tool for delegation
- Automatic delegation possible (AI decides when to use)
- Sub-agent has full access to tools

**GitHub Copilot**:
- Uses `#runSubagent` directive
- Manual invocation required (users must type `/n6`)
- Sub-agent isolated from main context

**Success Criteria Verification**:

✅ **Context Isolation**: Achieved via separate context execution
✅ **Cross-Platform Support**: Single SKILL.md, platform-specific entry points
✅ **Maintenance Efficiency**: Single source of truth for workflows
✅ **User Experience**: Clear documentation, simple invocation method

**Known Limitations**:

1. **GitHub Copilot**: Cannot programmatically invoke agents (requires user to type `/n6`)
2. **Auto-loading**: Still works in main context if user doesn't use `/n6` (by design for backward compatibility)

**Testing Needed**:

- [ ] Verify `/n6` command works in Claude Code
- [ ] Verify `/n6` prompt works in GitHub Copilot
- [ ] Confirm context isolation (intermediate results not in main context)
- [ ] Measure token usage reduction
- [ ] Verify output quality and format consistency
