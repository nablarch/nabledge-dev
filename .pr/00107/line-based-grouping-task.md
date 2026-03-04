# Line-Based Grouping Task Specification

## Background

Current implementation (Section-Unit Split) creates 1,648 files from 334 RST files by splitting each h2 section into a separate file. This is inefficient for processing.

**Problem**: Small sections (78.8% are ≤50 lines) are not grouped together.

## Objective

Implement line-based grouping that combines multiple sections up to a threshold, reducing file count from 1,648 to ~408 files.

## Requirements

### R1. Unified Threshold

- **Single threshold value**: 400 lines
- Use for both:
  - H3 fallback (when h2 > 400 lines, split to h3)
  - Section grouping (combine sections up to 400 lines)

**Rationale**:
- Analysis shows 400-line threshold produces 408 files with max 31,143 tokens (~25.7 KB)
- Better balance than 500-line (max 40,312 tokens) or 300-line (458 files)

### R2. Grouping Algorithm

For each RST file with ≥2 h2 sections:

1. **Expand sections**:
   - If h2 ≤ 400 lines → keep as-is
   - If h2 > 400 lines → expand to h3 subsections
   - If no h3 exists → keep giant h2 with warning

2. **Group sections**:
   - Iterate expanded sections in order
   - Accumulate sections until total > 400 lines
   - When threshold exceeded, finalize current group and start new
   - Final group contains remaining sections

3. **Generate entries**:
   - Each group → 1 entry
   - `section_range.sections` = list of all section titles in group
   - Split ID format: `{base_id}--{start_section_id}` (use first section's ID)

### R3. Section Range Structure

Each split entry must have:

```json
{
  "section_range": {
    "start_line": 0,
    "end_line": 450,
    "sections": ["Section 1", "Section 2", "Section 3"]
  },
  "split_info": {
    "is_split": true,
    "part": 1,
    "total_parts": 3,
    "original_id": "libraries-tag",
    "group_line_count": 370
  }
}
```

### R4. Backward Compatibility

- Files with <2 h2 sections: no change (not split)
- Non-RST files: no change
- Existing test fixtures: update expectations to match new grouping

## Implementation

### Files to Modify

1. **steps/step2_classify.py**:
   - Change `H3_FALLBACK_THRESHOLD = 500` → `LINE_GROUP_THRESHOLD = 400`
   - Rewrite `split_file_entry()` to implement grouping algorithm
   - Add `group_line_count` to split_info

2. **tests/test_split_criteria.py**:
   - Update all test expectations
   - Add meaningful tests:
     - Small sections grouped together
     - Large section triggers h3 expansion and grouping
     - Boundary cases (exactly 400 lines, 401 lines)
     - Group covers all lines without gaps/overlaps
     - Multiple groups per file

3. **tests/test_e2e_split.py**:
   - Update expected file counts in E2E tests
   - Verify merged output is correct

## Test Requirements

### Meaningful Tests (Must Have)

1. **Grouping behavior**:
   - `test_small_sections_grouped`: 5 sections of 80 lines each → 1 group (400 lines)
   - `test_boundary_exactly_threshold`: 2 sections totaling exactly 400 lines → 1 group
   - `test_boundary_exceeds_threshold`: 3 sections (200+150+100) → 2 groups (200+150, 100)

2. **H3 fallback**:
   - `test_large_h2_with_h3_grouped`: h2 with 600 lines, 3 h3s → h3s grouped to 400-line chunks
   - `test_threshold_consistency`: Verify H3_FALLBACK and grouping use same value

3. **Coverage**:
   - `test_section_range_accuracy`: All groups cover all lines without gaps/overlaps
   - `test_multiple_groups_per_file`: File with 1200 lines → 3 groups

4. **Edge cases**:
   - `test_single_giant_section_no_h3`: 600-line h2 with no h3 → warning + kept as-is
   - `test_mixed_small_and_large`: File with small h2 + giant h2 → correct grouping

### Remove/Update Tests

- ~~`test_split_produces_one_entry_per_section`~~ → Update to test grouping
- ~~`test_h3_fallback_for_large_h2`~~ → Update expected counts
- Keep: ID format, deduplication, preamble inclusion tests

## Success Criteria

1. All tests pass (including updated expectations)
2. Run on ja RST files produces ~408 output files (±10%)
3. Max file size ≤ 31,000 tokens (~25 KB)
4. No gaps/overlaps in section_range coverage
5. Test coverage includes all meaningful scenarios

## Non-Goals

- Changing Phase B/C/D/E/F/G/M logic (they already handle split files correctly)
- Optimizing for exact 400 lines (greedy accumulation is fine)
- Cross-file grouping (each RST file processed independently)
