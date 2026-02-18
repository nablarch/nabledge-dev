# Mapping Creation System Design

**Version**: 5.0 (Design Document)
**Purpose**: Design documentation for Nablarch official documentation to knowledge file mapping system

---

## Overview

### Purpose

Create a JSON mapping file that links Nablarch official documentation to target knowledge files. This mapping drives the automated generation of structured knowledge files for the nabledge AI assistant.

### Architecture

```
Input Sources
├── nablarch-document (main docs, EN/JA)
├── nablarch-system-development-guide (patterns, v6 only)
└── categories-v{version}.json (category definitions)
                    ↓
        Processing Pipeline (5 Scripts)
                    ↓
├── Step 1-3: create-mapping-v6.py
│   └── Path-based categorization (component, setup, about)
├── Step 4: categorize-ai-judgment-v6.py
│   └── Content-based categorization (AI judgment)
├── Step 5: verify-patterns-v6.py
│   └── Processing pattern verification (7 patterns)
├── Step 6-10: finalize-mapping-v6.py
│   └── Target names, titles, validation
└── Step 11: export-to-excel-v6.py
    └── Excel export for review
                    ↓
              Output Files
├── mapping-v6.json (final mapping)
├── mapping-v6.json.stats.txt (statistics)
└── mapping-v6.json.xlsx (Excel review)
```

### Key Design Decisions

**Why 5 separate scripts instead of one monolithic script?**
1. **Incremental processing**: Each step produces intermediate output for inspection
2. **Resumability**: Can restart from any step if issues found
3. **Maintainability**: Clear separation of concerns (path rules vs content analysis vs validation)
4. **Debugging**: Easy to isolate issues to specific step

**Why 11 steps?**
- Logical progression: discover → categorize → verify → finalize → validate → export
- Different data sources processed separately (dev guide vs nab-doc)
- Validation as distinct phase before output

---

## Source Documentation Structure

### Three Documentation Sources

1. **nablarch-document** (main documentation)
   - EN/JA language variants (English priority)
   - RST, MD, XML formats
   - Structure: `/handlers/`, `/libraries/`, `/batch/`, `/web/`, etc.

2. **nablarch-system-development-guide** (development guide)
   - Japanese only
   - Patterns and anti-patterns
   - Security matrix
   - **v5 note**: No v5-specific guide; uses v6 guide

3. **nablarch-*-archetype** (Maven archetypes)
   - **Excluded from mapping** (code, not documentation)

### Language Priority

**English over Japanese**: When both `/en/` and `/ja/` versions exist, English is used.

**Rationale**: English documentation is more complete and suitable for AI processing. Japanese documentation may have translation inconsistencies or be outdated.

---

## Categorization Strategy

### Three-Phase Approach

```
Phase 1: Rule-Based (Step 3)
         ↓ (path patterns)
    Component, Setup, About categories
         ↓
Phase 2: AI Judgment (Step 4)
         ↓ (content keywords)
    Remaining files categorized
         ↓
Phase 3: Pattern Verification (Step 5)
         ↓ (full content inspection)
    7 processing patterns added
```

**Why this order?**

1. **Rule-based first (Step 3)**: Fast, deterministic for obvious cases
   - Path `/handlers/` → clearly "handler" category
   - No content reading needed for structural categories

2. **AI judgment second (Step 4)**: Handles ambiguous cases
   - Files without clear path patterns
   - Requires content reading but not full analysis

3. **Pattern verification last (Step 5)**: Comprehensive check
   - Processing patterns often can't be inferred from path
   - Handler in `/handlers/web/` needs content check to confirm "web" pattern
   - Libraries may support multiple patterns (validation in batch, web, REST)

**Why process patterns separately?**
- **Path ambiguity**: `/handlers/` doesn't tell if it's for batch, web, or REST
- **Multiple patterns**: Validation library applies to batch-nablarch, web, and rest
- **Content dependency**: Keywords like "JSP", "JAX-RS" distinguish patterns
- **Critical for filtering**: Processing patterns determine when knowledge appears in retrieval

---

## Category System

### Category Types (5 Types, 21 Categories)

**Source**: `doc/mapping-creation/categories-v{version}.json`

```json
{
  "type": "processing-pattern",  // 7 patterns
  "type": "component",            // 5 components
  "type": "setup",                // 2 setup types
  "type": "guide",                // 3 guide types
  "type": "about"                 // 2 about types
}
```

#### Processing Patterns (7)
Critical for knowledge retrieval filtering:
- `batch-nablarch`: Nablarch batch (FILE to DB, DB to DB, DB to FILE)
- `batch-jsr352`: Jakarta Batch (JSR 352)
- `rest`: RESTful web services (JAX-RS)
- `http-messaging`: HTTP-based system messaging
- `web`: Web applications (JSP/UI)
- `messaging-mom`: MOM messaging (JMS)
- `messaging-db`: DB messaging / resident batch

#### Components (5)
Framework building blocks:
- `handler`: Request handlers
- `library`: Framework libraries
- `adaptor`: Third-party integration
- `tool`: Development tools
- `security-check`: Security features

#### Setup (2)
Project initialization:
- `setup`: Project setup, blank projects
- `configuration`: Configuration guides

#### Guide (3)
Development guidance:
- `dev-guide-pattern`: Recommended patterns
- `dev-guide-anti`: Anti-patterns to avoid
- `dev-guide-other`: Other guidance

#### About (2)
Meta-documentation:
- `about`: Framework overview, concepts
- `migration`: Version migration guides

### Multiple Categories Philosophy

**Rule**: A file can have multiple categories.

**Common patterns**:
- Component + Pattern(s): `["handler", "web"]` (web handler)
- Component + Multiple Patterns: `["library", "batch-nablarch", "web", "rest"]` (validation library)
- Component + Security: `["library", "security-check"]` (authorization library)

**Limits**:
- **Typical**: 1-3 categories per file
- **Warning**: 4+ categories may indicate over-categorization
- **Exception**: Common libraries legitimately span many patterns

**Rationale**:
- Components serve multiple patterns (handlers, libraries)
- Processing patterns filter knowledge retrieval ("show me REST docs")
- Granular categorization improves relevance

---

## Key Decision Rules

### Step 3: Path Pattern Matching

**Scope**: Non-processing-pattern categories only (component, setup, about)

**High-Level Logic**:
```
/handlers/**        → handler
/libraries/**       → library
/adaptors/**        → adaptor
/development_tools/ → tool
/blank_project/     → setup
/about_nablarch/    → about
/migration/         → migration
```

**Special case**: `/libraries/authorization/` → `["library", "security-check"]`

**Implementation**: See `categorize_by_path()` in `create-mapping-v6.py` (L214-256)

**Rationale**: Path structure reveals architectural role but not processing pattern.

---

### Step 4: Content-Based Categorization

**For files without clear path patterns.**

**Navigation-Only Detection**:
```
toctree count > 0 AND code blocks = 0 AND words < 50
  → mark as _no_content
```

**Rationale**: Navigation files don't provide technical content; marking prevents empty knowledge files.

**Technical Indicators** (9 categories):
```
handler:        "Handler", "HandlerQueue", "request processing"
library:        "library", "repository", "utility"
security-check: "authentication", "authorization", "CSRF", "XSS"
setup:          "blank project", "getting started"
configuration:  "configuration", "settings", "properties"
about:          "overview", "introduction", "concept"
```

**Default**: If no indicators found → `["about"]` (low confidence flag)

**Implementation**: See `categorize_by_content()` in `categorize-ai-judgment-v6.py` (L105-163)

**Rationale**: Keyword matching provides sufficient signal for high-level categories. Full NLP unnecessary.

---

### Step 5: Processing Pattern Verification

**Critical step**: Verifies all 7 processing patterns through full content inspection.

**Why necessary?**
- File paths often ambiguous for patterns
- Component files may support multiple patterns
- Content inspection is the only reliable method

**Assignment Logic**:

✅ **Assign pattern when**:
1. **Primary focus**: Title/headings reference pattern, code examples for pattern
2. **Explicit scope**: "This handler is used in batch/web/REST applications"
3. **Pattern-specific examples**: "Example for Jakarta Batch application:"

❌ **Do NOT assign when**:
- Pattern mentioned in passing: "Unlike batch processing, web applications..."
- Comparison table without detailed coverage
- Brief mention without implementation details

**Technical Indicators** (7 patterns):

```
batch-nablarch:  "Nablarch batch", "FILE to DB", "NablarchBatchlet"
batch-jsr352:    "JSR 352", "Jakarta Batch", "ItemReader", "@BatchProperty"
rest:            "JAX-RS", "@Path", "@GET", "REST API", "BodyConverter"
http-messaging:  "HTTP messaging", "HTTP send", "MessagingProvider"
web:             "JSP", "HTML form", "HttpRequest", "SessionStore"
messaging-mom:   "MOM", "JMS", "MessageSender", "message queue"
messaging-db:    "resident batch", "DB messaging", "database polling"
```

**Special case**: REST vs HTTP-messaging disambiguation
- Count keyword occurrences
- Keep both if roughly equal frequency
- Drop one if significantly lower

**Implementation**: See `get_processing_patterns()` in `verify-patterns-v6.py` (L68-141)

**Rationale**: Processing patterns determine knowledge retrieval filtering. Must be accurate and complete.

---

### Step 6: Target File Name Generation

#### Category Priority Order

**5-tier hierarchy for determining target directory**:

```
Tier 1: Processing patterns (alphabetical)
  batch-jsr352, batch-nablarch, http-messaging, messaging-db,
  messaging-mom, rest, web

Tier 2: Components (alphabetical)
  adaptor, handler, library, security-check, tool

Tier 3: Setup (alphabetical)
  configuration, setup

Tier 4: Guide (alphabetical)
  dev-guide-anti, dev-guide-other, dev-guide-pattern

Tier 5: About (alphabetical)
  about, migration
```

**Rationale**:
- Processing patterns are most specific → highest priority
- Components are structural → second priority
- Setup/Guide/About are meta → lower priority
- Within tier, alphabetical for consistency

**Example**: File with `["handler", "web"]`
- Both categories present
- Tier 1 (web) beats Tier 2 (handler)
- Target directory: `features/web/`
- But if `["handler", "library"]`, handler wins (both Tier 2, alphabetical)

#### Conflict Resolution

**3-strategy precedence** (preserves semantic meaning):

1. **Category prefix** - Distinguish by primary category
   - `config.json` → `handler-config.json` (if different categories)
   - Preserves category context

2. **Parent directory prefix** - Distinguish by source structure
   - `overview.json` → `batch-overview.json` (from `/batch/`)
   - Preserves source organization

3. **Numeric suffix** - Last resort for identical contexts
   - `config.json` → `config-2.json`
   - Only when category and parent are identical

**Rationale**: Prefer semantic disambiguation over arbitrary numbering. Users can understand file purpose without consulting mapping.

**Implementation**: See `resolve_conflict()` in `finalize-mapping-v6.py` (L150-194)

#### Generic Names

**Require parent directory prefix**:
```
index, overview, main, introduction, readme,
summary, guide, concepts, getting-started
```

**Example**: `index.rst` in `/batch/` → `batch-index.json`

**Rationale**: Generic names lack context. Parent directory makes meaning clear.

---

## Validation Strategy

### Five Validation Checks (Step 9)

All executed before writing output:

#### 9.1: No Duplicate Targets
- Check all `target_files` for duplicates
- Error with list of duplicates if found

#### 9.2: Schema Compliance
- Required fields: id, source_file, title, categories
- Either target_files OR _no_content required
- ID format: `v{version}-{0000}`
- Target format: lowercase, .json extension, no underscores

#### 9.3: Category Validation
- All category IDs must exist in `categories-v{version}.json`
- Error with invalid category IDs

#### 9.4: Source File Existence
- All source files must exist on filesystem
- Error with missing file list

#### 9.5: Target Path Consistency
- All targets must start with `features/` or `guides/`
- Error with invalid paths

**Rationale**: Fail fast before output. Validation errors caught early prevent downstream issues in knowledge generation.

**Implementation**: See `validate_mapping()` in `finalize-mapping-v6.py` (L381-488)

---

## Example Mappings

### Example 1: Batch-Specific Handler

```json
{
  "id": "v6-0087",
  "source_file": "nablarch-document/en/application_framework/application_framework/handlers/batch/nablarch_batch/BatchActionHandler.rst",
  "title": "Batch Action Handler",
  "categories": ["handler", "batch-nablarch"],
  "target_files": ["features/handler/batch-action-handler.json"]
}
```

**Categorization path**:
1. Step 3: `/handlers/batch/` → `["handler"]` (path pattern)
2. Step 5: Content contains "Nablarch batch", "ExecutionContext" → add `["batch-nablarch"]`
3. Result: `["handler", "batch-nablarch"]`

**Target directory**:
- Primary category: "handler" (Tier 2)
- Directory: `features/handler/`
- Filename: `batch-action-handler.json` (from source name)

---

### Example 2: Multi-Pattern Library

```json
{
  "id": "v6-0123",
  "source_file": "nablarch-document/en/application_framework/application_framework/libraries/validation.rst",
  "title": "Validation",
  "categories": ["library", "batch-nablarch", "web", "rest"],
  "target_files": ["features/library/validation.json"]
}
```

**Why multiple patterns?**
- Content explicitly states: "Validation is used in batch, web, and REST applications"
- Code examples for all three patterns
- Configuration examples for batch, web, REST

**Categorization path**:
1. Step 3: `/libraries/` → `["library"]`
2. Step 5: Content inspection finds all three patterns → add `["batch-nablarch", "web", "rest"]`

**Target directory**:
- Primary category: "library" (Tier 2, beats patterns in alphabetical)
- Directory: `features/library/`

**Knowledge retrieval**: This file appears when filtering by batch-nablarch, web, OR rest.

---

### Example 3: Navigation-Only File

```json
{
  "id": "v6-0005",
  "source_file": "nablarch-document/en/application_framework/application_framework/index.rst",
  "title": "Application Framework",
  "categories": ["about"],
  "_no_content": true,
  "_no_content_reason": "Navigation only (toctree without technical content)"
}
```

**Detection**:
- File contains only `.. toctree::` directive
- No code examples, < 50 words
- Marked as navigation-only in Step 4

**Why marked?**
- Prevents creation of empty knowledge file
- Navigation structure doesn't provide technical information
- Still tracked in mapping for completeness

---

### Example 4: Security Library with Pattern

```json
{
  "id": "v6-0156",
  "source_file": "nablarch-document/en/application_framework/application_framework/libraries/authorization/authorization.rst",
  "title": "Authorization Check",
  "categories": ["library", "security-check", "web"],
  "target_files": ["features/library/authorization.json"]
}
```

**Triple categorization**:
1. Step 3: `/libraries/authorization/` → `["library", "security-check"]` (special rule)
2. Step 5: Content shows web-specific usage → add `["web"]`

**Why "web" pattern?**
- Authorization primarily for web applications
- Examples use HttpRequest, SessionStore
- Not applicable to batch processing

---

## Error Handling Philosophy

### Encoding Strategy

**UTF-8 first, Shift-JIS fallback**:
- Japanese documentation may use Shift-JIS
- Try UTF-8, catch UnicodeDecodeError, retry Shift-JIS
- Mark as unreadable only if both fail

**Implementation**: All file reading functions have this fallback.

### Empty and Unreadable Files

**Empty files**:
- Detected in Step 2 (file validation)
- Marked as `_no_content` with reason "Empty file"
- Assigned default `["about"]` category

**Unreadable files**:
- Encoding errors after UTF-8/Shift-JIS attempts
- Binary files accidentally included
- Marked as `_no_content` with reason "Unreadable: {error}"

**Rationale**: Graceful degradation. Don't fail entire process for individual file issues.

### Navigation-Only Detection

**Indicators**:
- Only toctree directives (RST)
- Only bullet lists with links
- < 50 words of prose
- No code examples

**Why 50 words?**
- Short summaries < 50 words are likely just navigation headers
- Technical content typically > 100 words
- Threshold balances false positives/negatives

### Validation Failures

**Fail fast approach**:
- Run all 5 validations before writing output
- First validation error stops execution
- Clear error messages with examples

**Rationale**: Better to catch issues early than generate invalid mapping.

---

## Version-Specific Handling

### v6 (Nablarch 6)
- Full development guide available
- Uses v6 source: `.lw/nab-official/v6/`
- All patterns supported

### v5 (Nablarch 5)
- **No v5-specific development guide**
- Uses v6 development guide (path adjustment in script)
- Nab-doc structure may differ slightly
- Path patterns may need verification

**Implementation**: Version detection in `create-mapping-v6.py` (L100-115)

---

## Execution

### Running All Steps

```bash
./doc/mapping-creation/work-v6/run-all-v6.sh
```

**Prerequisites**:
- Python 3.7+
- openpyxl library (`pip install openpyxl`)

**Output**:
- `mapping-v6.json` (final mapping)
- `mapping-v6.json.stats.txt` (statistics)
- `mapping-v6.json.xlsx` (Excel review file)

### Intermediate Files

```
work-v6/
├── needs-ai-judgment-v6.json       # After Step 3
├── categorized-ai-files-v6.json    # After Step 4
└── pattern-verified-v6.json        # After Step 5
```

**Purpose**: Allow inspection and restart from any step if issues found.

### Individual Step Execution

```bash
python3 doc/mapping-creation/work-v6/create-mapping-v6.py
python3 doc/mapping-creation/work-v6/categorize-ai-judgment-v6.py
python3 doc/mapping-creation/work-v6/verify-patterns-v6.py
python3 doc/mapping-creation/work-v6/finalize-mapping-v6.py
python3 doc/mapping-creation/work-v6/export-to-excel-v6.py
```

---

## Output Schema

```json
{
  "schema_version": "1.0",
  "version": "6",
  "created_at": "2026-02-18T10:30:00+09:00",
  "mappings": [
    {
      "id": "v6-0001",
      "source_file": "nablarch-document/en/path/to/doc.rst",
      "title": "Document Title",
      "categories": ["category-id-1", "category-id-2"],
      "target_files": ["features/directory/filename.json"]
    }
  ]
}
```

**For navigation-only files**:
```json
{
  "id": "v6-0002",
  "source_file": "nablarch-document/en/path/to/nav.rst",
  "title": "Navigation Document",
  "categories": ["about"],
  "_no_content": true,
  "_no_content_reason": "Navigation only (toctree without technical content)"
}
```

---

## Implementation References

**Path pattern rules**: `create-mapping-v6.py` lines 214-256
**Category keywords**: `categorize-ai-judgment-v6.py` lines 27-37
**Processing pattern keywords**: `verify-patterns-v6.py` lines 29-65
**Category priority**: `finalize-mapping-v6.py` lines 36-48
**Directory mapping**: `finalize-mapping-v6.py` lines 50-72
**Conflict resolution**: `finalize-mapping-v6.py` lines 150-194
**Validation**: `finalize-mapping-v6.py` lines 381-488

---

## Design Rationale Summary

### Why This Architecture?

1. **Incremental processing**: Catch issues early, restart from any step
2. **Separation of concerns**: Path rules ≠ content analysis ≠ pattern verification
3. **Rule-based first**: Fast, deterministic for obvious cases
4. **AI judgment for ambiguity**: Keyword matching sufficient for high-level categories
5. **Pattern verification last**: Only processing patterns need full content inspection
6. **Multiple categories**: Reflects reality (components serve multiple patterns)
7. **Priority tiers**: Deterministic conflict resolution, preserves semantic meaning
8. **Fail fast validation**: Better to catch errors before output

### Trade-offs Accepted

**Redundant processing**: Step 5 re-reads files already categorized in Steps 3-4
- **Why accepted**: Processing patterns can't be inferred from paths or simple keywords
- **Alternative considered**: Single-pass full analysis → rejected (too slow, harder to debug)

**Keyword-based matching**: Not full NLP/semantic analysis
- **Why accepted**: Sufficient signal-to-noise ratio, faster, more maintainable
- **Alternative considered**: LLM-based categorization → rejected (cost, consistency issues)

**Hardcoded keywords**: Not machine-learned
- **Why accepted**: Nablarch vocabulary is stable, manual curation ensures accuracy
- **Alternative considered**: TF-IDF/embeddings → rejected (over-engineering for this domain)

---

**End of Design Document**
