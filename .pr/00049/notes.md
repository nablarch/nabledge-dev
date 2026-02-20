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
