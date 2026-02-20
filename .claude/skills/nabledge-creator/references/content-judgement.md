# Content-Based Judgement Rules

Rules for reading RST content to make classification decisions when path-based rules are insufficient.

## When Content Reading is Required

Content reading is necessary when:
1. Confidence level is `needs_content` or `unknown`
2. Path-based classification needs verification
3. Review items are reported by generate-mapping.py

## Reading Strategy

### What to Read

1. **First 50 lines** of the RST file (includes title, overview, and structure)
2. **toctree directives** (indicates this is a container/index file)
3. **Referenced files** (`:ref:` targets, files in `toctree`)
4. **Parent directory context** (other files in the same directory)

### What to Extract

- **h1 title**: The file's main subject
- **First paragraph**: Purpose and scope
- **Section headers** (h2, h3): Structure and topics covered
- **Code references**: Class names, interfaces mentioned
- **Directive types**: `.. important::`, `.. warning::`, `.. toctree::`

## index.rst Judgement

### Adoption Criteria

**Include** if:
- Contains `toctree` directive → It's a category index
- Contains substantive content (>100 words, excluding toctree) → It's a guide page
- Title indicates it's a conceptual overview → It's documentation

**Exclude** if:
- Empty or near-empty file
- Only contains `toctree` with no other content
- Title is generic "Index" or "Contents" with no explanation

### Examples

**Include**:
```rst
Batch Application
=================

Nablarch provides two batch processing frameworks...

.. toctree::
   :maxdepth: 2

   nablarch_batch/index
   jsr352/index
```
→ This explains batch concepts, include it.

**Exclude**:
```rst
Index
=====

.. toctree::
   nablarch_batch/index
   jsr352/index
```
→ Just a container, exclude it.

## Processing Pattern Determination

### Standalone Handlers

Path: `application_framework/application_framework/handlers/standalone/**`

**Judgement criteria**:

Read the file's first paragraph and section headers. Look for:

**Indicators of batch-specific handler**:
- Mentions "batch application" in purpose
- Describes sequential data processing
- References `DataReader`, batch-specific classes
- Used in batch handler queue

**Indicators of common handler**:
- Describes general-purpose functionality
- No mention of specific processing pattern
- Can be used across multiple patterns

**Decision**:
- If batch-specific → PP = `nablarch-batch`
- If common → PP = empty

### Handlers in Batch Directory

Path: `application_framework/application_framework/handlers/batch/**`

**Judgement criteria**:

**Type override logic**:

Read the content to determine if this is:

1. **Handler queue configuration** (processing-pattern documentation):
   - Describes handler queue structure
   - Explains handler execution order
   - Lists multiple handlers and their roles
   - → Type = `processing-pattern`, Category = `nablarch-batch`, PP = `nablarch-batch`

2. **Individual handler** (component documentation):
   - Focuses on a single handler class
   - Describes handler's specific responsibility
   - Contains class name, setup, configuration
   - → Type = `component`, Category = `handlers`, PP = `nablarch-batch`

**Examples**:

- `loop_handler.rst`: Single handler documentation → Type = `component` override
- If it were `handler_queue.rst`: Queue documentation → Keep as `processing-pattern`

## Type Overriding

### When to Override

Override Type from path-based classification ONLY when:
1. Content clearly contradicts path-based classification
2. The file is misplaced in the source repository structure

### Common Override Scenarios

**Scenario 1: Handler in processing-pattern directory**
- Path suggests: Type = `processing-pattern`
- Content shows: Individual handler documentation
- Override to: Type = `component`, Category = `handlers`, PP = (from path)

**Scenario 2: Library in handlers directory**
- Path suggests: Type = `component`, Category = `handlers`
- Content shows: Library/utility documentation (no handler interface)
- Override to: Type = `component`, Category = `libraries`, PP = empty

**Scenario 3: Guide in setup directory**
- Path suggests: Type = `setup`
- Content shows: Conceptual guide, not setup instructions
- Override to: Type = `guide`, Category = (determine from content)

### Override Confidence

Overrides should have `confirmed` confidence ONLY when:
- Content unambiguously indicates different classification
- Multiple indicators support the override
- No indicators contradict the override

## Processing Pattern Assignment

### For setup/blank-project Files

Read filename and first section:

**jakarta-batch indicators**:
- Filename contains `Jbatch`, `jsr352`
- Content mentions "Jakarta Batch", "JSR 352"
- → PP = `jakarta-batch`

**nablarch-batch indicators**:
- Filename contains `NablarchBatch`
- Content mentions "Nablarch batch", "standalone batch"
- → PP = `nablarch-batch`

**web-application indicators**:
- Filename contains `Web` but NOT `WebService`
- Content mentions "web application", "Jakarta EE web"
- → PP = `web-application`

**restful-web-service indicators**:
- Filename contains `WebService`, `RestfulWebService`
- Content mentions "RESTful", "REST API", "Jakarta RESTful Web Services"
- → PP = `restful-web-service`

## Special Cases

### duplicate_form_submission.rst

- English file: `duplicate_form_submission.rst`
- Japanese equivalent: `double_transmission.rst` (NOT `duplicate_form_submission.rst`)
- This is a known exception, handle explicitly in the enrichment phase

### getting_started Directories

Files under `getting_started/` are tutorials, not reference documentation.

**Exclusion rule**:
- Exclude all files under `getting_started/` subdirectories
- **Exception**: Files named `getting_started.rst` at the directory level are included (they're index files)

Example:
- Include: `batch/nablarch_batch/getting_started/getting_started.rst`
- Exclude: `batch/nablarch_batch/getting_started/tutorial/step1.rst`

### Multi-language Content

When reading English RST to verify Japanese title:
- Path: Replace `en/` with `ja/` in source path
- If Japanese file exists, read its h1 title
- If Japanese file doesn't exist (rare), report as warning

## Verification Checklist

When verifying classifications, confirm:

1. **Title matches content**: h1 title accurately describes the content
2. **Type matches scope**: Type reflects whether it's a concept, component, or guide
3. **Category matches subject**: Category correctly categorizes the technical area
4. **PP matches application**: PP is assigned only when file is pattern-specific

## Implementation Notes

Content judgement is implemented in the `verify()` function of `generate-mapping.py`:

```python
def verify(classification, rst_path):
    content = read_rst_first_50_lines(rst_path)
    indicators = extract_indicators(content)

    if classification['confidence'] == 'needs_content':
        # Upgrade to confirmed or downgrade to review
        if can_confirm(indicators, classification):
            classification['confidence'] = 'confirmed'
        else:
            classification['confidence'] = 'review'

    elif classification['confidence'] == 'confirmed':
        # Check for contradictions
        if contradicts(indicators, classification):
            classification['confidence'] = 'review'

    return classification
```

The `contradicts()` and `can_confirm()` functions implement the logic described in this document.
