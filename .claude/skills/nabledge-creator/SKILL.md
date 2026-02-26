---
name: nabledge-creator
description: Internal skill for creating and maintaining nabledge knowledge files, mappings, and indexes
---

# nabledge-creator

## Usage

```
nabledge-creator <workflow> <version> [args...]
```

Where:
- `<workflow>`: Workflow name (mapping, knowledge, verify-mapping, verify-knowledge, clean)
- `<version>`: Nablarch version number (6, 5, etc.)
- `[args...]`: Additional workflow-specific arguments

Execute the corresponding workflow file in `workflows/<workflow>.md` with the provided arguments.

## Workflows

### Generation Workflows

- **mapping**: Generate documentation mapping from official sources (Type/Category/PP classification)
- **knowledge**: Generate knowledge files (JSON + MD) and update index.toon from RST documentation

### Verification Workflows

- **verify-mapping**: Verify mapping classification accuracy by reading RST content
- **verify-knowledge**: Verify knowledge files content accuracy and index.toon integration

### Maintenance Workflows

- **clean**: Delete generated files (knowledge/*.json, docs/*.md, output/mapping-v{version}.*) for clean regeneration
