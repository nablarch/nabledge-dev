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

Successfully updated workflow configuration. Commit a39c34b created on branch `fix-workflow-branch-references`.

## Next steps

1. Push branch and create PR to main
2. Test deployment after merging PR (workflow will trigger on push to main)
3. Verify that deployment to release branch succeeds
4. Close issue #24 after successful verification
