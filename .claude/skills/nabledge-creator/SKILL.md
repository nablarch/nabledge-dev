---
name: nabledge-creator
description: Internal skill for creating and maintaining nabledge knowledge files, mappings, and indexes
---

# nabledge-creator

Internal skill for nabledge developers to create and maintain knowledge files, documentation mappings, and search indexes.

## Workflows

### Mapping Workflows

- `mapping` - Generate documentation mapping from Nablarch official docs
- `verify-mapping-6` - Verify mapping classification accuracy (separate session)

### Knowledge File Workflows

- `knowledge` - Generate knowledge files from official documentation
- `verify-knowledge` - Verify knowledge file quality (separate session)

### Index Workflows

- `index` - Generate index.toon from knowledge files
- `verify-index-6` - Verify index hints accuracy (separate session)

## Usage

**Generate mapping**:
```
nabledge-creator mapping
```

**Verify mapping** (separate session):
```
nabledge-creator verify-mapping-6
```

**Generate knowledge files**:
```
nabledge-creator knowledge --filter "Type=component AND Category=handlers"
```

**Generate index**:
```
nabledge-creator index
```

## Verification Sessions

Verification workflows run in separate sessions to avoid context bias. The generation session creates a checklist, and the verification session reviews actual content against that checklist.
