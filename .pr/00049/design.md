# Design: Separate Context Execution for nabledge-6

**Issue**: #49
**Date**: 2026-02-20
**Status**: Draft

## Problem Statement

nabledge-6 skills execute in main agent context, causing:
- Context pollution from large-scale file searches and analysis
- Degraded response quality due to context bloat
- Higher costs from excessive token consumption
- Slower responses as context fills

**Goal**: Execute nabledge-6 operations in separate contexts to keep main conversation clean and focused.

## Platform Research Findings

### Claude Code

**Capabilities** (from official docs):
- ✅ Custom agents in `.claude/agents/`
- ✅ Agents can invoke skills via `skills:` frontmatter preload
- ✅ Agents have full tool access (Read, Grep, Glob, Bash, etc.)
- ✅ Automatic context isolation and result summarization
- ✅ Can be invoked programmatically via Task tool

**Limitations**:
- ❌ Subagents cannot spawn other subagents (no nesting)
- ⚠️ Skills must be explicitly listed in agent frontmatter (not auto-inherited)

### GitHub Copilot

**Capabilities** (from official docs):
- ✅ **Custom Agents** in `.github/agents/*.agent.md`
- ✅ **Can load skills** from `.github/skills/` or `.claude/skills/`
- ✅ Invocation via `/agent name` command
- ✅ Context isolation (agents run in separate context)
- ✅ Tool access configurable via `tools:` frontmatter
- ✅ MCP server support for external data

**Limitations**:
- ⚠️ **Manual invocation** (user must type `/agent name`)
- ⚠️ Cannot be invoked programmatically from skills
- ⚠️ Skills must be explicitly listed in agent frontmatter

**Note**: GitHub also has "Agentic Workflows" (`.github/workflows/*.md`) which are different - those are automated background processes running in GitHub Actions, not interactive agents.

## Original Proposal Analysis

**User's proposal**: "Create agent that invokes nabledge-6 skill from separate context"

**Feasibility**:
- ✅ **Claude Code**: Fully feasible with `.claude/agents/nabledge-6.md`
- ✅ **GitHub Copilot**: Fully feasible with `.github/agents/nabledge-6.agent.md`
- ✅ **Cross-platform**: Both support agent + skill architecture

**Key findings**:
- Both platforms support custom agents that can load skills
- Both provide context isolation
- Main difference: CC auto-invokes via Task tool, GHC requires manual `/agent` command

## Design Options

### Option 1: Agent-Wraps-Skill Approach (Recommended)

**Approach**: Create parallel agent files that load existing nabledge-6 skill

**Implementation**:

**Claude Code** (`.claude/agents/n6.md`):
```yaml
---
name: n6
description: Nablarch 6 knowledge search and code analysis agent
skills:
  - nabledge-6
tools: Read, Grep, Glob, Bash
---

# Nablarch 6 Assistant Agent

This agent provides separate-context execution for nabledge-6 operations.
The nabledge-6 skill is preloaded and available for all operations.

Execute nabledge-6 skill workflows as requested by the user.
```

**GitHub Copilot** (`.github/agents/n6.agent.md`):
```yaml
---
name: n6
description: Nablarch 6 framework knowledge and code analysis
tools: ['read', 'search', 'edit', 'grep']
---

# Nablarch 6 Assistant Agent

This agent provides separate-context execution for nabledge-6 operations.
Load and execute nabledge-6 skill from `.claude/skills/nabledge-6/`.

{Similar instructions to Claude Code version}
```

**Usage**:
- **Claude Code**: Automatic delegation via Task tool (transparent to user)
- **GitHub Copilot**: User types `/agent n6` then asks questions

**Pros**:
- ✅ Clean context isolation on both platforms
- ✅ Uses existing nabledge-6 skill as-is (zero skill changes)
- ✅ Single maintenance point (skill codebase)
- ✅ Minimal implementation effort (two small agent files)
- ✅ Cross-platform compatible architecture

**Cons**:
- ⚠️ Different invocation methods (CC automatic, GHC manual)
- ⚠️ Adds indirection layer (but necessary for context isolation)
- ⚠️ GitHub Copilot requires user to remember `/agent` command

### Option 2: Workflow Refactoring

**Approach**: Restructure skill into lightweight dispatcher + heavy modules

**Structure**:
```
.claude/skills/nabledge-6/
  SKILL.md                    # Lightweight dispatcher
  workflows/                  # Lightweight orchestration
  modules/                    # NEW: Heavy analysis logic
    handler-search.md
    dependency-analysis.md
    code-structure.md
```

**Agents load modules directly**, bypassing skill layer.

**Pros**:
- ✅ Cleaner architecture (separation of concerns)
- ✅ More flexible (modules reusable across contexts)
- ✅ Better testability (modules isolated)

**Cons**:
- ❌ Requires significant refactoring
- ❌ More complex architecture
- ❌ Migration effort for existing workflows
- ❌ Breaks existing skill users during transition

## Recommended Design

**Agent-Wraps-Skill Approach** (Option 1):

1. **Create `.claude/agents/n6.md` for Claude Code**
   - Agent name: `n6` (short, easy to type)
   - Preload nabledge-6 skill via `skills:` frontmatter
   - Automatic delegation via Task tool (transparent to user)
   - Clean context isolation achieved

2. **Create `.github/agents/n6.agent.md` for GitHub Copilot**
   - Agent name: `n6` (short, easy to type)
   - Load nabledge-6 skill from `.claude/skills/nabledge-6/`
   - Manual invocation via `/agent n6` command (easy to remember!)
   - Same context isolation benefits

3. **Keep existing nabledge-6 skill unchanged**
   - Skill name remains: `nabledge-6` (descriptive)
   - Zero changes to skill code
   - Agents wrap skill, not replace it
   - Skill remains usable directly if user prefers

4. **Document invocation methods**
   - Update GUIDE-CC.md: "Automatically uses separate context"
   - Update GUIDE-GHC.md: "Use `/agent n6` for separate context"

**Naming rationale**:
- **Agent name**: `n6` - Short for frequent user input (`/agent n6`)
- **Skill name**: `nabledge-6` - Descriptive for marketplace and internal reference
- **Future**: `n5` agent for nabledge-5 skill

**Why this approach**:
- ✅ Minimal implementation effort (two small agent files)
- ✅ Zero risk to existing skill functionality
- ✅ Both platforms achieve context isolation
- ✅ Single codebase maintenance (skill unchanged)
- ✅ User experience optimal for each platform
- ✅ Short agent name easy to type and remember

## Implementation Plan

### Phase 1: Create Agent Files

1. **Create `.claude/agents/n6.md` (Claude Code)**:
   ```yaml
   ---
   name: n6
   description: Nablarch 6 framework knowledge and code analysis
   skills:
     - nabledge-6
   tools: Read, Grep, Glob, Bash
   ---

   # Nablarch 6 Assistant Agent

   Execute nabledge-6 skill workflows in separate context.
   The skill is preloaded and available for all operations.
   ```

2. **Create `.github/agents/n6.agent.md` (GitHub Copilot)**:
   ```yaml
   ---
   name: n6
   description: Nablarch 6 framework knowledge and code analysis
   tools: ['read', 'search', 'edit', 'grep']
   ---

   # Nablarch 6 Assistant Agent

   Load and execute nabledge-6 skill from .claude/skills/nabledge-6/.
   Provide knowledge search and code analysis in separate context.
   ```

3. **No changes to existing skill** - Agents wrap skill, don't modify it

### Phase 2: Enable Auto-Delegation (Claude Code)

1. Modify `.claude/skills/nabledge-6/SKILL.md`:
   - Add detection: If main context, delegate to `n6` agent via Task tool
   - If already in agent context, execute normally
   - GitHub Copilot: Skip delegation (manual `/agent n6` invocation)

2. Test automatic delegation:
   - User invokes `/nabledge-6` in main context
   - Should automatically spawn `n6` agent
   - Verify context isolation

### Phase 3: Documentation

1. **Update GUIDE-CC.md**:
   - Add "Automatic Context Isolation" section
   - Explain transparent delegation to `n6` agent
   - Document benefits (clean context, faster responses)

2. **Update GUIDE-GHC.md**:
   - Add "Using Separate Context" section
   - Document `/agent n6` invocation (short and easy!)
   - Explain when to use agent vs direct skill

3. **Update CHANGELOG**:
   - Add feature: Context isolation via custom agents (both platforms)
   - Note: Use `/agent n6` for separate context execution
   - Platform differences documented (CC automatic, GHC manual)

### Phase 4: Validation

1. **Test both platforms**:
   - Claude Code: Verify auto-delegation to `n6` works
   - GitHub Copilot: Verify `/agent n6` loads skill correctly

2. **Measure context reduction**:
   - Run typical handler search scenario
   - Compare token usage: main context vs agent context
   - Target: 80%+ reduction in main context

3. **Verify response quality**:
   - Run nabledge-test scenarios with `n6` agent
   - Compare answer quality vs direct skill invocation
   - Document any differences

4. **Document findings** in `.pr/00049/notes.md`

## Open Questions

1. **Skill detection**: How does main agent detect nabledge-6 requests?
   - Option A: User explicitly invokes skill (`/nabledge-6`)
   - Option B: Claude detects based on conversation (unreliable)
   - **Decision**: Keep explicit invocation (no change)

2. **Agent vs Skill naming**: ✅ **RESOLVED**
   - Agent name: `n6` (short for user typing)
   - Skill name: `nabledge-6` (descriptive for marketplace)
   - Future: `n5` for nabledge-5

3. **Nested invocation**: What if user invokes skill while already in agent?
   - Current: Would fail (agents can't spawn subagents on Claude Code)
   - Solution: Detect context and execute directly if already in agent
   - Implementation: Check environment or context metadata in SKILL.md

4. **GitHub Copilot future**: If GH adds automatic agent delegation?
   - Current design allows easy migration
   - Just enable automatic delegation in SKILL.md
   - No architecture changes needed

## Success Criteria Mapping

| Criterion | Solution | Status |
|-----------|----------|--------|
| Execute in separate context (CC & GHC) | CC: ✅ Agent, GHC: ✅ Agent | **Met** |
| Main context clean (CC & GHC) | CC: ✅ Automatic, GHC: ✅ Manual | **Met** |
| 80%+ token reduction | Both platforms via agents | To validate |
| Single maintenance point | ✅ One skill, agents wrap it | **Met** |
| Both platforms supported | CC: ✅ Auto, GHC: ✅ Manual `/agent` | **Met** |
| No duplication | ✅ Agents reuse skill | **Met** |
| Testing verifies both platforms | Need test for both CC and GHC | To implement |

**Constraints accepted**:
- ⚠️ **Invocation difference**: Claude Code auto-delegates, GitHub Copilot requires `/agent` command
- ⚠️ **User action**: GHC users must learn `/agent nabledge-6` command
- ✅ **Both achieve core goal**: Context isolation on both platforms

**All success criteria achievable** with user documentation about platform differences.

## Decision

**Proceed with Agent-Wraps-Skill Approach** (user's original proposal):
- ✅ Create `.claude/agents/n6.md` for Claude Code (auto-delegation)
- ✅ Create `.github/agents/n6.agent.md` for GitHub Copilot (manual `/agent n6`)
- ✅ Agent name: `n6` (short, easy to type)
- ✅ Keep existing nabledge-6 skill unchanged (agents wrap it)
- ✅ Both platforms achieve context isolation
- ✅ Single skill codebase maintained
- ⚠️ Accept invocation method difference (CC automatic, GHC manual)

**User confirmation**: Awaiting approval to proceed with implementation.
