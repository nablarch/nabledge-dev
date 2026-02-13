# V5 Handler Categorization Review Summary

## Overview
Reviewed all 44 handler entries in mapping-v5.json to determine proper categorization for processing patterns (batch-nablarch and rest).

## Files Reviewed
- **Total handlers**: 44 entries
- **Source**: mapping-v5.json from work/20260213/create-mapping-info/

## Categorization Rules Applied

### Pattern-Specific Handlers
1. **handlers/batch/**: Already correctly categorized as `batch-nablarch`
2. **handlers/rest/**: Already correctly categorized as `rest`

### Common Handlers to Add Categories
Based on content analysis and module dependencies:

#### Handlers requiring `batch-nablarch` category addition:
- **v5-0200**: retry_handler (Module: nablarch-fw-standalone, extensively used in batch)
- **v5-0201**: duplicate_process_check_handler (Module: nablarch-fw-batch, batch-specific)
- **v5-0204**: process_stop_handler (Modules: nablarch-fw-standalone + nablarch-fw-batch)
- **v5-0205**: data_read_handler (Core batch component for DataReader)
- **v5-0206**: multi_thread_execution_handler (Batch performance optimization)
- **v5-0207**: status_code_convert_handler (Batch exit code management)
- **v5-0208**: main (Standalone/batch launcher)
- **v5-0223**: file_record_writer_dispose_handler (Batch file output patterns)

#### Handlers requiring `batch-nablarch` + `rest` category addition:
- **v5-0213**: database_connection_management_handler (Used in all DB-accessing patterns)
- **v5-0214**: global_error_handler (Common error handling)
- **v5-0215**: thread_context_handler (Common thread context management)
- **v5-0217**: thread_context_clear_handler (Paired with thread_context_handler)
- **v5-0222**: transaction_management_handler (Common transaction control)

#### Handlers requiring `rest` category addition:
- **v5-0219**: permission_check_handler (REST API authorization)
- **v5-0221**: ServiceAvailabilityCheckHandler (REST API availability control)

### Handlers Kept Generic (handler only)
- Index pages (v5-0076, v5-0202, v5-0216)
- Out of scope handlers:
  - Web interceptors (v5-0244 to v5-0249) - Web UI is out of scope
  - HTTP messaging (v5-0209 to v5-0212) - Messaging is out of scope
  - MOM messaging (v5-0250 to v5-0253) - Messaging is out of scope
- Generic infrastructure:
  - request_thread_loop_handler (v5-0203) - For resident monitoring, not on-demand batch
  - request_path_java_package_mapping (v5-0218) - Web-focused
  - request_handler_entry (v5-0220) - Generic infrastructure

## Key Findings

### Standalone Handlers Analysis
The `handlers/standalone/` directory contains handlers that are **primarily used in Nablarch batch processing**, despite the "standalone" name suggesting generic usage. Evidence:

1. **Module Dependencies**: Many depend on `nablarch-fw-batch` (e.g., duplicate_process_check_handler, process_stop_handler)
2. **Documentation References**: Extensively referenced in Nablarch batch architecture documentation
3. **Use Cases**: Core components for batch processing patterns (FILE-DB, DB-DB, DB-FILE)

### Common Handlers Cross-Pattern Usage
Several `handlers/common/` handlers are used across multiple patterns:
- Database/transaction handlers → both batch and REST
- Thread context handlers → both batch and REST
- Error handlers → both batch and REST
- File handlers → primarily batch (DB-FILE pattern)

## Recommendations Summary

**Add batch-nablarch category**: 8 handlers (standalone handlers used in batch)
**Add rest category**: 2 handlers (permission and service availability)
**Add both batch-nablarch + rest**: 5 handlers (common infrastructure)
**Keep generic**: 29 handlers (index pages, out-of-scope, or truly generic)

## Output Files
- **handler-categorization-review-v5.json**: Detailed review with recommendations for all 44 handlers
- Each entry includes: id, file_path, title, current_categories, recommended_categories, and detailed reason

## Next Steps
1. Review recommendations in handler-categorization-review-v5.json
2. Update mapping-v5.json categories based on approved recommendations
3. Consider same analysis for mapping-v6.json if needed
