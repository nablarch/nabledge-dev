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
- `<workflow>`: Workflow name (mapping, index, knowledge, verify-mapping, verify-index, verify-knowledge)
- `<version>`: Nablarch version number (6, 5, etc.)
- `[args...]`: Additional workflow-specific arguments

Execute the corresponding workflow file in `workflows/<workflow>.md` with the provided arguments.
