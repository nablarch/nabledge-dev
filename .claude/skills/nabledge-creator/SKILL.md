---
name: nabledge-creator
description: Internal skill for creating and maintaining nabledge knowledge files, mappings, and indexes
---

# nabledge-creator

Internal skill for nabledge developers to create and maintain knowledge files, documentation mappings, and search indexes.

## Usage

```
nabledge-creator <workflow> [args...]
```

**Workflows:**
- `mapping {version}` - Generate documentation mapping for Nablarch v{version}
- `verify-mapping {version}` - Verify mapping accuracy
- `knowledge {version}` - Generate knowledge files
- `verify-knowledge {version}` - Verify knowledge content
- `index {version}` - Generate search index
- `verify-index {version}` - Verify index accuracy

Refer to individual workflow files in `workflows/` directory for detailed instructions.
