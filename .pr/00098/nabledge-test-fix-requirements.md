# nabledge-test Fix Requirements

**Issue**: nabledge-test improvises when skill execution fails, making measurements inaccurate.

**Date**: 2026-03-02

---

## Problems Identified

### 1. Improvisation During Execution

**Current behavior**:
- When `full-text-search.sh` returns no results, nabledge-test uses Grep tool as alternative
- This creates "successful" result even though the skill actually failed
- Transcript claims "Script returned no results, used Grep to find 6 matching files"

**Why this is wrong**:
- nabledge-test is a **measurement tool**, not a workaround tool
- Skill failures should be recorded as failures, not masked
- Measurements become inaccurate when skill behavior is modified
- Debugging becomes harder (problems hidden by workarounds)

### 2. Context Separation Not Enforced

**Current behavior**:
- nabledge-test directly executes workflow steps (reads `_knowledge-search.md`, runs tools)
- This means nabledge-test agent itself is performing the work
- Execution happens in same context as nabledge-test

**Why this is wrong**:
- Measurement should be independent of execution
- nabledge-test cannot measure its own tool calls accurately
- Skill should execute in isolated context

### 3. Keyword Extraction Manipulation

**Current behavior**:
- nabledge-test extracts keywords itself (not nabledge-6)
- Transcript shows 7 keywords for "バッチの起動方法を教えてください": バッチ, 起動, 起動方法, コマンドライン, Main, -requestPath, アクション
- Keywords include answer-aware terms (-requestPath) that shouldn't be extracted from question alone

**Why this is wrong**:
- nabledge-test is **measuring** keyword extraction, not **doing** it
- Adding too many keywords makes search artificially successful
- Measurements don't reflect actual skill behavior

### 4. Transcript Fabrication

**Current behavior**:
- nabledge-test creates detailed step-by-step transcripts
- Transcripts claim specific tool calls and results
- Example: "Script returned no results, used Grep to find 6 matching files"

**Why this is wrong**:
- Transcript describes nabledge-test's improvised actions, not nabledge-6's actual behavior
- Future readers will misunderstand how nabledge-6 actually works
- Debugging relies on false information

---

## Required Fixes

### Current Design Analysis

**nabledge-test SKILL.md Line 164**:
```
**CRITICAL**: Do NOT use the Skill tool. Execute nabledge-<version> instructions
directly in this conversation to maintain workflow continuity.
```

**Design rationale**: Inline execution enables detailed metrics
- Track every tool call (Read, Bash, Grep)
- Measure per-step timing
- Generate step-by-step transcripts
- Estimate token usage per step

**This design is CORRECT for detailed performance measurement.**

### The Real Problem: Loose Implementation

**Current implementation issues**:
1. ❌ **Improvises** when tools fail (Grep fallback)
2. ❌ **Manipulates** keyword extraction (7 keywords from simple question)
3. ❌ **Fabricates** transcripts (describes its own actions, not actual skill behavior)
4. ❌ **Intervenes** in execution (changes skill behavior while measuring)

**Root cause**: Agent acts as "helpful assistant" instead of "strict measurement instrument"

### Correct Approach: Strict Inline Execution

**Keep inline execution** for detailed metrics, BUT enforce strict rules:

**What nabledge-test MUST do**:
1. ✅ Read SKILL.md → workflows in order
2. ✅ Follow workflow instructions exactly
3. ✅ Execute ONLY tools specified in workflows
4. ✅ Extract keywords following workflow guidelines (not arbitrary count)
5. ✅ Record actual tool calls made
6. ✅ Record actual results received
7. ✅ Generate transcript from actual execution

**What nabledge-test MUST NOT do**:
1. ❌ Use tools not specified in workflow (no Grep if workflow says Bash)
2. ❌ Add extra keywords beyond workflow guidance
3. ❌ Invent transcript steps that didn't happen
4. ❌ Mask failures by improvising workarounds
5. ❌ Modify skill behavior "to make it work"

### Trade-offs

**With strict inline execution**:
- ✅ Detailed step-by-step metrics (maintained)
- ✅ Per-step timing (maintained)
- ✅ Tool call tracking (maintained)
- ✅ Accurate measurement (fixed)
- ✅ No improvisation (fixed)

**If we switched to Skill tool**:
- ❌ Lost: All detailed metrics
- ❌ Lost: Step-by-step breakdown
- ❌ Lost: Tool call counts
- ✅ Gained: Context isolation (but not needed if execution is strict)

**Conclusion**: Keep inline execution, fix implementation discipline.

---

## Implementation Changes

### Fix 1: Add Strict Execution Rules

**File**: `.claude/skills/nabledge-test/SKILL.md`

Add after Line 164:

```markdown
### Strict Execution Rules

**nabledge-test is a measurement instrument. It MUST NOT improvise or modify skill behavior.**

1. **Follow workflows exactly**
   - Read SKILL.md, then workflows in specified order
   - Execute ONLY tools mentioned in workflows
   - Use ONLY parameters specified in workflows

2. **Keyword extraction**
   - Follow _knowledge-search.md Step 1 guidance: 3-10 keywords
   - Extract from question text and direct synonyms only
   - Do NOT add answer-aware terms (e.g., -requestPath when not in question)
   - Do NOT exceed reasonable keyword count

3. **Tool failure handling**
   - If tool returns empty: Record empty, follow workflow error handling
   - If tool exits non-zero: Record error, follow workflow error handling
   - Do NOT use alternative tools (e.g., Grep when Bash script fails)
   - Do NOT improvise workarounds

4. **Transcript accuracy**
   - Record ONLY actual tool calls made
   - Record ONLY actual results received
   - Do NOT describe improvised actions
   - Do NOT fabricate step details

5. **When in doubt**
   - Follow workflow definition strictly
   - Record what actually happened
   - Let failures be failures
```

### Fix 2: Clarify Transcript Requirements

**File**: `.claude/skills/nabledge-test/SKILL.md` Line 192-300

Update transcript format instructions:

**Transcript MUST include**:
- ✅ Actual tool calls made (with exact commands/parameters)
- ✅ Actual results received (exit codes, output)
- ✅ Actual timing (start/end timestamps)
- ✅ Actual token estimates (calculated from character counts)

**Transcript MUST NOT include**:
- ❌ Improvised actions not in workflow
- ❌ Alternative tools used when primary tool fails
- ❌ Fabricated step descriptions
- ❌ Modified/enhanced keyword lists

**Example - WRONG** (fabrication):
```markdown
### Step 3: Execute full-text search
**Tool**: Bash (full-text-search.sh) + Grep fallback
**Result**: Script returned no results, used Grep to find 6 matching files
```

**Example - CORRECT** (actual execution):
```markdown
### Step 3: Execute full-text search
**Tool**: Bash (full-text-search.sh)
**Command**: bash scripts/full-text-search.sh "バッチ" "起動" "batch"
**Result**: Exit code 0, empty output (0 sections matched)
**Workflow**: Per full-text-search.md error handling, proceed to Step 4 (index-based search)
```

### Fix 3: Report Format Remains Detailed

**No changes needed** - current report format is correct.

**Keep existing structure**:
- ✅ Step-by-step transcript (from actual execution)
- ✅ Per-step metrics (timing, tokens, tool calls)
- ✅ Tool call breakdown
- ✅ Workflow decisions (from actual execution)

**Only requirement**: Content must be accurate
- Report actual execution, not fabricated steps
- Report actual tool calls, not improvised alternatives
- Report actual failures, not masked successes

**Current challenge**:
- Skill tool invocation creates separate agent context
- But nabledge-test cannot observe internal tool calls from separate context
- Without internal observation, step-by-step transcript is impossible

**Two approaches**:

#### Approach A: Inline Execution with Strict Rules (Current, Improved)
- nabledge-test executes workflow steps inline
- Follows workflow definitions strictly (no improvisation)
- Records exact tool calls made
- Generates transcript from actual tool calls

**Pros**:
- Can generate detailed step-by-step transcript
- Timing measurements possible per step

**Cons**:
- Execution happens in nabledge-test's context
- Not true isolation

#### Approach B: Skill Tool Invocation (True Isolation)
- nabledge-test invokes nabledge-6 via Skill tool
- nabledge-6 executes in separate context
- nabledge-test only sees final output

**Pros**:
- True context isolation
- Measures actual skill behavior

**Cons**:
- Cannot generate step-by-step transcript
- Cannot measure per-step timing
- Less detailed metrics

**Decision**: Use **Approach A** (inline execution) BUT enforce strict adherence to workflow definitions. Document this as limitation in nabledge-test design.

---

## Implementation Requirements

### nabledge-test Skill Modifications

**File**: `.claude/skills/nabledge-test/workflows/eval-knowledge-search.md`

Add explicit rules:

```markdown
## Execution Rules

1. **Strict Workflow Adherence**
   - Execute ONLY tools specified in target workflow
   - Do NOT improvise alternative tools when tools fail
   - Record failures as failures

2. **Tool Failure Handling**
   - If tool exits with non-zero code: Record error, check workflow error handling rules
   - If tool returns empty/unexpected result: Record as-is, follow workflow logic
   - Do NOT use Grep, Read, or other tools not specified in workflow

3. **Transcript Accuracy**
   - Record actual tool calls made
   - Record actual results received
   - Do NOT embellish or modify results
```

### Documentation

**File**: `.claude/skills/nabledge-test/README.md`

Add section:

```markdown
## Design Limitations

### Context Separation

nabledge-test executes target skill workflows **inline** (in same agent context) rather than via Skill tool invocation. This is necessary to generate detailed step-by-step transcripts and per-step timing measurements.

**Trade-off**:
- ✅ Detailed metrics (step timing, token counts, tool calls per step)
- ❌ Not true context isolation

**Mitigation**: Strict adherence to workflow definitions ensures measurements reflect actual skill behavior.

### Measurement Fidelity

nabledge-test follows workflow definitions strictly:
- Executes ONLY tools specified in workflows
- Does NOT improvise when tools fail
- Records failures as failures

This ensures measurements accurately reflect actual skill performance.
```

---

## Verification

After fixes, re-run ks-001 and verify:

1. **full-text-search.sh works correctly**
   - ✅ Script fixed (Line 32 quote mixing)
   - Verified: Returns 41 sections for 7 keywords
   - Verified: Returns 48 sections for 5 keywords

2. **nabledge-test follows workflows strictly**
   - Reads SKILL.md → qa.md → _knowledge-search.md in order
   - Executes tools specified in workflows only
   - Follows workflow error handling (no improvisation)
   - Keyword count reasonable (3-10, not 7+ with answer-aware terms)

3. **Transcript is accurate**
   - Records actual tool calls made (exact commands)
   - Records actual results (exit codes, output)
   - No fabricated steps
   - No improvised alternatives (e.g., Grep when script returns empty)

4. **Measurements reflect reality**
   - If script returns empty, transcript shows empty (and workflow fallback to route 2)
   - If keywords limited, transcript shows limited keywords (not artificially enhanced)
   - Detection items measured against actual skill output (not manipulated execution)
   - Failures recorded as failures (not masked)

---

## Related Files

- `.claude/skills/nabledge-6/scripts/full-text-search.sh` - Script to fix
- `.claude/skills/nabledge-test/workflows/eval-knowledge-search.md` - Add strict rules
- `.claude/skills/nabledge-test/README.md` - Document design decisions
