# Classification Rules

Path-based classification rules for mapping Nablarch documentation files to Type, Category ID, and Processing Pattern.

## Rule Priority

Rules are evaluated in order. The first matching rule determines the classification.

## Type and Category Rules

### about

**Pattern**: `about_nablarch/**`
- Type: `about`
- Category: `about-nablarch`
- PP: empty

### migration

**Pattern**: `migrationguide/**`
- Type: `about`
- Category: `migration`
- PP: empty

### release-notes

**Pattern**: `releases/**`
- Type: `about`
- Category: `release-notes`
- PP: empty

### adapters

**Pattern**: `application_framework/adaptors/**`
- Type: `component`
- Category: `adapters`
- PP: empty

### blank-project

**Pattern**: `application_framework/application_framework/blank_project/**`
- Type: `setup`
- Category: `blank-project`
- PP: determined by PP rules (see below)

### configuration

**Pattern**: `application_framework/application_framework/configuration/**`
- Type: `setup`
- Category: `configuration`
- PP: empty

### cloud-native

**Pattern**: `application_framework/application_framework/cloud_native/**`
- Type: `setup`
- Category: `cloud-native`
- PP: empty

### handlers (processing-pattern specific)

**Patterns**:
- `application_framework/application_framework/handlers/batch/**`
  - Type: `processing-pattern`
  - Category: `nablarch-batch`
  - PP: `nablarch-batch`

- `application_framework/application_framework/handlers/http_messaging/**`
  - Type: `component`
  - Category: `handlers`
  - PP: `http-messaging`

- `application_framework/application_framework/handlers/mom_messaging/**`
  - Type: `component`
  - Category: `handlers`
  - PP: `mom-messaging`

- `application_framework/application_framework/handlers/rest/**`
  - Type: `component`
  - Category: `handlers`
  - PP: `restful-web-service`

- `application_framework/application_framework/handlers/web/**`
  - Type: `component`
  - Category: `handlers`
  - PP: `web-application`

- `application_framework/application_framework/handlers/web_service/**`
  - Type: `component`
  - Category: `handlers`
  - PP: `http-messaging`

- `application_framework/application_framework/handlers/standalone/**`
  - Type: `component`
  - Category: `handlers`
  - PP: `nablarch-batch` (needs content verification)

- `application_framework/application_framework/handlers/common/**`
  - Type: `component`
  - Category: `handlers`
  - PP: empty

- `application_framework/application_framework/handlers/messaging/**`
  - Type: `component`
  - Category: `handlers`
  - PP: `db-messaging`

### processing-patterns (jsr352)

**Pattern**: `application_framework/application_framework/batch/jsr352/**`
- Type: `processing-pattern`
- Category: `jakarta-batch`
- PP: `jakarta-batch`

### processing-patterns (nablarch_batch)

**Pattern**: `application_framework/application_framework/batch/nablarch_batch/**`
- Type: `processing-pattern`
- Category: `nablarch-batch`
- PP: `nablarch-batch`

### processing-patterns (batch index)

**Patterns**:
- `application_framework/application_framework/batch/index.rst`
  - Type: `processing-pattern`
  - Category: `nablarch-batch`
  - PP: `nablarch-batch`

- `application_framework/application_framework/batch/functional_comparison.rst`
  - Type: `processing-pattern`
  - Category: `nablarch-batch`
  - PP: `nablarch-batch`

### processing-patterns (web)

**Pattern**: `application_framework/application_framework/web_application/**`
- Type: `processing-pattern`
- Category: `web-application`
- PP: `web-application`

### processing-patterns (rest)

**Pattern**: `application_framework/application_framework/web_service/**`
- Type: `processing-pattern`
- Category: `restful-web-service`
- PP: `restful-web-service`

### processing-patterns (http-messaging)

**Pattern**: `application_framework/application_framework/messaging/http/**`
- Type: `processing-pattern`
- Category: `http-messaging`
- PP: `http-messaging`

### processing-patterns (mom-messaging)

**Pattern**: `application_framework/application_framework/messaging/mom/**`
- Type: `processing-pattern`
- Category: `mom-messaging`
- PP: `mom-messaging`

### processing-patterns (db-messaging)

**Pattern**: `application_framework/application_framework/messaging/db/**`
- Type: `processing-pattern`
- Category: `db-messaging`
- PP: `db-messaging`

### libraries

**Pattern**: `application_framework/application_framework/libraries/**`
- Type: `component`
- Category: `libraries`
- PP: empty

### testing-framework

**Pattern**: `development_tools/testing_framework/**`
- Type: `development-tools`
- Category: `testing-framework`
- PP: empty

### toolbox

**Pattern**: `development_tools/toolbox/**`
- Type: `development-tools`
- Category: `toolbox`
- PP: empty

### java-static-analysis

**Pattern**: `development_tools/java_static_analysis/**`
- Type: `development-tools`
- Category: `java-static-analysis`
- PP: empty

### setting-guide

**Pattern**: `application_framework/application_framework/setting_guide/**`
- Type: `setup`
- Category: `setting-guide`
- PP: empty

### nablarch-patterns (system-development-guide)

**Patterns from nablarch-system-development-guide**:
- `Asynchronous_operation_in_Nablarch.md`
  - Type: `guide`
  - Category: `nablarch-patterns`
  - PP: empty

- `Nablarch_anti-pattern.md`
  - Type: `guide`
  - Category: `nablarch-patterns`
  - PP: empty

- `Nablarch_batch_processing_pattern.md`
  - Type: `guide`
  - Category: `nablarch-patterns`
  - PP: empty

### security-check (system-development-guide)

**Pattern**: `Sample_Project/設計書/Nablarch機能のセキュリティ対応表.xlsx`
- Type: `check`
- Category: `security-check`
- PP: empty

## Processing Pattern Rules

Processing Pattern (PP) is assigned ONLY when:
1. The file belongs to a processing-pattern Type, OR
2. The file is in handlers/ but is specific to a processing pattern

### PP Assignment Logic

If Type is `processing-pattern`:
- PP = Category ID (same value)

If Type is `component` and Category is `handlers`:
- If path contains `/batch/` → PP = `nablarch-batch`
- If path contains `/http_messaging/` → PP = `http-messaging`
- If path contains `/mom_messaging/` → PP = `mom-messaging`
- If path contains `/rest/` → PP = `restful-web-service`
- If path contains `/web/` → PP = `web-application`
- If path contains `/web_service/` → PP = `http-messaging`
- If path contains `/messaging/` → PP = `db-messaging`
- If path contains `/standalone/` → PP = `nablarch-batch` (needs content verification)
- If path contains `/common/` → PP = empty (common handlers)

If Type is `setup` and Category is `blank-project`:
- If filename contains `Jbatch` → PP = `jakarta-batch`
- If filename contains `NablarchBatch` → PP = `nablarch-batch`
- If filename contains `Web.rst` (not WebService) → PP = `web-application`
- If filename contains `WebService` → PP = `restful-web-service`
- Otherwise → PP = empty

All other cases → PP = empty

## Confidence Levels

Each classification has a confidence level:

- `confirmed`: Path pattern clearly indicates classification
- `needs_content`: Path pattern suggests classification but content verification needed
- `unknown`: No path pattern matches

### Confidence Assignment

- Most path rules → `confirmed`
- `/standalone/` handlers → `needs_content` (could be batch, messaging, or common)
- No matching rule → `unknown`

## Type Overriding

Some files may appear to be one Type based on path but are actually another Type based on content.

### Common Overrides

**Loop handlers in batch**:
- Path: `application_framework/application_framework/handlers/batch/`
- Path-based: Type = `processing-pattern`, Category = `nablarch-batch`
- Content-based: If file describes handler queue configuration → keep as `processing-pattern`
- Content-based: If file is standalone handler documentation → override to Type = `component`, Category = `handlers`

This override is rare and requires content judgement (see `content-judgement.md`).

## Exclusions

The following files are excluded from mapping:

- Root `README.md`
- Files under `.textlint/`
- Files under `getting_started/` directories (tutorials, not reference documentation)
  - Exception: `getting_started.rst` index files are included

## Valid Taxonomy

### Type → Category Mappings

| Type | Valid Category IDs |
|------|-------------------|
| processing-pattern | nablarch-batch, jakarta-batch, restful-web-service, http-messaging, web-application, mom-messaging, db-messaging |
| component | handlers, libraries, adapters |
| development-tools | testing-framework, toolbox, java-static-analysis |
| setup | blank-project, configuration, setting-guide, cloud-native |
| guide | nablarch-patterns, business-samples |
| check | security-check |
| about | about-nablarch, migration, release-notes |

### Category → Processing Pattern Mappings

| Category | Valid PPs |
|----------|-----------|
| nablarch-batch | nablarch-batch (or empty) |
| jakarta-batch | jakarta-batch (or empty) |
| restful-web-service | restful-web-service (or empty) |
| http-messaging | http-messaging (or empty) |
| web-application | web-application (or empty) |
| mom-messaging | mom-messaging (or empty) |
| db-messaging | db-messaging (or empty) |
| handlers | any PP or empty |
| All others | empty |

## Special Cases

### duplicate_form_submission.rst

English: `application_framework/application_framework/web_application/feature_details/tag/duplicate_form_submission.rst`
Japanese equivalent: `double_transmission.rst` (not `duplicate_form_submission.rst`)

When generating Japanese titles, use this mapping.

### index.rst Files

**Adoption rule**:
- If `index.rst` contains `toctree` directive → Include (it's a category index)
- If `index.rst` is empty or minimal → Exclude (it's just a container)

This determination requires content reading (see `content-judgement.md`).
