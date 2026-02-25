# Issue #78: Tasks for Success Criteria Achievement

**Issue**: As a nabledge developer, I want automated knowledge creation and validation skill so that future Nablarch releases can be handled reproducibly

**Success Criteria**:
- [ ] SC1: Nablarch v6 knowledge files are created accurately from official sources
- [ ] SC2: Multiple executions produce consistent, reproducible results

**Critical Understanding**:
- **Goal**: Develop a reusable **skill** (not just generate data)
- **Test**: Skill must work for v6 AND v5 (proves "reproducible for future versions")
- **Method**: All work executed via `/nabledge-creator` skill commands

**Quality Requirements (Mission-Critical System Level)**:
- **No sampling**: Full validation of all 162 files (not 10-15 samples)
- **No script execution**: All verification via `/nabledge-creator` skill commands
- **No guessing**: Definitive proof that skill works correctly
- **Rationale**: Knowledge files support systems handling hundreds of billions of yen

---

## Phase 0: Skill Understanding & Verification Plan ⏳ START HERE

**Purpose**: Accurately understand what the nabledge-creator skill does before executing verification

**Critical Issue**: Previous work proceeded with incomplete understanding of skill behavior, leading to incorrect verification approach (script execution instead of skill execution).

### Task 0.1: Read and understand skill specifications ✅

**Files to read**:
1. `.claude/skills/nabledge-creator/SKILL.md` - Skill interface and commands
2. `.claude/skills/nabledge-creator/workflows/mapping.md` - Mapping workflow definition
3. `.claude/skills/nabledge-creator/workflows/index.md` - Index workflow definition
4. `.claude/skills/nabledge-creator/workflows/knowledge.md` - Knowledge workflow definition
5. `.claude/skills/nabledge-creator/scripts/generate-mapping.py` - What mapping script does
6. `.claude/skills/nabledge-creator/scripts/generate-index.py` - What index script does
7. `.claude/skills/nabledge-creator/scripts/validate-knowledge.py` - Validation logic

**Questions answered** ✅:
- `/nabledge-creator mapping`: Executes 6-step workflow (generate → assign PP → validate → export → resolve → checklist)
- `/nabledge-creator index`: Executes 5-step workflow (generate → verify → validate → test → commit)
- `/nabledge-creator knowledge`: Executes 5-step workflow (identify → generate → convert → validate → checklist)
- Arguments: mapping/index (none), knowledge (--filter, --limit, --all)
- Skill vs Script: Skill = complete workflow with validation and edge case handling; Script = single step execution

### Task 0.2: Understand execution strategy ✅

**Understanding confirmed**:

1. **Phase 1-2 Strategy** ✅
   - Execute via `/nabledge-creator mapping` and `/nabledge-creator index`
   - NOT via `python scripts/*.py` (proves skill works, not just scripts)
   - 5 runs each for reproducibility verification
   - Expected: 291 files (mapping), 154 entries (index)

2. **Phase 3-4 Strategy** ✅
   - Execute via `/nabledge-creator knowledge --all`
   - NOT via Task tool or script execution
   - All 162 files generated via skill
   - 3 runs for reproducibility testing

3. **Phase 5 Quality Assurance Strategy** ✅
   - Task 5.1: Implement `/nabledge-creator verify-knowledge --all` workflow
   - **All 162 files verified** (not sampling)
   - Task 5.2: 3 full runs for reproducibility
   - Task 5.3: v5 compatibility (critical for SC2)

**Phase 0 Status**: ✅ **COMPLETE** (0.1 ✅ 0.2 ✅)

---

## Phase 1: Mapping Workflow ❌ NEEDS SKILL-BASED EXECUTION

**Skill Command**: `/nabledge-creator mapping`

### Task 1.1: Implement mapping workflow ✅
- [x] Design mapping workflow (workflows/mapping.md)
- [x] Implement generate-mapping.py
- [x] Implement validate-mapping.py
- [x] Scripts tested and working

**Result**: Scripts work correctly

### Task 1.2: Execute mapping via skill command ⏳ REQUIRED

**Previous Work (INVALID)**:
- Used `python scripts/generate-mapping.py v6` directly
- See `.pr/00078/phase1-reproducibility-test.md:32`
- This proves **script works**, not **skill works**

**Required Work**:
Execute via skill command 5 times:

```bash
# Run 1-5
/nabledge-creator mapping

# Validate
cd .claude/skills/nabledge-creator
python scripts/validate-mapping.py output/mapping-v6.md

# Compare
md5sum output/mapping-v6.md

# Backup
cp output/mapping-v6.md .tmp/phase1-skill-run{N}/
```

**Success Criteria**:
- [ ] 5 runs executed via `/nabledge-creator mapping` skill command
- [ ] All runs produce identical output (MD5 match)
- [ ] 0 validation errors
- [ ] Document results in phase1-skill-reproducibility.md

**Phase 1 Status**: ❌ **INVALID** - Used script directly, not skill

---

## Phase 2: Index Workflow ❌ NEEDS SKILL-BASED EXECUTION

**Skill Command**: `/nabledge-creator index`

### Task 2.1: Implement index workflow ✅
- [x] Design index schema (references/index-schema.md)
- [x] Design workflow (workflows/index.md)
- [x] Implement generate-index.py
- [x] Scripts tested and working

**Result**: Scripts work correctly

### Task 2.2: Execute index via skill command ⏳ REQUIRED

**Previous Work (INVALID)**:
- Used `python scripts/generate-index.py v6` directly
- See `.pr/00078/phase2-reproducibility-test.md:32`
- This proves **script works**, not **skill works**

**Required Work**:
Execute via skill command 5 times:

```bash
# Run 1-5
/nabledge-creator index

# Validate
ls -la .claude/skills/nabledge-6/knowledge/index.toon

# Compare
md5sum .claude/skills/nabledge-6/knowledge/index.toon

# Backup
cp .claude/skills/nabledge-6/knowledge/index.toon .tmp/phase2-skill-run{N}/
```

**Success Criteria**:
- [ ] 5 runs executed via `/nabledge-creator index` skill command
- [ ] All runs produce identical output (MD5 match)
- [ ] 259 entries in index.toon
- [ ] Document results in phase2-skill-reproducibility.md

**Phase 2 Status**: ❌ **INVALID** - Used script directly, not skill

---

## Phase 3: Knowledge Workflow (Pilot) ⚠️ NEEDS SKILL-BASED EXECUTION

**Skill Command**: `/nabledge-creator knowledge --filter "pilot=true"`

### Task 3.1: Implement knowledge workflow ✅
- [x] Design knowledge schema (references/knowledge-schema.md)
- [x] Design workflow (workflows/knowledge.md)
- [x] Implement validate-knowledge.py
- [x] Document generation patterns

**Result**: Schema and validation ready

### Task 3.2: Generate pilot files (17 files) ⚠️ NOT SKILL-BASED

**Current Status**: 17 files generated via Task tool (not skill execution)

**Problem**:
- ❌ Used Task tool directly instead of skill
- ❌ Cannot verify skill works correctly
- ❌ Not reproducible via skill command

### Task 3.3: Execute via skill and verify reproducibility ⏳ REQUIRED

**Method**: Use nabledge-creator skill (not Task tool)

For each run (1-3):
```bash
# Delete pilot files
rm -rf .claude/skills/nabledge-6/knowledge/*.json

# Execute skill
/nabledge-creator knowledge --filter "pilot=true" --files 17

# Validate
cd .claude/skills/nabledge-creator
python scripts/validate-knowledge.py ../nabledge-6/knowledge/

# Expect: 0 errors, 17 files

# Backup
mkdir -p .tmp/phase3-skill-run{N}
cp -r .claude/skills/nabledge-6/knowledge/ .tmp/phase3-skill-run{N}/
```

**Success Criteria**:
- [ ] Run 1: 0 errors, 17 files (via skill)
- [ ] Run 2: 0 errors, 17 files (via skill)
- [ ] Run 3: 0 errors, 17 files (via skill)
- [ ] Skill command executes without manual intervention

**Phase 3 Status**: ⚠️ **INCOMPLETE** - Must execute via skill

---

## Phase 4: Knowledge Workflow (Complete) ⚠️ NOT SKILL-BASED

**Skill Command**: `/nabledge-creator knowledge --all`

### Task 4.1: Current generation status ⚠️

**What was done**:
- 162 files generated via Task tool
- 0 validation errors
- All categories covered

**Problem**:
- ❌ Generated via Task tool, not skill
- ❌ Cannot reproduce via skill command
- ❌ Skill workflow not proven at scale

### Task 4.2: Regenerate via skill ⏳ REQUIRED

**Method**: Use nabledge-creator skill to generate all files

```bash
# Backup current files
cp -r .claude/skills/nabledge-6/knowledge/ .tmp/phase4-taskgen-backup/

# Delete and regenerate via skill
rm -rf .claude/skills/nabledge-6/knowledge/*.json

# Execute skill for all categories
/nabledge-creator knowledge --all

# Validate
cd .claude/skills/nabledge-creator
python scripts/validate-knowledge.py ../nabledge-6/knowledge/

# Expect: 0 errors, 162 files
```

**Success Criteria**:
- [ ] Skill generates all 162 files
- [ ] 0 validation errors
- [ ] Execution time recorded
- [ ] No manual intervention required

**Phase 4 Status**: ⚠️ **INCOMPLETE** - Must execute via skill

---

## Phase 5: Skill Quality Assurance ⏳ NEXT

**Goal**: Verify skill works correctly and is ready for v5

### Task 5.1: Content Accuracy Verification ⏳

**Skill Command**: `/nabledge-creator verify-knowledge --all`

**Purpose**: Verify generated files accurately reflect RST source content

**What skill does**:
1. Read knowledge-file-plan.md (source RST mapping)
2. For each of 162 files:
   - Read source RST from `.lw/nab-official/v6/`
   - Read generated JSON
   - Verify per knowledge-schema.md rules:
     - Section division (RST h2 → JSON sections, ±30%)
     - Mandatory fields (class_name, purpose, etc.)
     - L1/L2 keywords (minimum: L1≥1, L2≥2)
     - Category template compliance
     - Content correspondence
3. Report issues

**Implementation**:
- [ ] Create workflow: `workflows/verify-content-accuracy.md`
- [ ] Update SKILL.md with verification command
- [ ] Test: Execute `/nabledge-creator verify-knowledge --all`
- [ ] Output: `.pr/00078/phase5-content-accuracy-report.md`

**Success Criteria**:
- [ ] Skill executes verification automatically
- [ ] All 162 files pass verification
- [ ] 0 critical issues (missing fields, wrong structure)
- [ ] Report clearly lists any issues found

**Estimated Time**: 2-3 hours (skill development + execution)

### Task 5.2: Process Reproducibility at Scale ⏳

**Purpose**: Verify skill produces consistent results at full scale

**Method**: Execute skill 3 times for all 162 files

For each run (1-3):
```bash
# Clean slate
rm -rf .claude/skills/nabledge-6/knowledge/*.json
rm -f .claude/skills/nabledge-6/knowledge/index.toon

# Execute skill workflows
/nabledge-creator index
/nabledge-creator knowledge --all

# Verify via skill (not script directly)
/nabledge-creator verify-knowledge --all

# Record: errors, warnings, time
# Backup: cp -r .claude/skills/nabledge-6/knowledge/ .tmp/phase5-run{N}/
```

**Success Criteria**:
- [ ] Run 1: 0 errors via skill verification
- [ ] Run 2: 0 errors via skill verification
- [ ] Run 3: 0 errors via skill verification
- [ ] Consistent quality across runs (±10% warning count acceptable)
- [ ] Skill command works without intervention

**Estimated Time**: 9-12 hours (3 runs × 3-4 hours per run including verification)

### Task 5.3: v5 Compatibility Test ⏳ CRITICAL

**Purpose**: Prove skill works for future Nablarch versions (SC2 requirement)

**Method**: Apply skill to v5 documentation with representative coverage

```bash
# Generate v5 mapping (full)
/nabledge-creator mapping --version v5

# Generate v5 knowledge files (major categories, ~30-50 files)
/nabledge-creator knowledge --version v5 --filter "Category IN (handlers,libraries,processing)"

# Verify via skill (not script)
/nabledge-creator verify-knowledge --version v5 --all
```

**Success Criteria**:
- [ ] Skill executes for v5 without errors
- [ ] v5 mapping generated successfully (full coverage)
- [ ] Major categories knowledge files generated (30-50 files minimum)
- [ ] 0 validation errors on v5 files via skill verification
- [ ] **Proves**: "Reproducible for future Nablarch releases"

**Critical**: This proves SC2 ("future Nablarch releases can be handled reproducibly")

**Note**: Not full 162 files for v5, but sufficient coverage across categories to prove reproducibility

**Estimated Time**: 3-4 hours

### Task 5.4: Skill Documentation ⏳

**Purpose**: Document skill usage for future users

- [ ] Update SKILL.md with complete examples
- [ ] Document all workflow commands
- [ ] Add troubleshooting section
- [ ] Create quick start guide

**Success Criteria**:
- [ ] Another developer can use skill without assistance
- [ ] All commands documented with examples
- [ ] Clear error messages and solutions

---

## Phase 6: Final Verification ⏳

### Task 6.1: End-to-end skill test

**Purpose**: Verify complete skill workflow from scratch

```bash
# Start fresh
rm -rf .claude/skills/nabledge-6/knowledge/
rm -f .claude/skills/nabledge-creator/output/mapping-v6.md

# Execute complete workflow via skill
/nabledge-creator mapping
/nabledge-creator index
/nabledge-creator knowledge --all
/nabledge-creator verify-knowledge --all

# Expect: Complete knowledge base with 0 errors
```

**Success Criteria**:
- [ ] Complete workflow executes via skill commands
- [ ] 162 files generated, 0 errors
- [ ] Content verification passes
- [ ] No manual intervention needed

### Task 6.2: Skill package verification

**Purpose**: Verify skill is ready for deployment

- [ ] All workflows in `.claude/skills/nabledge-creator/workflows/` complete
- [ ] All scripts tested and working
- [ ] SKILL.md complete and accurate
- [ ] References documentation complete
- [ ] Example outputs documented

---

## Success Criteria Final Check

### SC1: Nablarch v6 knowledge files are created accurately ❌

**Requirements**:
- [ ] ❌ All 162 files generated via skill (Phase 4 pending)
- [ ] ❌ Content accuracy verified via `/nabledge-creator verify-knowledge --all` (Phase 5.1 pending)
  - **All 162 files verified** (not sampling)
  - Automated RST↔JSON correspondence check
  - Schema compliance verification
- [ ] ❌ 0 validation errors via skill execution
- [ ] ❌ All categories covered via skill

**Status**: 0% complete (previous work invalid - used Task tool, not skill)

### SC2: Multiple executions produce consistent, reproducible results ❌

**Requirements**:
- [ ] ❌ Mapping reproducibility via skill (Phase 1 pending)
- [ ] ❌ Index reproducibility via skill (Phase 2 pending)
- [ ] ❌ Knowledge reproducibility via skill (Phase 5.2 pending)
- [ ] ❌ Future versions: Works for v5 (Phase 5.3 pending)
- [ ] ❌ Documentation: Complete skill docs (Phase 5.4 pending)

**Status**: 0% complete (previous work invalid - used scripts directly, not skill)

**Critical Gap**:
- All previous work used scripts/Task tool directly ❌
- This proves scripts work, NOT that skill works ❌
- Must restart from Phase 0 with correct understanding ✅

---

## Summary

| Phase | Method | Status | Critical Issue |
|-------|--------|--------|----------------|
| **Phase 0: Skill Understanding** | - | ✅ **COMPLETE** | Understanding confirmed |
| **Phase 1: Mapping** | ❌ Script direct | ❌ Invalid | **Must use skill** |
| **Phase 2: Index** | ❌ Script direct | ❌ Invalid | **Must use skill** |
| **Phase 3: Pilot (17)** | ❌ Task tool | ❌ Invalid | **Must use skill** |
| **Phase 4: Complete (162)** | ❌ Task tool | ❌ Invalid | **Must use skill** |
| **Phase 5.1: Verify** | - | ⏳ Pending | Workflow implementation required |
| **Phase 5.2: Reproduce** | - | ⏳ Pending | Need skill-based generation |
| **Phase 5.3: v5 test** | - | ⏳ Pending | Critical for SC2 |

**Critical Path**:
1. **Phase 0**: ✅ Complete - Skill specifications understood
2. **Phase 1**: Execute mapping via skill with 5-run reproducibility (1h) ← **NEXT**
3. **Phase 2**: Execute index via skill with 5-run reproducibility (1h)
4. **Phase 3**: Execute pilot knowledge files via skill (1h)
5. **Phase 4**: Execute all 162 knowledge files via skill (3-4h)
6. **Phase 5**: Quality assurance and v5 compatibility (15-20h including verification workflow)

**Total Time to SC Achievement**: 21-28 hours (increased due to full verification requirements)

**Key Insight**:
- Issue #78 is about **skill development**, not **data generation**
- Previous work used scripts/Task tool directly - this is INVALID
- Must start from Phase 0: accurately understand what skill does
- All subsequent phases must use `/nabledge-creator` skill commands
- v5 compatibility test is CRITICAL for "future Nablarch releases"

---

## Next Immediate Action

**Phase 1: Execute mapping workflow via skill**

Execute 5 runs of `/nabledge-creator mapping` to verify:
1. Skill command works (not script direct execution)
2. Reproducibility (5 runs produce identical results)
3. Output: 291 files mapped, 0 review items

Then proceed to Phase 2 (index) → Phase 3 (pilot) → Phase 4 (full) → Phase 5 (QA with verification workflow implementation).
