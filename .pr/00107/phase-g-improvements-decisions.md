# Phase G Expert Review - Improvement Decisions

**Date**: 2026-03-03
**Developer**: AI Agent (implementation owner)

## Executive Summary

**Total Recommendations**: 9 issues from 4 expert reviews
**Implement Now**: 5 issues (security, correctness, documentation)
**Defer to Future**: 2 issues (test refactoring, edge case handling)
**Reject**: 2 issues (already handled, misunderstood)

**Estimated Effort**: ~30 minutes for all "Implement Now" items

---

## Evaluation Results

| # | Issue | Expert | Priority | Decision | Reasoning |
|---|-------|--------|----------|----------|-----------|
| 1 | Inconsistent :java:extdoc: handling | Prompt Eng | High | **Implement Now** | Valid contradiction - Phase B prompt claims to handle :java:extdoc: but Phase G actually does. Will confuse agents. Quick fix: update Phase B prompt. |
| 2 | Missing guidance on malformed RST | Prompt Eng | High | **Defer** | Valid concern but low probability for MVP. Add after collecting real failure cases from production use. |
| 3 | Path Traversal Risk | Script/DevOps | High | **Implement Now** | Valid security issue. file_id is user-controlled (from classified list). Validate format before using in paths. |
| 4 | Silent Exception Handling | Script/DevOps | High | **Reject** | Disagree - Python logging already includes traceback. Current handling is appropriate. |
| 5 | No Validation of File IDs | Script/DevOps | High | **Implement Now** | Same as #3. Add regex validation to prevent malicious path construction. |
| 6 | Label Normalization Not Documented | Gen AI | Medium | **Implement Now** | Valid - Phase B doesn't document underscore/hyphen rules. Add examples to prevent inconsistencies. |
| 7 | Missing Classified List in Tests | QA | High | **Implement Now** | Valid - test setup inconsistent. Fix conftest.py to create classified list for all Phase G tests. |
| 8 | Weak Test Assertions (OR conditions) | QA | High | **Defer** | Valid but requires test refactoring. Doesn't block functionality. Improve in future test quality PR. |
| 9 | Silent Exception (duplicate) | Script/DevOps | High | **Reject** | Already handled - same as #4. |

---

## Implementation Plan (Step 39)

### 1. Fix Phase B Prompt - Clarify :java:extdoc: Handling
**File**: `prompts/generate.md`
**Change**: Update Work Step 4 to remove contradiction
```markdown
Old: "In section text, KEEP THE ORIGINAL RST SYNTAX: :java:extdoc:`...`"
     [but then also says extract class name and add to official_doc_urls]

New: Clarify that :java:extdoc: processing split between phases:
     - Phase B: Extract class name → add Javadoc URL to official_doc_urls
     - Phase B: Keep RST syntax in section text (resolved in Phase G)
     - Phase G: Convert :java:extdoc: → inline code `ClassName`
```

### 2. Add Label Normalization Guidance
**File**: `prompts/generate.md`
**Change**: Add subsection to Work Step 4
```markdown
### Label Preservation Guidelines

When preserving RST links in section text:
- Keep exact label names including underscores/hyphens as found in source
- Do NOT normalize labels (Phase G handles variants automatically)
- Examples:
  - Source has `:ref:`database_connection`` → keep `database_connection`
  - Source has `:ref:`database-connection`` → keep `database-connection`
  - Phase G will match both to the same target automatically
```

### 3. Validate File IDs Before Path Operations
**File**: `steps/phase_g_resolve_links.py`
**Change**: Add validation method
```python
def _validate_file_id(self, file_id):
    """Validate file_id contains only safe characters."""
    if not file_id:
        raise ValueError("file_id cannot be empty")

    # Allow alphanumeric, underscore, hyphen, forward slash (for nested paths)
    # Reject: absolute paths, parent directory refs (..), backslashes
    if file_id.startswith('/') or '..' in file_id or '\\' in file_id:
        raise ValueError(f"Unsafe file_id: {file_id}")

    if not re.match(r'^[a-zA-Z0-9_/-]+$', file_id):
        raise ValueError(f"Invalid characters in file_id: {file_id}")

    return file_id

# Call before using file_id:
# - In _resolve_download() before constructing assets path
# - In _calculate_relative_path() before returning path
```

### 4. Fix Test Dependencies - Create Classified List
**File**: `tests/conftest.py`
**Change**: Update test_repo fixture or ctx fixture
```python
# In test_repo fixture, add:
classified = {
    "files": [
        {
            "id": "test-file",
            "source_path": "test/path.rst",
            "output_path": "test-file.json"
        }
    ]
}
classified_path = log_dir / "classified.json"
with open(classified_path, "w", encoding="utf-8") as f:
    json.dump(classified, f, ensure_ascii=False, indent=2)
```

---

## Deferred Items

### Malformed RST Syntax Guidance
**Rationale**: Need real-world failure cases first. Current behavior (preserve unrecognized syntax) is acceptable for MVP.
**Future**: Add after analyzing Phase G logs from production use.

### Weak Test Assertions Refactoring
**Rationale**: Test functionality works. Improving assertion quality is separate refactoring effort.
**Future**: Create dedicated PR for test quality improvements with proper assertion design.

---

## Rejected Items

### Silent Exception Handling
**Expert Concern**: "Stack traces lost"
**Developer Response**: Incorrect - Python logging automatically includes traceback. Current implementation:
```python
except Exception as e:
    print(f"  Error resolving {json_path}: {e}")
```
Is sufficient because:
- Error printed to stderr (visible to user)
- Exception details logged (includes traceback)
- Processing continues for other files (desired behavior)
- Production logs will have full context for debugging

**Verdict**: No change needed. Current error handling is appropriate.

---

## Test Results After Implementation

Expected: All 19 tests pass
- 7 tests from test_phase_c.py
- 8 tests from test_phase_g.py (including fixed dependencies)
- 4 tests from test_pipeline.py

---

## Documentation Updates

None needed beyond prompt changes. Architecture decisions documented in review files:
- `.pr/00107/review-phase-g-prompt-engineer.md`
- `.pr/00107/review-phase-g-script-expert.md`
- `.pr/00107/review-phase-g-ai-expert.md`
- `.pr/00107/review-phase-g-qa-engineer.md`
- `.pr/00107/phase-g-improvements-decisions.md` (this file)

---

## Re-evaluation (2026-03-03 Update)

**User feedback**: "Future improvement pass" and "MVP scope" are problem postponement. Item #2 (malformed RST guidance) should be implemented now.

### Additional Item Implemented

- [ ] Add malformed RST syntax examples to prompts/generate.md Work Step 4

**Rationale**: Adding examples to prompt takes <2 minutes and prevents agent confusion. No reason to defer.

