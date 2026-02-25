# Issue #78: Tasks for Success Criteria Achievement

**Issue**: As a nabledge developer, I want automated knowledge creation and validation skill so that future Nablarch releases can be handled reproducibly

**Success Criteria**:
- [ ] SC1: Nablarch v6 knowledge files are created accurately from official sources
- [ ] SC2: Multiple executions produce consistent, reproducible results

**Critical Understanding**:
- **Goal**: Develop a reusable **skill** (not just generate data)
- **Test**: Skill must work for v6 AND v5 (proves "reproducible for future versions")
- **Method**: All work executed via `/nabledge-creator` skill commands

---

## Phase 1: Mapping Workflow ✅ COMPLETE

**Skill Command**: `/nabledge-creator mapping`

### Task 1.1: Implement mapping workflow ✅
- [x] Design mapping workflow (workflows/mapping.md)
- [x] Implement generate-mapping.py
- [x] Implement validate-mapping.py
- [x] Test: Execute `/nabledge-creator mapping` successfully

**Result**: 291 files mapped, 0 errors

### Task 1.2: Verify mapping reproducibility ✅
- [x] Execute `/nabledge-creator mapping` 5 times
- [x] Compare outputs with MD5 checksums
- [x] Document in phase1-reproducibility-test.md

**Result**: 5/5 runs byte-identical (MD5: `11ea4a7e9b732312ceaee82ffa3720b2`)

**Evidence**: `.pr/00078/phase1-reproducibility-test.md`

**Phase 1 Status**: ✅ **COMPLETE** - Skill produces perfect reproducibility

---

## Phase 2: Index Workflow ✅ COMPLETE

**Skill Command**: `/nabledge-creator index`

### Task 2.1: Implement index workflow ✅
- [x] Design index schema (references/index-schema.md)
- [x] Design workflow (workflows/index.md)
- [x] Implement generate-index.py
- [x] Test: Execute `/nabledge-creator index` successfully

**Result**: 259 entries, all validations passed

### Task 2.2: Verify index reproducibility ✅
- [x] Execute `/nabledge-creator index` 5 times
- [x] Compare outputs with MD5 checksums
- [x] Document in phase2-reproducibility-test.md

**Result**: 5/5 runs byte-identical (MD5: `2cfc12cdd6f0c8127c757e99de007c78`)

**Evidence**: `.pr/00078/phase2-reproducibility-test.md`

**Phase 2 Status**: ✅ **COMPLETE** - Skill produces perfect reproducibility

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

# Validate
cd .claude/skills/nabledge-creator
python scripts/validate-knowledge.py ../nabledge-6/knowledge/

# Record: errors, warnings, time
# Backup: cp -r knowledge/ .tmp/phase5-run{N}/
```

**Success Criteria**:
- [ ] Run 1: 0 errors via skill
- [ ] Run 2: 0 errors via skill
- [ ] Run 3: 0 errors via skill
- [ ] Consistent quality across runs
- [ ] Skill command works without intervention

**Estimated Time**: 6-9 hours (3 runs × 2-3 hours per run)

### Task 5.3: v5 Compatibility Test ⏳ CRITICAL

**Purpose**: Prove skill works for future Nablarch versions (SC2 requirement)

**Method**: Apply skill to v5 documentation

```bash
# Generate v5 mapping
/nabledge-creator mapping --version v5

# Generate sample v5 knowledge files (5-10 files)
/nabledge-creator knowledge --version v5 --sample 10

# Validate
cd .claude/skills/nabledge-creator
python scripts/validate-knowledge.py ../nabledge-5/knowledge/

# Expect: Skill works with v5 sources
```

**Success Criteria**:
- [ ] Skill executes for v5 without errors
- [ ] v5 mapping generated successfully
- [ ] Sample v5 knowledge files generated
- [ ] 0 validation errors on v5 files
- [ ] **Proves**: "Reproducible for future Nablarch releases"

**Critical**: This proves SC2 ("future Nablarch releases can be handled reproducibly")

**Estimated Time**: 2-3 hours

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

### SC1: Nablarch v6 knowledge files are created accurately ⏳

**Requirements**:
- [ ] ✅ All 162 files generated (Phase 4)
- [ ] ⏳ Via skill command (Phase 4.2 pending)
- [ ] ⏳ Content accuracy verified (Phase 5.1 pending)
- [ ] ✅ 0 validation errors
- [ ] ✅ All categories covered

**Status**: 60% complete (generation done, skill execution pending)

### SC2: Multiple executions produce consistent, reproducible results ⏳

**Requirements**:
- [ ] ✅ Script-based: Perfect reproducibility (Phases 1-2)
- [ ] ⏳ Skill-based: Reproducibility at scale (Phase 5.2 pending)
- [ ] ⏳ Future versions: Works for v5 (Phase 5.3 pending)
- [ ] ⏳ Documentation: Complete skill docs (Phase 5.4 pending)

**Status**: 40% complete (script proven, skill pending)

**Critical Gap**:
- Generated 162 files via Task tool ❌
- Must regenerate via skill to prove reproducibility ✅

---

## Summary

| Phase | Method | Status | Critical Issue |
|-------|--------|--------|----------------|
| **Phase 1: Mapping** | ✅ Skill | ✅ Complete | None |
| **Phase 2: Index** | ✅ Skill | ✅ Complete | None |
| **Phase 3: Pilot (17)** | ❌ Task tool | ⚠️ Invalid | **Must use skill** |
| **Phase 4: Complete (162)** | ❌ Task tool | ⚠️ Invalid | **Must use skill** |
| **Phase 5.1: Verify** | - | ⏳ Pending | Workflow not implemented |
| **Phase 5.2: Reproduce** | - | ⏳ Pending | Need skill-based generation |
| **Phase 5.3: v5 test** | - | ⏳ Pending | Critical for SC2 |

**Critical Path**:
1. **Phase 4.2**: Regenerate 162 files via skill (2-3h) ← **START HERE**
2. **Phase 5.1**: Implement & run content verification (2-3h)
3. **Phase 5.2**: Run 3 reproducibility tests via skill (6-9h)
4. **Phase 5.3**: Verify v5 compatibility (2-3h)

**Total Time to SC Achievement**: 12-18 hours

**Key Insight**:
- Issue #78 is about **skill development**, not **data generation**
- Current 162 files are test outputs, not proof of skill quality
- Must demonstrate skill works via `/nabledge-creator` commands
- v5 compatibility test is CRITICAL for "future Nablarch releases"

---

## Next Immediate Action

**Phase 4.2: Regenerate all files via skill**

```bash
# Backup current Task-generated files
cp -r .claude/skills/nabledge-6/knowledge/ .tmp/phase4-taskgen-backup/

# Regenerate via skill
rm -rf .claude/skills/nabledge-6/knowledge/*.json
/nabledge-creator knowledge --all

# If skill works → Prove skill is ready
# If skill fails → Fix skill and retry
```

This is the foundation for all subsequent phases.
