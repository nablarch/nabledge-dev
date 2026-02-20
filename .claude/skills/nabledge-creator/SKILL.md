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

## Scripts

All scripts are located in `.claude/skills/nabledge-creator/scripts/`:

- `generate-mapping.py` - Parse and classify documentation files
- `validate-mapping.py` - Validate mapping structure and taxonomy
- `export-excel.py` - Export mapping to Excel format
- `generate-mapping-checklist.py` - Create verification checklist
- `validate-knowledge.py` - Validate knowledge file schema
- `convert-knowledge-md.py` - Convert JSON to human-readable Markdown
- `generate-checklist.py` - Create knowledge verification checklist
- `generate-index.py` - Generate index.toon from knowledge files
- `generate-index-checklist.py` - Create index verification checklist

## References

Reference files in `.claude/skills/nabledge-creator/references/`:

- `classification.md` - Path-based classification rules
- `target-path.md` - Source to target path conversion rules
- `content-judgement.md` - Content-based classification rules
- `knowledge-file-plan.md` - Knowledge file catalog and sources
- `knowledge-schema.md` - JSON schema and templates for knowledge files
