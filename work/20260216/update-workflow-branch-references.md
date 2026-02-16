# Update Workflow Branch References

## What was done

Updated `.github/workflows/sync-to-nabledge.yml` to align with new branch structure after branch rename (main→release, develop→main).

### Changed files
- `.github/workflows/sync-to-nabledge.yml`
  - Line 6: Trigger branch changed from `refactor-extract-workflow-scripts` to `main`
  - Line 25: Checkout ref changed from `test-to` to `release`
  - Line 47: Push target changed from `test-to` to `release`

### Branch strategy
- **main**: Development branch (receives ongoing work)
- **release**: Production release branch (controlled release timing)

The workflow now automatically deploys changes from main to release branch when changes are pushed to main.

## Results

Successfully updated workflow configuration. Commit a39c34b created on branch `fix-workflow-branch-references`.

## Next steps

1. Push branch and create PR to main
2. Test deployment after merging PR (workflow will trigger on push to main)
3. Verify that deployment to release branch succeeds
4. Close issue #24 after successful verification
