# Restructure Nablarch Official Documentation Layout

## What Was Done

Separated Nablarch official documentation into version-specific directories to enable parallel development of nabledge-6 and nabledge-5 skills.

### Files Changed

1. **setup.sh** (lines 272-311)
   - Added `NAB_OFFICIAL_V6_DIR` and `NAB_OFFICIAL_V5_DIR` variables
   - Enhanced `clone_or_update_repo()` function to accept branch parameter
   - Clone v6 repositories (main branch) to `.lw/nab-official/v6/`
   - Clone v5 repositories (v5-main branch) to `.lw/nab-official/v5/`
   - Skip nablarch-system-development-guide for v5 (no v5-main branch exists)
   - Added `.lw/research/` directory creation

2. **CLAUDE.md** (lines 29-45)
   - Updated directory structure diagram to show v6/ and v5/ subdirectories
   - Added new section "Nablarch Official Documentation" with:
     - Repository version table
     - Note for nabledge-5 development about which sources to use

### Directory Structure

```
.lw/nab-official/
├── v6/
│   ├── nablarch-document/ (main branch)
│   ├── nablarch-single-module-archetype/ (main branch)
│   └── nablarch-system-development-guide/ (main branch)
└── v5/
    ├── nablarch-document/ (v5-main branch)
    └── nablarch-single-module-archetype/ (v5-main branch)
```

## Results

Changes completed successfully. The setup script now:
- Clones Nablarch 6 documentation (main branch) into v6/ directory
- Clones Nablarch 5 documentation (v5-main branch) into v5/ directory
- Avoids branch switching confusion when working across versions

## Verification Steps

To test the changes:

```bash
# Run setup script
./setup.sh

# Verify directory structure
ls -la .lw/nab-official/v6/
ls -la .lw/nab-official/v5/

# Verify branches
git -C .lw/nab-official/v6/nablarch-document branch --show-current  # Should show: main
git -C .lw/nab-official/v5/nablarch-document branch --show-current  # Should show: v5-main
```

## Notes

- The `.lw/` directory is in `.gitignore` and remains local-only
- Zero runtime impact - nabledge skills use `knowledge/*.json` files, not cloned repositories
- Cloned repositories serve as source material for creating knowledge files during development
