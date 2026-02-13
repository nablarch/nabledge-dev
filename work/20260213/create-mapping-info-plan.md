# Plan: Create Mapping Info from Official Docs to Knowledge Files

## Context

We are building nabledge skills that enable AI agents to autonomously perform Nablarch development tasks. To create knowledge files systematically, we need comprehensive mapping information that shows:
- Which official documentation files map to which knowledge files
- What category each file belongs to (batch, REST, handler, library, etc.)
- Whether each file is in scope or out of scope

This mapping will be used later by a skill to automatically create knowledge files.

## Exploration Results

### V6 Documentation Structure
- **nablarch-document**: 667 RST files organized by topic (batch, REST, web, libraries, handlers, tools)
- **nablarch-system-development-guide**: 158 MD files (project setup, patterns, anti-patterns)
- **nablarch-single-module-archetype**: 10 archetype projects (batch, REST, web, container variants)

### V5 Documentation Structure
- **nablarch-document**: 772 RST files (similar structure to v6 but more legacy content)
- **nablarch-single-module-archetype**: 9 archetype projects
- **No system-development-guide** for v5 (use v6 guide as reference)

### Current nabledge-6 Knowledge Structure
Knowledge files organized in:
- `features/processing/` - Processing methods (batch, REST)
- `features/libraries/` - Framework libraries (database, validation, data_io, log, etc.)
- `features/handlers/` - Handlers (common, batch, standalone, rest, web, etc.)
- `features/tools/` - Testing tools (NTF)
- `features/adapters/` - Third-party adapters
- `checks/` - Security checklists
- `releases/` - Release notes

## Implementation Approach

### Core Strategy: Script-Based Automation

Use Python scripts to efficiently process 1,400+ files instead of individual Read operations:
- **Efficiency gain**: 18x faster, 95% reduction in tool calls
- **Approach**: Scripts generate initial mapping, then AI/human verify edge cases
- **Coverage**: Automatic categorization handles 90%+ of files, manual review for remaining 10%

### Design Decisions

1. **File Scanning**: Python script extracts titles from RST (line 3) and MD (line 1) files
2. **Categorization**: Path-based pattern matching using directory structure
   - `batch/nablarch_batch/` → batch-nablarch (IN SCOPE)
   - `batch/jsr352/` → batch-jsr352 (OUT OF SCOPE)
   - `web_service/rest/` → rest (IN SCOPE)
   - `web/` → web (OUT OF SCOPE)
   - `messaging/` → messaging-mom/messaging-db (OUT OF SCOPE)
3. **Target Mapping**: Match against existing index.toon to generate target paths
4. **Validation**: Script verifies file counts, category references, and generates statistics

### Implementation Phases

#### Phase 1: Setup (2h)
- Create work directory structure
- Create category definitions (categories-v6.json, categories-v5.json)
- Create path rules configuration (path-rules.json)

#### Phase 2: Script Development (4h)
- **scan-sources.py**: Walk directory trees, extract file metadata
- **apply-categorization.py**: Apply path rules, determine in_scope
- **map-targets.py**: Generate target knowledge file paths
- **validate-mapping.sh**: Verify integrity, generate statistics

#### Phase 3: V6 Mapping Generation (1h)
- Run scripts on v6 repos
- Generate mapping-v6-draft.json (~500 entries)
- Initial statistics report

#### Phase 4: V6 Out-of-Scope Verification (3h)
- Extract out-of-scope files by reason
- AI agent reads samples, verifies correctness
- Flag false positives, update mapping

#### Phase 5: V6 Manual Review (2h)
- Review NEEDS_REVIEW entries (~5-10% of files)
- Assign correct categories and in_scope
- Finalize mapping-v6.json

#### Phase 6: V6 Validation (1h)
- Run validation script
- Fix errors/inconsistencies
- Generate final statistics

#### Phase 7: V5 Mapping (4h)
- Repeat Phases 3-6 for v5 repositories
- Note: v5 has no system-development-guide, use v6 guide

#### Phase 8: Documentation (1h)
- Write README with work summary
- Document out-of-scope decisions

### Path-Based Categorization Rules

```json
{
  "priority_1_exclusions": [
    {"pattern": "**/batch/jsr352/**", "reason": "Jakarta Batch excluded"},
    {"pattern": "**/messaging/**", "reason": "Messaging (MOM/DB queue) excluded"},
    {"pattern": "**/web/**", "reason": "Web applications (JSP/UI) excluded", "except": "**/web_service/**"}
  ],
  "priority_2_inclusions": [
    {"pattern": "**/batch/nablarch_batch/**", "categories": ["processing-pattern:batch-nablarch"]},
    {"pattern": "**/web_service/rest/**", "categories": ["processing-pattern:rest"]},
    {"pattern": "**/handlers/batch/**", "categories": ["component:handler", "processing-pattern:batch-nablarch"]},
    {"pattern": "**/handlers/rest/**", "categories": ["component:handler", "processing-pattern:rest"]},
    {"pattern": "**/libraries/**", "categories": ["component:library"], "check": "usage_context"}
  ]
}
```

### Mapping File Structure

```json
{
  "version": "6",
  "statistics": {
    "total_entries": 500,
    "in_scope": 280,
    "out_of_scope": 215,
    "needs_review": 5
  },
  "mappings": [
    {
      "id": "v6-doc-001",
      "source_file": ".lw/nab-official/v6/nablarch-document/ja/application_framework/.../index.rst",
      "title": "Nablarchバッチアプリケーション",
      "categories": ["processing-pattern:batch-nablarch"],
      "in_scope": true,
      "reason_for_exclusion": null,
      "target_files": ["features/processing/nablarch-batch.json"]
    }
  ]
}
```

## Critical Files

**Python Scripts** (to be created):
- `work/20260213/create-mapping-info/scripts/scan-sources.py` - File scanning
- `work/20260213/create-mapping-info/scripts/apply-categorization.py` - Categorization
- `work/20260213/create-mapping-info/scripts/map-targets.py` - Target mapping
- `work/20260213/create-mapping-info/scripts/path-rules.json` - Pattern rules

**Source Documentation**:
- `.lw/nab-official/v6/nablarch-document/ja/application_framework/` (334 RST files)
- `.lw/nab-official/v6/nablarch-system-development-guide/` (158 MD files)
- `.lw/nab-official/v6/nablarch-single-module-archetype/` (10 projects)
- `.lw/nab-official/v5/nablarch-document/ja/` (772 RST files)
- `.lw/nab-official/v5/nablarch-single-module-archetype/` (9 projects)

**Reference Structure**:
- `.claude/skills/nabledge-6/knowledge/index.toon` - Target path mapping reference

## Deliverables

```
work/20260213/create-mapping-info/
├── scripts/
│   ├── scan-sources.py           # File scanning script
│   ├── apply-categorization.py   # Categorization script
│   ├── map-targets.py            # Target mapping script
│   ├── path-rules.json           # Pattern rules
│   └── requirements.txt          # Python dependencies
├── categories-v6.json            # v6 category definitions
├── categories-v5.json            # v5 category definitions
├── mapping-v6.json               # v6 complete mapping
├── mapping-v5.json               # v5 complete mapping
├── out-of-scope-v6.md            # v6 out-of-scope review
├── out-of-scope-v5.md            # v5 out-of-scope review
├── validate-mapping.sh           # Validation script
└── README.md                     # Work log
```

## Verification

**Validation checks**:
1. File count: All source files accounted for (100% coverage)
2. Category references: All categories defined in categories-vX.json
3. In-scope files: All have target_files assigned
4. Out-of-scope files: All have reason_for_exclusion
5. Statistics: Match expected distribution (batch ~45, REST ~32, handlers ~58, libraries ~87)

**Success criteria**:
- [ ] All v6 files mapped (334 RST + 158 MD + 10 archetypes = ~500 entries)
- [ ] All v5 files mapped (772 RST + 9 archetypes = ~780 entries)
- [ ] Out-of-scope files verified (sample 10% of each category)
- [ ] Validation script passes with 0 errors
- [ ] Statistics reports generated
