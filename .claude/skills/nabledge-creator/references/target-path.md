# Target Path Conversion Rules

Rules for converting Source Path (RST location) to Target Path (knowledge file location in nabledge-6).

## Basic Structure

```
Target Path = {type}/{category}/{subdirs}/{filename}
```

Where:
- `{type}`: Type from classification
- `{category}`: Category ID from classification
- `{subdirs}`: Subdirectories preserved from source (see rules below)
- `{filename}`: Converted filename

## Filename Conversion

### Extension

- `.rst` → `.md`
- `.md` → `.md` (no change)
- `.xlsx` → `.xlsx` (no change)

### Character Replacement

- `_` → `-` (underscore to hyphen)

### Examples

| Source | Target |
|--------|--------|
| `data_read_handler.rst` | `data-read-handler.md` |
| `jsr310_adaptor.rst` | `jsr310-adaptor.md` |
| `Asynchronous_operation_in_Nablarch.md` | `Asynchronous-operation-in-Nablarch.md` |

## Subdirectory Rules

### component Category

**Preserve subdirectories after the category directory**.

Examples:
- Source: `application_framework/adaptors/lettuce_adaptor/redisstore_lettuce_adaptor.rst`
  - Type: `component`, Category: `adapters`
  - Target: `component/adapters/lettuce_adaptor/redisstore-lettuce-adaptor.md`

- Source: `application_framework/application_framework/handlers/common/global_error_handler.rst`
  - Type: `component`, Category: `handlers`
  - Target: `component/handlers/common/global-error-handler.md`

- Source: `application_framework/application_framework/handlers/standalone/data_read_handler.rst`
  - Type: `component`, Category: `handlers`
  - Target: `component/handlers/standalone/data-read-handler.md`

### processing-pattern Category

**Preserve subdirectories within the processing pattern directory**.

Examples:
- Source: `application_framework/application_framework/batch/nablarch_batch/feature_details/nablarch_batch_error_process.rst`
  - Type: `processing-pattern`, Category: `nablarch-batch`
  - Target: `processing-pattern/nablarch-batch/nablarch-batch-error-process.md`
  - Note: `feature_details/` is flattened

- Source: `application_framework/application_framework/batch/jsr352/feature_details/database_reader.rst`
  - Type: `processing-pattern`, Category: `jakarta-batch`
  - Target: `processing-pattern/jakarta-batch/database-reader.md`

### setup Category

**Preserve subdirectories after category directory**.

Example:
- Source: `application_framework/application_framework/blank_project/setup_blankProject/setup_Jbatch.rst`
  - Type: `setup`, Category: `blank-project`
  - Target: `setup/blank-project/setup-Jbatch.md`
  - Note: `setup_blankProject/` is flattened to match the pattern

### Other Categories

**No subdirectories** (flatten to category level).

Examples:
- Source: `about_nablarch/concept.rst`
  - Type: `about`, Category: `about-nablarch`
  - Target: `about/about-nablarch/concept.md`

- Source: `development_tools/testing_framework/guide/unit_test/guide.rst`
  - Type: `development-tools`, Category: `testing-framework`
  - Target: `development-tools/testing-framework/guide.md`

## index.rst Special Rules

### Rule 1: Meaningful Name

If `index.rst` represents a meaningful section (not just a directory container), use a descriptive name from the h1 title.

Examples:
- Source: `application_framework/application_framework/batch/index.rst`
  - Title: "Batch Application"
  - Target: `processing-pattern/nablarch-batch/batch.md` (not `index.md`)

- Source: `application_framework/application_framework/batch/jsr352/index.rst`
  - Title: "Jakarta Batch-compliant Batch Application"
  - Target: `processing-pattern/jakarta-batch/jsr352.md`

### Rule 2: Directory Name

If the `index.rst` is a directory container with a clear directory name, use that directory name.

Example:
- Source: `application_framework/application_framework/handlers/batch/nablarch_batch/index.rst`
  - Target: `processing-pattern/nablarch-batch/nablarch_batch.md`

### Rule 3: Keep index.md

If no better name is evident, keep `index.md`.

## Path Validation

Target paths must satisfy:

1. **Start with Type**: Path must begin with the Type directory
2. **Contain Category**: Path must contain the Category ID
3. **Unique**: No two source files can map to the same target path
4. **Valid characters**: Only alphanumeric, `-`, `/`, and `.` allowed

## Examples

| Source Path | Type | Category | Target Path |
|-------------|------|----------|-------------|
| `about_nablarch/concept.rst` | about | about-nablarch | `about/about-nablarch/concept.md` |
| `application_framework/adaptors/doma_adaptor.rst` | component | adapters | `component/adapters/doma-adaptor.md` |
| `application_framework/application_framework/handlers/common/database_connection_management_handler.rst` | component | handlers | `component/handlers/common/database-connection-management-handler.md` |
| `application_framework/application_framework/batch/nablarch_batch/architecture.rst` | processing-pattern | nablarch-batch | `processing-pattern/nablarch-batch/architecture.md` |
| `development_tools/testing_framework/guide/development_guide/05_UnitTestGuide/02_RequestUnitTest/index.rst` | development-tools | testing-framework | `development-tools/testing-framework/RequestUnitTest.md` |
| `Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx` | check | security-check | `check/security-check/Nablarch機能のセキュリティ対応表.xlsx` |

## Implementation Notes

The conversion logic is:

```python
def convert_target_path(source_path, type_val, category, pp):
    # Extract filename
    filename = source_path.split('/')[-1]

    # Convert filename
    target_filename = convert_filename(filename)

    # Determine subdirectories
    subdirs = extract_subdirs(source_path, category)

    # Build target path
    if subdirs:
        return f"{type_val}/{category}/{subdirs}/{target_filename}"
    else:
        return f"{type_val}/{category}/{target_filename}"
```

The exact subdirectory extraction logic depends on the category and source path structure.
