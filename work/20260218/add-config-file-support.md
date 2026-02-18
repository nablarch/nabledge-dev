# Add Support for .config and config.txt Files

**Date**: 2026-02-18
**Task**: Extend mapping scripts to collect critical file types (.config, .txt)

## Background

User identified missing critical files in the mapping collection:
1. **Published API definition files** (`.config`) - 90 files per version (180 total)
2. **Archetype README.md** - Setup instructions for archetype projects
3. **JSP static analysis config** (`config.txt`) - Configuration files

These files are essential for:
- `check-published-api` category: Public API definitions
- `archetype` category: Project setup instructions
- `tool` category: Static analysis tool configurations

## Changes Made

### 1. Phase 2: File Collection (02-collect-files.sh)

Added new file type collection:

```bash
# For v6 and v5
find "$ARCHETYPE" -path "*/spotbugs/published-config/*.config" 2>/dev/null || true
find "$ARCHETYPE" -path "*/jspanalysis/config.txt" 2>/dev/null || true
find "$DOCS" -name "config.txt" 2>/dev/null || true
```

Added statistics output:
```bash
echo "  - .config: $(grep '\.config$' "$WORK_DIR/files-v6-all.txt" | wc -l)"
echo "  - .txt: $(grep '\.txt$' "$WORK_DIR/files-v6-all.txt" | wc -l)"
```

### 2. Phase 3: Filtering (03-filter-language.sh)

Added new filtering rules:

```bash
config)
    # Include only .config from spotbugs/published-config directory
    if echo "$file" | grep -q "spotbugs/published-config"; then
        include=true
    fi
    ;;
txt)
    # Include only config.txt from jspanalysis or toolbox directories
    if echo "$file" | grep -Eq "(jspanalysis|JspStaticAnalysis)/config\.txt$"; then
        include=true
    fi
    ;;
```

Extended .md filtering:
```bash
md)
    # Include .md from development guide OR archetype README.md
    if echo "$file" | grep -q "nablarch-system-development-guide" || \
       echo "$file" | grep -Eq "nablarch-single-module-archetype/.*/README\.md$"; then
        include=true
    fi
    ;;
```

Updated selection rules documentation and statistics output.

### 3. Documentation (mapping-creation-procedure.md)

Updated Phase 2 description:
- Added `.config` and `.txt` to file type list
- Added detailed explanation of each file type

Updated Phase 3 filtering rules:
- Added `.config` filtering rule
- Added `.txt` filtering rule
- Updated `.md` rule to include archetype README.md

## Test Results

### Collection Results (Phase 2)

**Nablarch v6**:
- Total files: 942 (was 848)
- .rst: 667
- .md: 170
- .xml: 11
- .config: 90 ✅ (new)
- .txt: 4 ✅ (new)

**Nablarch v5**:
- Total files: 889 (was 795)
- .rst: 772
- .md: 12
- .xml: 11
- .config: 90 ✅ (new)
- .txt: 4 ✅ (new)

### Filtering Results (Phase 3)

**Nablarch v6**:
- After filtering: 605 files (was 503)
- .rst: 336
- .md: 167 (includes 9 archetype README.md)
- .xml: 9
- .config: 90 ✅
- .txt: 3 ✅

**Nablarch v5**:
- After filtering: 544 files (was 442)
- .rst: 433
- .md: 9 (includes 9 archetype README.md)
- .xml: 9
- .config: 90 ✅
- .txt: 3 ✅

### Verification

**Published API .config files** (sample from v6):
```
nablarch-batch-dbless/tools/static-analysis/spotbugs/published-config/production/NablarchApiForProgrammer.config
nablarch-batch-dbless/tools/static-analysis/spotbugs/published-config/production/NablarchApiForArchitect.config
nablarch-batch-dbless/tools/static-analysis/spotbugs/published-config/test/NablarchTestingApiForProgrammer.config
...
(9 archetype projects × 10 config files each = 90 files)
```

**Archetype README.md** (v6):
```
nablarch-single-module-archetype/nablarch-batch/README.md
nablarch-single-module-archetype/nablarch-jaxrs/README.md
nablarch-single-module-archetype/nablarch-web/README.md
...
(9 archetype projects)
```

**config.txt files**:
```
nablarch-document/en/development_tools/toolbox/tools/JspStaticAnalysis/config.txt
nablarch-single-module-archetype/nablarch-container-web/tools/static-analysis/jspanalysis/config.txt
nablarch-single-module-archetype/nablarch-web/tools/static-analysis/jspanalysis/config.txt
```

## Impact

### File Count Changes

| Version | Before | After | Increase |
|---------|--------|-------|----------|
| v6 | 503 | 605 | +102 (+20.3%) |
| v5 | 442 | 544 | +102 (+23.1%) |
| **Total** | **945** | **1,149** | **+204 (+21.6%)** |

### New File Breakdown

**Per version**:
- .config: 90 files (public API definitions)
- .txt: 3 files (JSP static analysis config)
- README.md: 9 files (archetype setup instructions)
- **Total: 102 new files per version**

### Category Mapping

These files will map to:
1. **check-published-api** (90 .config files per version)
   - NablarchApiForArchitect.config
   - NablarchApiForProgrammer.config
   - NablarchTestingApiForArchitect.config
   - NablarchTestingApiForProgrammer.config
   - JavaOpenApi.config / JakartaEEOpenApi.config

2. **archetype** (9 README.md per version)
   - Setup instructions for each archetype project

3. **tool** (3 config.txt per version)
   - JSP static analysis configuration

## Next Steps

1. Update PR #12 description to reflect new file counts
2. Phase 5-7 execution will categorize these new files
3. Validation scripts may need updates to handle new file types

## Git Operations

```bash
# Commit
git add doc/mapping-creation-procedure/
git commit -m "Add support for .config and config.txt files in mapping scripts."

# Push
git push origin feature/issue-10-create-mapping-info
```

**Commit**: 4803f8d
