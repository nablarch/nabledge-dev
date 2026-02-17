# Implementation Plan: Issue #27 - nabledge-6 Plugin Recognition on First Startup

## Context

**Problem**: The nabledge-6 plugin is not recognized on first Claude Code startup after running setup-6-cc.sh. Users must restart Claude Code to use the skill, causing friction in onboarding.

**Root Cause**: Claude Code's marketplace system has a race condition. The setup script configures `.claude/settings.json` with marketplace/plugin settings, but Claude Code's asynchronous marketplace fetching completes AFTER the synchronous skill loading on first startup. This means the skill files aren't in the user-level cache (`~/.claude/plugins/`) when Claude Code first looks for them.

**Solution**: Switch from marketplace/plugin mechanism to direct skill copy (same method as setup-6-ghc.sh). Copy skill files directly to `.claude/skills/nabledge-6/`. Claude Code auto-recognizes skills in this directory without settings.json configuration or restart.

**Why This Matters**: This issue affects all new nabledge-6 users with Claude Code. Fixing it improves first-run experience and reduces support burden. It also establishes standardized bug investigation processes (post-mortem format, horizontal checks) for the team.

## Success Criteria from Issue #27

All 8 criteria must be satisfied:

1. ✅ Root cause identified and reproducible test environment created
2. ✅ Issue verified as resolved in test environment
3. ✅ Workaround documented (if applicable)
4. ✅ Horizontal check documented with method, results, and status
5. ✅ Recurrence prevention measures implemented
6. ✅ Post-mortem created in work/YYYYMMDD/ following standardized format
7. ✅ `.claude/rules/issues.md` updated with bug-specific Success Criteria
8. ✅ `.claude/rules/postmortem.md` created with standardized format

## Implementation Phases

### Phase 1: Establish Standards (Create Rule Files First)

These standards must exist before creating documentation that follows them.

#### 1.1 Create `.claude/rules/postmortem.md`

**Purpose**: Define standardized post-mortem format for bug analysis.

**Location**: `/home/tie303177/work/nabledge-dev-work1/.claude/rules/postmortem.md`

**Required Sections**:
- Purpose and when to write post-mortems
- Required sections: Incident Summary, Timeline, Root Cause Analysis, Resolution, Horizontal Check, Prevention Measures, Lessons Learned
- File location convention: `work/YYYYMMDD/postmortem-<topic>.md`
- Template with examples
- Rationale for standardization

**Key Content**:
- Similar structure to `.claude/rules/issues.md` (Purpose, Structure, Template, Examples, Rationale)
- Emphasize blameless culture and systems thinking
- Include specific examples for each section
- Reference related documents (issues.md, work-log.md)

#### 1.2 Update `.claude/rules/issues.md`

**Purpose**: Add bug-specific Success Criteria to ensure thorough investigation.

**Location**: `/home/tie303177/work/nabledge-dev-work1/.claude/rules/issues.md`

**Change**: Insert new section after "## Body Format" (after line 69), before "## Complete Example"

**New Section Title**: `## Bug-Specific Success Criteria`

**Content**:
- Explanation of why bugs need additional criteria
- Required criteria template with checkboxes:
  - Root cause identification and reproducible test
  - Fix verification in test environment
  - Workaround documentation (if applicable)
  - Horizontal check with method/results/status
  - Recurrence prevention measures
  - Post-mortem documentation
- Examples for bugs with and without workarounds
- Rationale section

### Phase 2: Horizontal Check (Identify Similar Issues)

#### 2.1 Create Horizontal Check Document

**Purpose**: Systematically examine repository for similar marketplace/plugin issues.

**Location**: `/home/tie303177/work/nabledge-dev-work1/work/20260217/horizontal-check-plugin-marketplace-issues.md`

**Structure**:
- **Check Method**: How patterns were identified (script search, documentation review, workflow analysis)
- **Check Results**: Findings in structured tables
  - Scripts examined (setup-6-cc.sh vs setup-6-ghc.sh)
  - Settings.json usage in development repository
  - Documentation references to marketplace/plugin
  - GitHub Actions workflows
- **Resolution Status**: For each finding, document if addressed/planned/not applicable
- **Follow-up Actions**: Immediate tasks and future considerations

**Key Findings to Document**:
- setup-6-cc.sh: ❌ Uses marketplace (needs fix)
- setup-6-ghc.sh: ✅ Uses direct copy (works correctly)
- GUIDE-CC.md: ❌ References plugin prompts (needs update)
- Other files: ✅ No issues found

### Phase 3: Core Fix (Modify Setup Script and Documentation)

#### 3.1 Update `scripts/setup-6-cc.sh`

**Purpose**: Switch from marketplace configuration to direct skill copy.

**Location**: `/home/tie303177/work/nabledge-dev-work1/scripts/setup-6-cc.sh`

**Pattern Reference**: `/home/tie303177/work/nabledge-dev-work1/scripts/setup-6-ghc.sh` lines 18-41

**Major Changes**:

1. **Header and Variables** (lines 11-26):
   - Remove marketplace-specific variables
   - Add download variables (REPO_URL, TEMP_DIR)
   - Change messaging from "plugin" to "skill"

2. **Download and Copy** (replace lines 28-112):
   ```bash
   cd "$TEMP_DIR"
   git clone --depth 1 --filter=blob:none --sparse --branch "$BRANCH" "$REPO_URL"
   cd "$REPO_NAME"
   git sparse-checkout set plugins/nabledge-6

   mkdir -p "$PROJECT_ROOT/.claude/skills"
   cp -r "$TEMP_DIR/$REPO_NAME/plugins/nabledge-6/skills/nabledge-6" "$PROJECT_ROOT/.claude/skills/"
   rm -rf "$TEMP_DIR"
   ```

3. **jq Installation** (keep lines 33-73, adjust messaging):
   - Keep same logic for Linux, GitBash, macOS
   - Update success message to reflect skill directory location

4. **Final Message** (replace lines 114-125):
   - Location: `.claude/skills/nabledge-6/`
   - Team sharing: Commit `.claude/skills/` directory
   - No restart required

**Intentional Differences from setup-6-ghc.sh**:
- ❌ NO .vscode/settings.json configuration (Claude Code doesn't need it)
- ✅ Same git sparse-checkout download pattern
- ✅ Same direct copy to .claude/skills/
- ✅ Same jq installation logic

#### 3.2 Update `.claude/skills/nabledge-6/plugin/GUIDE-CC.md`

**Purpose**: Update documentation to reflect direct skill installation.

**Location**: `/home/tie303177/work/nabledge-dev-work1/.claude/skills/nabledge-6/plugin/GUIDE-CC.md`

**Changes**:

1. **Installation Section** (lines 10-22):
   - Remove marketplace/plugin prompt references
   - Clarify skill directory creation (`.claude/skills/nabledge-6/`)
   - Emphasize auto-recognition and no restart needed
   - Update team sharing instructions (commit `.claude/skills/` not `.claude/settings.json`)

2. **Version Update Section** (lines 59-82):
   - Update paths from `settings.json` to `.claude/skills/nabledge-6/`
   - Keep version pinning instructions but update file references
   - Maintain Japanese language (user-facing documentation)

**Remove All References To**:
- "プラグインのインストールが促されます" (plugin installation prompts)
- `.claude/settings.json` changes or commits
- Marketplace configuration
- Plugin mechanism

**Add Clarity About**:
- Direct skill directory structure
- Immediate availability without restart
- Team sharing via `.claude/skills/` directory

### Phase 4: Testing and Verification

#### 4.1 Create Test Script

**Purpose**: Automated test to reproduce issue and verify fix.

**Location**: `/home/tie303177/work/nabledge-dev-work1/scripts/test-issue-27-reproduce.sh`

**Features**:
- Creates isolated test directories
- Tests old method (marketplace) - expects failure on first startup
- Tests new method (direct copy) - expects success on first startup
- Checks for `.claude/skills/nabledge-6/SKILL.md` (recognition requirement)
- Provides visual indicators (✅ ❌ ⚠️)
- Preserves test directory for manual inspection
- Returns exit code 0 on success, 1 on failure (CI-compatible)

**Test Logic**:
```bash
check_skill_recognition() {
  # Check if .claude/skills/nabledge-6/SKILL.md exists
  # This is what Claude Code uses for auto-recognition
}

# Test 1: Old method (download from release branch)
# Expected: Skill NOT immediately available (settings.json only)

# Test 2: New method (local setup-6-cc.sh)
# Expected: Skill immediately available (.claude/skills/)
```

#### 4.2 Execute Test and Document Results

**Action**: Run test script and verify fix works.

**Command**:
```bash
cd /home/tie303177/work/nabledge-dev-work1
bash scripts/test-issue-27-reproduce.sh
```

**Expected Output**:
- Old method: ⚠️ Skill NOT immediately available (marketplace config found)
- New method: ✅ Skill immediately available (SKILL.md exists)
- Test summary: Fix confirmed working

**Document**: Record test execution results in work log and post-mortem.

### Phase 5: Documentation and Post-mortem

#### 5.1 Create Post-mortem Document

**Purpose**: Complete analysis of Issue #27 for learning and future reference.

**Location**: `/home/tie303177/work/nabledge-dev-work1/work/20260217/postmortem-issue-27-plugin-recognition.md`

**Required Sections** (following `.claude/rules/postmortem.md` format):

1. **Incident Summary**: What happened, who affected, impact (2-3 sentences)

2. **Timeline**: Chronological events from observation to fix verification

3. **Root Cause Analysis**:
   - Claude Code's two-layer storage (project settings + user cache)
   - Async marketplace fetch vs sync skill loading
   - Race condition details

4. **Resolution**:
   - Approach chosen: Direct skill copy
   - Changes made to setup-6-cc.sh and GUIDE-CC.md
   - Code examples showing before/after
   - Why this approach (advantages, trade-offs)
   - Alternatives considered

5. **Horizontal Check**: Reference to `work/20260217/horizontal-check-plugin-marketplace-issues.md` with summary

6. **Prevention Measures**:
   - Test script created (regression prevention)
   - Documentation updated
   - Standards established (postmortem.md, issues.md)
   - Horizontal check process

7. **Lessons Learned**:
   - What worked well (pattern comparison with setup-6-ghc.sh)
   - What could improve (test on fresh environments earlier)
   - Technical insights (CC architecture, auto-recognition)
   - Process improvements

#### 5.2 Create Work Log

**Purpose**: Concise summary following `.claude/rules/work-log.md` format.

**Location**: `/home/tie303177/work/nabledge-dev-work1/work/20260217/issue-27-plugin-recognition-fix.md`

**Structure**:
- **What was done**: Investigation, implementation, documentation (bulleted list with file names)
- **Results**: Fix verification (test output), changed files list
- **Next steps**: Commit, test clean environment, create PR, verify Success Criteria

### Phase 6: Final Verification and Release Prep

#### 6.1 Verify All Success Criteria

**Action**: Systematically check each criterion from Issue #27.

**Verification Checklist**:

1. ✅ Root cause identified (documented in post-mortem)
2. ✅ Test environment created (test script in scripts/)
3. ✅ Issue verified resolved (test script passes)
4. ✅ Workaround documented (restart CC, noted as unnecessary with fix)
5. ✅ Horizontal check documented (method, results, status all present)
6. ✅ Prevention measures implemented (test script, docs, standards)
7. ✅ Post-mortem created (work/20260217/, follows standard format)
8. ✅ Rules updated (postmortem.md created, issues.md updated)

**Verification Commands**:
```bash
# Verify all files exist
ls -l scripts/setup-6-cc.sh
ls -l scripts/test-issue-27-reproduce.sh
ls -l .claude/skills/nabledge-6/plugin/GUIDE-CC.md
ls -l .claude/rules/postmortem.md
ls -l .claude/rules/issues.md
ls -l work/20260217/postmortem-issue-27-plugin-recognition.md
ls -l work/20260217/horizontal-check-plugin-marketplace-issues.md
ls -l work/20260217/issue-27-plugin-recognition-fix.md

# Run test
bash scripts/test-issue-27-reproduce.sh

# Verify issues.md update
grep "Bug-Specific Success Criteria" .claude/rules/issues.md

# Verify postmortem.md structure
grep "Required Sections" .claude/rules/postmortem.md
```

#### 6.2 Update CHANGELOG

**Purpose**: Document changes for release notes.

**Location**: `/home/tie303177/work/nabledge-dev-work1/.claude/skills/nabledge-6/plugin/CHANGELOG.md`

**Change**: Add `[Unreleased]` section at top (after line 6):

```markdown
## [Unreleased]

### Fixed
- Claude Code setup script now installs skill directly to `.claude/skills/` directory instead of using marketplace configuration, ensuring immediate recognition on first startup without restart required (Issue #27)

## [0.1] - 2026-02-16
```

**Note**: Per `.claude/rules/changelog.md`, only document changes affecting deployed content. This fix affects setup-6-cc.sh and GUIDE-CC.md (both deployed), so CHANGELOG update is required.

## Critical Files Reference

**Most Important Files**:

1. **scripts/setup-6-cc.sh** (lines 1-125) - Core fix, switch to direct copy
2. **scripts/setup-6-ghc.sh** (lines 18-41) - Pattern reference for git sparse-checkout
3. **.claude/rules/postmortem.md** (new) - Standard format for post-mortem
4. **.claude/skills/nabledge-6/plugin/GUIDE-CC.md** (lines 10-22, 59-82) - User documentation
5. **scripts/test-issue-27-reproduce.sh** (new) - Verification of fix

**Existing Patterns to Follow**:
- `.claude/rules/issues.md` - Structure and style for rules documentation
- `.claude/rules/work-log.md` - Format for work logs
- `work/20260216/update-workflow-branch-references.md` - Example work log

## Task Dependencies

**Sequential Order** (some parallelization possible):

```
Phase 1: Standards (MUST BE FIRST)
├─ 1.1 Create postmortem.md
└─ 1.2 Update issues.md

Phase 2: Horizontal Check
└─ 2.1 Create horizontal check (references Phase 1 standards)

Phase 3: Core Fix (can start after Phase 1)
├─ 3.1 Update setup-6-cc.sh [CRITICAL]
└─ 3.2 Update GUIDE-CC.md

Phase 4: Testing (depends on Phase 3)
├─ 4.1 Create test script (depends on 3.1)
└─ 4.2 Execute test (depends on 4.1)

Phase 5: Documentation (depends on all previous phases)
├─ 5.1 Create post-mortem (depends on 2.1, 4.2 results)
└─ 5.2 Create work log (depends on 5.1)

Phase 6: Final Verification (depends on all phases)
├─ 6.1 Verify Success Criteria
└─ 6.2 Update CHANGELOG
```

**Critical Path**: 1.1 → 1.2 → 3.1 → 4.1 → 4.2 → 5.1 → 6.1 → 6.2

**Can Be Parallel**:
- Tasks 1.1 and 1.2 (different files, no conflicts)
- Tasks 3.1 and 3.2 (different files)
- Task 2.1 can be done anytime after Phase 1 completes

## Key Design Decisions

### Direct Copy vs Marketplace

**Decision**: Use direct skill copy for Claude Code (same as GitHub Copilot)

**Rationale**:
- Proven pattern (setup-6-ghc.sh already works)
- Eliminates race condition completely
- Immediate recognition without restart
- Consistent approach across AI tools
- Not dependent on Claude Code's marketplace behavior

**Trade-offs**:
- Larger repo size (skill files committed)
- Manual updates needed (re-run setup for new versions)
- No automatic marketplace updates

### Standards First Approach

**Decision**: Create postmortem.md and update issues.md BEFORE writing documentation

**Rationale**:
- Ensures all documentation follows consistent format
- Template reminds implementer of required sections
- Reusable for future incidents
- Improves quality through standardization

### Separate Horizontal Check Document

**Decision**: Horizontal check as standalone document, referenced from post-mortem

**Rationale**:
- Contains detailed analysis (tables, findings)
- Can be referenced from multiple documents
- Easier to update status independently
- Separates "what went wrong" from "what else might be wrong"

## Verification

**How to verify plan is complete**:

1. **File existence**: All 8 files created/modified exist
2. **Test passes**: test-issue-27-reproduce.sh returns exit code 0
3. **Success criteria**: All 8 criteria from Issue #27 verified
4. **Documentation quality**: Post-mortem follows postmortem.md format
5. **Consistency**: setup-6-cc.sh matches setup-6-ghc.sh pattern (except VSCode config)

**Manual verification steps**:

1. Run test script on clean repository clone
2. Check GUIDE-CC.md has no marketplace references
3. Verify setup-6-cc.sh creates .claude/skills/nabledge-6/
4. Confirm SKILL.md exists in copied directory
5. Test: Clone fresh repo, run setup, verify `/nabledge-6` works immediately

## Risk Mitigation

**Risk**: Test script can't download old method from release branch
**Mitigation**: Test script skips old method test gracefully, new method test alone confirms fix

**Risk**: Direct copy incompatible with future CC versions
**Mitigation**: Document decision rationale, monitor CC releases, test script will catch regression

**Risk**: Team members have old settings.json
**Mitigation**: Old settings.json harmless (ignored if .claude/skills/ exists), document re-run in GUIDE

## Notes for Implementation

- All documentation in English except user-facing GUIDE-CC.md (Japanese)
- CHANGELOG is in Japanese (user-facing)
- No emojis unless explicitly requested
- Bash scripts use `${variable}` syntax for safety
- Test script preserves directories for manual inspection
- Exit codes: 0 success, 1 failure (CI-compatible)

## Success Definition

Implementation is complete when:
1. Test script passes (exit code 0)
2. All 8 Success Criteria verified
3. PR created with reference to Issue #27
4. All changes committed to feature branch
5. Ready for review and merge
