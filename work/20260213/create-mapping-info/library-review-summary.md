# V6 Library Categorization Review Summary

## Overview
Reviewed all 49 library files in mapping-v6.json to determine proper categorization based on actual usage in different processing patterns.

## Key Findings

### Universal Libraries (Used by Both Batch and REST)
**Total: 20 files**

These libraries are fundamental and used across multiple processing patterns:

1. **Database Access** (5 files)
   - database_management.rst, database.rst, universal_dao.rst, generator.rst, functional_comparison.rst
   - Critical for both batch (FILE to DB, DB to FILE, DB to DB) and REST (CRUD operations)

2. **Validation** (4 files)
   - validation.rst, bean_validation.rst, nablarch_validation.rst, functional_comparison.rst
   - Essential for input validation in both batch (external data) and REST (request validation)

3. **Core Utilities** (4 files)
   - bean_util.rst, utility.rst, format.rst, date.rst
   - Universal utilities used by all patterns

4. **Logging** (4 files)
   - log.rst, failure_log.rst, sql_log.rst, performance_log.rst
   - Monitoring and debugging for both patterns

5. **Infrastructure** (3 files)
   - repository.rst, transaction.rst, static_data_cache.rst, message.rst, code.rst, exclusive_control.rst
   - Fundamental framework features

### Batch-Specific Libraries
**Total: 9 files**

Libraries primarily or exclusively used for batch file processing:

1. **Data I/O** (7 files)
   - data_converter.rst, data_bind.rst, data_format.rst
   - functional_comparison.rst, format_definition.rst, multi_format_example.rst
   - Critical for FILE to DB, DB to FILE patterns

2. **File Management** (1 file)
   - file_path_management.rst
   - File path resolution for batch operations

### REST-Specific Libraries
**Total: 2 files**

Libraries specifically for RESTful web services:

1. **REST Logging** (1 file)
   - jaxrs_access_log.rst
   - JAX-RS specific access logging

2. **Authorization** (1 file - partial)
   - role_check.rst
   - Role-based access control (can be used in REST APIs)

### Out of Scope Libraries
**Total: 18 files**

Libraries not relevant to in-scope patterns (batch-nablarch and rest):

1. **Web UI Features** (9 files)
   - tag.rst, tag_reference.rst
   - stateless_web_app.rst, db_double_submit.rst
   - session_store.rst, create_example.rst, update_example.rst
   - http_access_log.rst
   - permission_check.rst (authorization/permission_check.rst)

2. **Out of Scope Functionality** (4 files)
   - mail.rst (uses resident batch - excluded)
   - system_messaging.rst, http_system_messaging.rst, mom_system_messaging.rst (MOM - excluded)
   - messaging_log.rst (MOM logging)
   - service_availability.rst (primarily for web and resident batch)

3. **Index/TOC Files** (1 file)
   - index.rst (library index page)

## Categorization Statistics

### Current State
- All 49 files: `["library"]` only

### Recommended State
- **Generic library only**: 18 files (out of scope or index)
- **library + batch-nablarch**: 9 files (batch-specific)
- **library + rest**: 1 file (REST-specific)
- **library + batch-nablarch + rest**: 20 files (universal)
- **library + rest (partial)**: 1 file (role_check - can be used in REST)

## Implementation Impact

### High Priority Changes
Files that should definitely be added to pattern categories:

1. **Database libraries** → Add to both batch-nablarch AND rest
   - Essential for all data access patterns

2. **Validation libraries** → Add to both batch-nablarch AND rest
   - Critical for data quality in all patterns

3. **Data I/O libraries** → Add to batch-nablarch
   - Core batch file processing functionality

4. **JAX-RS access log** → Add to rest
   - REST-specific logging

### Pattern Usage Matrix

| Library Category | batch-nablarch | rest | Reason |
|-----------------|----------------|------|--------|
| Database Access | ✓ | ✓ | DB operations in both |
| Validation | ✓ | ✓ | Input validation in both |
| Data I/O | ✓ | ✗ | FILE processing (batch only) |
| Core Utilities | ✓ | ✓ | Universal utilities |
| Logging (general) | ✓ | ✓ | All patterns need logging |
| JAX-RS Log | ✗ | ✓ | REST-specific |
| Infrastructure | ✓ | ✓ | DI, transaction, etc. |
| Web UI | ✗ | ✗ | Out of scope |
| Messaging | ✗ | ✗ | Out of scope |

## Recommendations

1. **Update mapping-v6.json** with recommended categories for:
   - 20 universal libraries (add both batch-nablarch and rest)
   - 9 batch-specific libraries (add batch-nablarch)
   - 2 REST-specific libraries (add rest)

2. **Keep as generic library only**:
   - 18 out-of-scope or index files

3. **Priority order for updates**:
   1. Database and validation (highest priority - used everywhere)
   2. Data I/O for batch (critical for FILE processing)
   3. Core utilities and logging (universal support)
   4. REST-specific logging (REST monitoring)

## File Breakdown by Decision

### Add to BOTH batch-nablarch AND rest (20 files)
```
database_management.rst, database.rst, universal_dao.rst, generator.rst
database/functional_comparison.rst
validation.rst, bean_validation.rst, nablarch_validation.rst
validation/functional_comparison.rst
bean_util.rst, utility.rst, format.rst, date.rst
log.rst, failure_log.rst, sql_log.rst, performance_log.rst
repository.rst, transaction.rst, static_data_cache.rst
message.rst, code.rst, exclusive_control.rst
```

### Add to batch-nablarch ONLY (9 files)
```
data_converter.rst, data_bind.rst, data_format.rst
data_io/functional_comparison.rst
data_format/format_definition.rst, data_format/multi_format_example.rst
file_path_management.rst
```

### Add to rest ONLY (1 file)
```
log/jaxrs_access_log.rst
```

### Add to rest (partial - 1 file)
```
authorization/role_check.rst (may be used in REST APIs for authorization)
```

### Keep as library ONLY (18 files)
```
mail.rst, service_availability.rst, system_messaging.rst
http_system_messaging.rst, mom_system_messaging.rst
permission_check.rst, authorization/permission_check.rst
stateless_web_app.rst, db_double_submit.rst
session_store.rst, session_store/create_example.rst, session_store/update_example.rst
tag.rst, tag/tag_reference.rst
log/http_access_log.rst, log/messaging_log.rst
index.rst
```

## Validation Notes

- Content-based analysis confirms libraries are properly identified
- Universal libraries (database, validation, logging) are correctly identified as used by both patterns
- Batch-specific file I/O libraries correctly identified as batch-only
- Out-of-scope features (web UI, MOM) correctly kept as generic
- REST-specific logging correctly identified as REST-only
