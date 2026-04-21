# Exclude development infrastructure from plugin distribution

Closes #112

## Summary

This PR implements a whitelist approach to exclude development infrastructure files from nabledge plugin distribution, preventing end users from seeing irrelevant CI/CD configurations.

### Problem

Development infrastructure files (`.github/workflows/` and `.github/scripts/`) were being synced to nablarch/nabledge repository, causing confusion for end users who clone or browse the distribution repository.

### Solution

**Whitelist Approach**: Changed from copying entire `.github/` directory to explicitly copying only `.github/prompts/` (useful for GitHub Copilot users).

**Cleanup Implementation**: Added cleanup steps to remove existing development infrastructure files from:
- Distribution repository (nablarch/nabledge) during sync workflow
- User installations when running `setup-6-ghc.sh`

## Changes

### 1. Transform Script (`.github/scripts/transform-to-plugin.sh`)

**Before**: Copied entire `.github/` directory
```bash
cp -r "$SOURCE_DIR/.github" "$DEST_DIR/plugins/nabledge-6/"
```

**After**: Copies only `.github/prompts/` directory
```bash
if [ -d "$SOURCE_DIR/.github/prompts" ]; then
    mkdir -p "$DEST_DIR/plugins/nabledge-6/.github"
    cp -r "$SOURCE_DIR/.github/prompts" "$DEST_DIR/plugins/nabledge-6/.github/"
fi
```

### 2. Sync Workflow (`.github/workflows/sync-to-nabledge.yml`)

**Added**: Cleanup step to remove development infrastructure from distribution repository
```yaml
- name: Clean up development infrastructure files
  run: |
    # Remove .github/workflows and .github/scripts if they exist
    rm -rf "nabledge-repo/plugins/nabledge-6/.github/workflows"
    rm -rf "nabledge-repo/plugins/nabledge-6/.github/scripts"
```

### 3. Setup Script (`scripts/setup-6-ghc.sh`)

**Added**: Cleanup of previously installed development infrastructure
```bash
# First, clean up any previously installed development infrastructure files
if [ -d "$PROJECT_ROOT/.github/workflows" ]; then
    rm -rf "$PROJECT_ROOT/.github/workflows"
fi
if [ -d "$PROJECT_ROOT/.github/scripts" ]; then
    rm -rf "$PROJECT_ROOT/.github/scripts"
fi
```

**Changed**: Installs only `.github/prompts/` instead of entire `.github/`
```bash
if [ -d "$TEMP_DIR/$REPO_NAME/plugins/nabledge-6/.github/prompts" ]; then
    mkdir -p "$PROJECT_ROOT/.github"
    cp -r "$TEMP_DIR/$REPO_NAME/plugins/nabledge-6/.github/prompts" "$PROJECT_ROOT/.github/"
fi
```

## Expert Review

- [Software Engineer](./.pr/00112/review-by-software-engineer.md) - Rating: 4/5
- [DevOps Engineer](./.pr/00112/review-by-devops-engineer.md) - Rating: 4/5

### Key Findings

**Positive Aspects**:
- Security-conscious whitelist approach prevents accidental distribution
- Comprehensive cleanup handles both new deployments and upgrades
- Clear intent through comments and consistent pattern across files
- Defense in depth with multiple protection layers

**Recommendations** (all deferred to future work):
- Add integration tests to verify exclusion
- Consider centralized cleanup logic
- Document whitelist approach for future maintainers

## Impact

### For New Deployments
- Only `.github/prompts/` directory is synced to distribution repository
- `.github/workflows/` and `.github/scripts/` are excluded from sync

### For Existing Deployments
- Sync workflow removes existing infrastructure directories from nablarch/nabledge
- Setup script cleans up previously installed infrastructure files from user projects

### For End Users
- Cleaner repository with only necessary plugin files
- No confusion from seeing development infrastructure
- Reduced repository size

## Testing

All shell scripts pass syntax validation:
- ✅ `transform-to-plugin.sh`: Syntax OK
- ✅ `setup-6-ghc.sh`: Syntax OK
- ✅ `setup-6-cc.sh`: Syntax OK (unchanged, verified for safety)

## Success Criteria

### For New Deployments (Whitelist Approach)

- [x] Sync workflow uses whitelist approach to include only necessary files
- [x] Whitelist includes `.github/prompts/` (useful for GitHub Copilot users)
- [x] Whitelist includes plugin content, knowledge files, workflows, user-facing docs
- [x] Whitelist includes setup scripts (`setup-6-*.sh`)
- [x] Whitelist includes marketplace metadata
- [x] Whitelist excludes `.github/workflows/` (entire directory)
- [x] Whitelist excludes `.github/scripts/` (entire directory)
- [x] Setup scripts use whitelist approach to install only necessary files

### For Existing Deployments (Cleanup)

- [x] Sync workflow deletes existing unnecessary directories from nablarch/nabledge
  - `.github/workflows/` (entire directory)
  - `.github/scripts/` (entire directory)
- [x] Setup scripts detect and remove previously installed unnecessary files from user environments

## Notes

- Setup script `setup-6-cc.sh` was not modified as it doesn't install `.github/` directory (Claude Code specific)
- The whitelist approach is more maintainable than blacklist, ensuring only approved directories are distributed
- This change addresses nablarch/nabledge#7

---

**Co-Authored-By**: Claude Sonnet 4.5 <noreply@anthropic.com>
