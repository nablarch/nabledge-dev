# Mapping Information: Official Docs to Knowledge Files

Created: 2026-02-13
Updated: 2026-02-17

## Summary

This mapping provides comprehensive information that maps Nablarch official documentation files to nabledge knowledge files. The mapping will be used by skills to automatically generate knowledge files.

## Files

### Category Definitions
- **categories-v6.json** - Category definitions for v6 (23 categories)
- **categories-v5.json** - Category definitions for v5 (23 categories)

### Mapping Information
- **mapping-v6.json** - Complete v6 mapping with categorization and targets (514 files)
- **mapping-v5.json** - Complete v5 mapping with categorization and targets (453 files)

### Excel Format (for review)
- **mapping-v6.xlsx** - Excel workbook with multiple sheets
- **mapping-v5.xlsx** - Excel workbook with multiple sheets

## Statistics

### V6 Mapping

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total files** | 514 | 100% |
| **In scope** | 451 | 87.7% |
| **Out of scope** | 63 | 12.3% |

### V5 Mapping

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total files** | 453 | 100% |
| **In scope** | 389 | 85.9% |
| **Out of scope** | 64 | 14.1% |

## Scope

**In Scope:**
- Nablarch Batch (On-demand) - FILE to DB, DB to DB, DB to FILE
- Nablarch Batch (Resident) - Table Queue messaging
- RESTful Web Services - JAX-RS support, REST API implementation
- HTTP Messaging - HTTP-based messaging between systems

**Out of Scope:**
- Jakarta Batch (JSR 352)
- MOM Messaging (Message-oriented middleware)
- Web Applications (JSP/UI)

## Processing Pattern Distribution

### V6

| Processing Pattern | Files | Description |
|--------------------|-------|-------------|
| batch-nablarch | 62 | Nablarch Batch (On-demand + Resident): FILE to DB, DB to DB, DB to FILE, Table Queue |
| rest | 56 | RESTful Web Services (JAX-RS) |
| http-messaging | 6 | HTTP Messaging (alternative to REST) |
| messaging-db | 8 | DB Messaging (Resident Batch, Table Queue) |

### V5

| Processing Pattern | Files | Description |
|--------------------|-------|-------------|
| batch-nablarch | 57 | Nablarch Batch (On-demand + Resident): FILE to DB, DB to DB, DB to FILE, Table Queue |
| rest | 55 | RESTful Web Services (JAX-RS) |
| http-messaging | 6 | HTTP Messaging (alternative to REST) |
| messaging-db | 8 | DB Messaging (Resident Batch, Table Queue) |

## Excel Sheets

Each Excel file contains 4 sheets for easy review:

1. **Summary** - Statistics overview
2. **All Files** - Complete file listing with categories and scope
3. **In Scope** - Files to be included in knowledge base
4. **Out of Scope** - Files excluded from knowledge base

**Features:**
- Color coding (green = in scope, red = out of scope)
- Auto filters on all data sheets
- Frozen header rows for easy scrolling
- Optimized column widths

## Usage

### Query Mapping (JSON)

Get in-scope files for a specific category:
```bash
jq '.mappings[] | select(.in_scope == true and (.categories | contains(["batch-nablarch"])))' mapping-v6.json
```

Get out-of-scope files:
```bash
jq '.mappings[] | select(.in_scope == false) | {file: .source_file, reason: .reason_for_exclusion}' mapping-v6.json
```

Get target file paths:
```bash
jq '.mappings[] | select(.source_file | contains("messaging/db")) | {source: .source_file, targets: .target_files}' mapping-v6.json
```

## Change History

### 2026-02-17: Scope Update
- Added DB Messaging (Resident Batch) to in-scope
- Updated 16 files (8 V6 + 8 V5) from out-of-scope to in-scope
- V6: in_scope 443→451, out_of_scope 71→63
- V5: in_scope 381→389, out_of_scope 72→64

### 2026-02-13: Initial Creation
- Created comprehensive mapping for 967 files
- All files reviewed by AI agents for proper categorization
- 100 category additions based on content analysis
