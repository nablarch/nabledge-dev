# Tasks: RBKC Feasibility Investigations

**PR**: #298
**Issue**: #297
**Updated**: 2026-04-10

## Not Started

### v6 Investigations (run scripts against `.lw/nab-official/v6/nablarch-document/ja/`)

All 10 v6 investigations must complete before implementation starts. Each task follows the same pattern:
1. Write a Python/bash script in `.tmp/rbkc-investigation/` or run inline
2. Record results in `.pr/00297/investigation-items.md` under the corresponding "I-XX 結果" section
3. Determine handling policy from results

#### I-01: RST directive full inventory

**Steps:**
- [ ] Script: extract all `.. directive_name::` patterns from 413 RST files, count occurrences
- [ ] Classify: README-covered vs uncovered directives
- [ ] Decide: policy for each uncovered directive (add rule / exclude / no-content)
- [ ] Record in investigation-items.md

#### I-02: RST heading symbol patterns

**Steps:**
- [ ] Script: extract all heading underline/overline patterns, count per symbol
- [ ] Check: overline usage count; h4+ (4+ level) files count
- [ ] Decide: policy for overline and deep headings
- [ ] Record in investigation-items.md

#### I-03: Cross-reference resolution scope

**Steps:**
- [ ] Script: extract all `.. _label:` definitions and `:ref:` usages
- [ ] Count: total labels, total refs, unresolvable refs (defined outside scan scope)
- [ ] Decide: policy for unresolved refs (text / error / skip)
- [ ] Record in investigation-items.md

#### I-04: RST table complex cases

**Steps:**
- [ ] Script: extract list-table usages, check for non-standard options
- [ ] Script: find grid tables (`+----+`) and simple tables (`==== ====`)
- [ ] Check: empty cells, multi-row cells, merged cells in real examples
- [ ] Decide: fallback policy for Markdown-incompatible cases
- [ ] Record in investigation-items.md

#### I-05: No-knowledge-content file candidates

**Steps:**
- [ ] Script: apply detection logic (short file / no meaningful content / index-only etc.)
- [ ] Check: candidate count and false-positive rate against manual sample
- [ ] Decide: refine detection logic if needed
- [ ] Record in investigation-items.md

#### I-06: ID collision cases

**Steps:**
- [ ] Script: simulate ID generation algorithm across all 413 files
- [ ] Check: any remaining collisions after deduplication suffix logic
- [ ] Decide: algorithm adjustment if collisions remain
- [ ] Record in investigation-items.md

#### I-07: Excel file structure (v6, 5 files)

**Steps:**
- [ ] Inspect: open/parse each of the 5 .xlsx files in `.lw/nab-official/v6/`
- [ ] Check: column names, sheet structure vs README assumptions
- [ ] Decide: any column mapping adjustments needed
- [ ] Record in investigation-items.md

#### I-08: MD source files (v6, 3 files)

**Steps:**
- [ ] Read: inspect each of the 3 .md files in `.lw/nab-official/v6/`
- [ ] Check: any special syntax (MDX, custom directives, frontmatter, etc.)
- [ ] Decide: additional handling rules if needed
- [ ] Record in investigation-items.md

#### I-09: Hints Stage 2 match rate

**Steps:**
- [ ] Script: for each section title in v6, attempt Stage 2 match against hint data
- [ ] Measure: match rate (% of sections that get Stage 2 hints)
- [ ] Decide: if match rate < threshold, drop Stage 2 or use fallback strategy
- [ ] Record in investigation-items.md

#### I-12: TOON format spec

**Steps:**
- [ ] Read: analyze existing `index.toon` file to understand format
- [ ] Check: all structural elements needed, can generation logic be implemented
- [ ] Decide: generation algorithm
- [ ] Record in investigation-items.md

### v5 Investigation (after all v6 complete)

#### I-10: v5 RST full-dimension diff

**Steps:**
- [ ] Re-run I-01 through I-09/I-12 scripts against v5 source
- [ ] Compare results to v6 results, identify differences
- [ ] Estimate additional implementation scope for v5-specific cases
- [ ] Record in investigation-items.md

### v1.x Investigations (independent of v6/v5)

#### I-11: v1.4 RST full-dimension investigation

**Steps:**
- [ ] Run I-01 through I-09 equivalent scripts against v1.4 source (`.lw/nab-official/v1.4/`)
- [ ] Extra: inspect .xls (old format) file structure vs .xlsx
- [ ] Note: separate lineage from v5/v6, document all differences
- [ ] Record in investigation-items.md

#### I-13: v1.3 RST diff (against v1.4)

**Steps:**
- [ ] Run scripts against v1.3, compare to v1.4 results
- [ ] Document dimensions that differ
- [ ] Record in investigation-items.md

#### I-14: v1.2 RST diff (against v1.3)

**Steps:**
- [ ] Run scripts against v1.2, compare to v1.3 results
- [ ] Document dimensions that differ
- [ ] Record in investigation-items.md

## Done

- [x] Place RBKC design draft (`tools/rbkc/README.md`)
- [x] Place pre-implementation evaluation results (`search-impact.md`, `section-granularity.md`)
- [x] Enumerate all design elements as specs, derive investigation items (`.pr/00297/investigation-items.md`)
- [x] Add "detail files via link" guideline to `work-notes.md` rule
- [x] Expert review (Technical Writer, 4/5)
- [x] All investigations complete (I-01 through I-14)
- [x] Update RBKC README with investigation findings (directive table, grid table rowspan, Stage 2 via .cache, multi-version support, Excel structure)
- [x] Create implementation issue #299
