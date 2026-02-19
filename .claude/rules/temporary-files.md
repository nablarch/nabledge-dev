# Temporary Files

## Policy

Use `.tmp/` directory in repository root for temporary files and workspaces.

## Rationale

- **Repository-local**: Safer than `~/tmp` which may be shared across projects
- **Consistent location**: All temporary files in one place
- **Easy cleanup**: Can delete entire `.tmp/` directory safely
- **Gitignored**: Automatically excluded from version control

## Use Cases

- Test evaluation workspaces (nabledge-test)
- Temporary build outputs
- Cache files during processing
- Intermediate data files

## Examples

**nabledge-test workspaces**:
```
.tmp/nabledge-test/eval-handlers-001-143025/
```

**Temporary processing**:
```
.tmp/build-cache/
.tmp/processing-20260219/
```

## Cleanup

The `.tmp/` directory can be safely deleted at any time. It is gitignored and should not contain any permanent data.
