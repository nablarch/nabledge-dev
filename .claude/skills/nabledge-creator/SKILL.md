---
name: nabledge-creator
description: Internal skill for creating and maintaining nabledge knowledge files, mappings, and indexes
---

# nabledge-creator

Internal skill for nabledge developers to create and maintain knowledge files, documentation mappings, and search indexes.

## Usage

```
nabledge-creator <workflow> <version> [args...]
```

Where:
- `<workflow>`: Workflow name (mapping, index, knowledge, verify-mapping, verify-index, verify-knowledge)
- `<version>`: Nablarch version number (6 for v6, 5 for v5)
- `[args...]`: Additional workflow-specific arguments

Examples:
```
nabledge-creator mapping 6
nabledge-creator index 6
nabledge-creator knowledge 6 --filter "pilot=true"
nabledge-creator verify-mapping 6
```

Execute workflows in `workflows/` directory.
