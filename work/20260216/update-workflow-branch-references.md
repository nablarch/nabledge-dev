# Update Workflow Branch References

## What was done

Updated `.github/workflows/sync-to-nabledge.yml` to align with new branch structure after branch rename (main→release, develop→main).

### Changed files
- `.github/workflows/sync-to-nabledge.yml`
  - Line 6: Trigger branch changed from `refactor-extract-workflow-scripts` to `release`
  - Line 25: Checkout ref changed from `test-to` to `main`
  - Line 47: Push target changed from `test-to` to `main`

### Branch strategy
- **main**: Development branch (receives ongoing work, merged via PRs)
- **release**: Release branch (ready for deployment)

The workflow triggers when changes are pushed to the release branch in nabledge-dev, and deploys to the main branch in nablarch/nabledge repository.

## Results

### Test Deployment
Successfully tested deployment to test-to branch:
- Workflow run: https://github.com/nablarch/nabledge-dev/actions/runs/22049794371
- Deployment target: test-to branch in nablarch/nabledge
- Status: ✅ All steps succeeded

### Verification Results
1. ✅ Marketplace structure deployed correctly
2. ✅ setup-6-cc.sh script works (generates settings.json)
3. ✅ setup-6-ghc.sh script works (copies skill to .claude/skills/)
4. ✅ All skill files properly structured

### Production Configuration
Set final configuration:
- Trigger: release branch
- Deploy to: main branch (nablarch/nabledge)

Commits:
- 349a313: Test configuration
- eb2c509: Production configuration

PR #25 created: https://github.com/nablarch/nabledge-dev/pull/25

## Next steps

1. Merge PR #25 to main
2. Merge main → release to trigger deployment
3. Verify deployment to nablarch/nabledge main branch succeeds
4. Close issue #24 after successful verification
