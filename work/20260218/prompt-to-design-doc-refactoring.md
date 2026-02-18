# Prompt to Design Document Refactoring

**Date**: 2026-02-18
**Related Issue**: #10 (Create mapping info from official documentation)

---

## Summary

Refactored 1,420-line implementation prompt to 463-line design document based on prompt engineering evaluation.

**Reduction**: 70% smaller (1,420 → 463 lines)
**Focus shift**: Implementation details → Design rationale

---

## Changes Made

### Deleted
- **`doc/mapping-creation/archive/mapping-creation-prompt-v4.0-full.md`** (1,420 lines)
  - Full implementation prompt with pseudocode
  - 70-80% redundant after script implementation
  - Available in Git history if needed

### Created
- **`doc/mapping-creation/mapping-creation-design.md`** (463 lines, v5.0)
  - Design rationale and philosophy
  - High-level logic with script references
  - Key decision rules and examples

---

## Content Comparison

### Old Prompt (v4.0, 1,420 lines)

**Structure**:
- Prerequisites (50 lines)
- Preparation (30 lines)
- Step 1-11 detailed procedures (1,100 lines)
- Example mappings (120 lines)
- Output schema (50 lines)
- Notes (70 lines)

**Focus**: 60% implementation, 20% design, 20% specifications

**Issues**:
- Pseudocode duplicates actual code
- Hard to find design rationale
- Mixes abstraction levels
- Too long for onboarding

---

### New Design Doc (v5.0, 463 lines)

**Structure**:
1. **Overview** (40 lines)
   - Purpose, architecture diagram, key decisions

2. **Source Documentation** (35 lines)
   - Three sources, language priority, rationale

3. **Categorization Strategy** (80 lines)
   - Three-phase approach with rationale
   - Why this order? Why separate patterns?

4. **Category System** (110 lines)
   - 5 types, 21 categories
   - Multiple categories philosophy

5. **Key Decision Rules** (120 lines)
   - Path patterns (summary + script ref)
   - Content categorization (logic + script ref)
   - Pattern verification (why + how)
   - Target name generation (priority + conflict)

6. **Validation Strategy** (25 lines)
   - Five checks with rationale

7. **Example Mappings** (50 lines)
   - Four examples with explanation

8. **Error Handling Philosophy** (30 lines)
   - Encoding, empty files, validation

9. **Version Handling** (15 lines)
   - v5 vs v6 differences

10. **Execution** (20 lines)
    - Running scripts, intermediate files

11. **Output Schema** (20 lines)
    - JSON structure

12. **Implementation References** (10 lines)
    - Direct links to script line numbers

13. **Design Rationale Summary** (50 lines)
    - Why this architecture?
    - Trade-offs accepted

**Focus**: 50% design rationale, 30% high-level logic, 20% examples

---

## What Was Removed

### 1. Implementation Pseudocode (709 lines, 50%)

**Removed**:
- Step 3 path pattern implementation (L260-326)
- Step 4 content categorization code (L433-494)
- Step 5 pattern detection code (L548-633)
- Step 6 target name generation code (L652-822)
- Step 7 title extraction code (L829-900)
- Step 8 JSON building code (L906-954)
- Step 9 validation code (L959-1058)
- Step 10 output writing code (L1063-1131)
- Step 11 Excel export code (L1139-1186)

**Replacement**: Script references with line numbers

**Example**:
```markdown
❌ Old (60 lines of pseudocode):
def categorize_by_path(file_path: str) -> list[str]:
    categories = []
    norm_path = file_path.lower()
    if '/handlers/' in norm_path:
        categories.append('handler')
    [... 50 more lines ...]
    return categories

✅ New (5 lines + reference):
**Implementation**: See `categorize_by_path()` in
`create-mapping-v6.py` (L214-256)

**High-level logic**:
/handlers/** → handler
/libraries/** → library
[... summary only ...]
```

---

### 2. Over-Detailed Procedures (284 lines, 20%)

**Simplified**:
- Step 1 procedure (L69-162) → 2 paragraphs
- Navigation detection (L363-399) → Core logic + reference
- Conflict resolution code (L761-821) → Rationale + 3 strategies

**Example**:
```markdown
❌ Old (60 lines):
#### 6.4: Handle Conflicts (Apply in Order)

If target name already exists, apply strategies **in this order**:

1. **Add category prefix**:
   ```python
   new_name = f"{primary_category}-{name}.json"
   ```
   Only use if the primary categories differ...

2. **Add parent directory prefix**:
   ```python
   parent_dir = source_path.split('/')[-2]
   new_name = f"{parent_dir}-{name}.json"
   ```
   Use parent directory name...

3. **Add numeric suffix**:
   ```python
   counter = 2
   while f"{name}-{counter}.json" in existing_targets:
       counter += 1
   ```

✅ New (12 lines):
**3-strategy precedence** (preserves semantic meaning):

1. **Category prefix** - Distinguish by primary category
2. **Parent directory prefix** - Distinguish by source structure
3. **Numeric suffix** - Last resort for identical contexts

**Rationale**: Prefer semantic disambiguation over arbitrary
numbering. Users can understand file purpose without consulting
mapping.

**Implementation**: See `resolve_conflict()` in
finalize-mapping-v6.py (L150-194)
```

---

### 3. Redundant Examples (70 lines)

**Reduced**: 6 examples → 4 examples
- Removed redundant "simple handler" (covered by batch-specific)
- Removed redundant "dev guide pattern" (structure obvious)
- Kept complex cases: multi-pattern library, navigation-only, security

---

## What Was Enhanced

### 1. Architecture Diagram (NEW, 25 lines)

```
Input Sources → Processing Pipeline (5 Scripts) → Output Files
```

Visual representation of data flow.

---

### 2. Design Rationale (NEW, 100 lines)

**Added sections**:
- Why 5 scripts instead of monolithic?
- Why 11 steps?
- Why three-phase categorization?
- Why process patterns separately?
- Trade-offs accepted

**Example**:
```markdown
### Why This Architecture?

1. **Incremental processing**: Catch issues early, restart from any step
2. **Separation of concerns**: Path rules ≠ content analysis ≠ pattern verification
3. **Rule-based first**: Fast, deterministic for obvious cases

### Trade-offs Accepted

**Redundant processing**: Step 5 re-reads files already categorized
- **Why accepted**: Processing patterns can't be inferred from paths
- **Alternative considered**: Single-pass → rejected (too slow, harder to debug)
```

---

### 3. Implementation References (NEW, 10 lines)

Direct links to script functions with line numbers:
```markdown
**Path pattern rules**: `create-mapping-v6.py` lines 214-256
**Category keywords**: `categorize-ai-judgment-v6.py` lines 27-37
**Processing pattern keywords**: `verify-patterns-v6.py` lines 29-65
```

**Purpose**: Quick navigation from design to implementation.

---

### 4. Multiple Categories Philosophy (ENHANCED, 30 lines)

**Old**: Scattered mentions
**New**: Dedicated section with:
- Common patterns
- Limits (1-3 typical, 4+ warning)
- Rationale for granular categorization

---

## Benefits of New Structure

### For Understanding Design (6 months later)

✅ **Clear rationale**: Why decisions were made
✅ **Trade-offs**: What alternatives were considered
✅ **Philosophy**: Multiple categories, priority tiers
✅ **Quick navigation**: Script references with line numbers

❌ **Old prompt**: Buried in implementation details

---

### For Modifying Code

✅ **Design context**: Understand impact before changing
✅ **Script references**: Find implementation quickly
✅ **Examples**: See expected behavior

❌ **Old prompt**: Had to read both prompt and script

---

### For Onboarding

✅ **Digestible**: 463 lines vs 1,420 lines
✅ **Focused**: Design and rationale, not implementation
✅ **Examples**: 4 complex cases with explanation

❌ **Old prompt**: Too long, mixed abstraction levels

---

## Validation

### Alignment Check

**Question**: Does design doc accurately reflect implementation?

**Answer**: Yes, verified by prompt engineer evaluation:
- Path patterns match script (L214-256)
- Keywords match script dictionaries
- Priority order matches script (L36-48)
- Validation checks match script (L381-488)

### Completeness Check

**Question**: Is anything important missing?

**Answer**: No major gaps:
- All key decisions explained
- All categories covered
- All steps referenced
- Error handling philosophy documented

---

## Git History Note

**Full v4.0 prompt available in Git history**:
```bash
git show HEAD~1:doc/mapping-creation/mapping-creation-prompt.md
```

**When to reference old prompt**:
- Need exact pseudocode for reference
- Debugging edge case behavior
- Understanding historical context

---

## Success Criteria

- ✅ 70% size reduction (1,420 → 463 lines)
- ✅ Focus on "why" not "how" (50% rationale vs 20%)
- ✅ Design doc accurately reflects implementation
- ✅ Script references with line numbers
- ✅ Examples for complex cases
- ✅ Trade-offs and alternatives documented
- ✅ Onboarding-friendly length
- ✅ Old prompt available in Git history

---

## Next Steps

1. **Test execution**: Verify scripts still work (no changes to scripts)
2. **Review design doc**: Check for clarity and completeness
3. **Update references**: If anyone references old prompt file

---

## Lessons Learned

1. **Prompt serves different purposes at different stages**:
   - Development: Detailed specification needed
   - Production: Design rationale more valuable

2. **Redundancy accumulates**:
   - Pseudocode → Code → Both exist → Maintenance burden

3. **Design docs age better than implementation docs**:
   - "Why" remains relevant
   - "How" becomes outdated as code evolves

4. **Git makes archiving unnecessary**:
   - History is preserved
   - Don't need separate archive directories

5. **Script comments + design doc > mega-prompt**:
   - Code documents "how" (with comments)
   - Design doc documents "why"
   - No duplication
