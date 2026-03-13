# Expert Review: DevOps Engineer

**Date**: 2026-03-13
**Reviewer**: AI Agent as DevOps Engineer
**Files Reviewed**: 1 file (.github/workflows/collect-metrics.yml)

## Overall Assessment

**Rating**: 3/5
**Summary**: Functional workflow with good practices (idempotent commit, minimal permissions, workflow_dispatch), but missing `set -e` and timeout. Both fixed before merge.

## Key Issues

### High Priority

1. **No `set -e` in collect step**
   - Description: Multi-line `run` blocks don't guarantee failure propagation; partial failures could commit incomplete metrics
   - Decision: Implement Now
   - Reasoning: Easy fix, important for data integrity

### Medium Priority

2. **No job timeout**
   - Description: Hung script could consume runner minutes for up to 6 hours
   - Decision: Implement Now
   - Reasoning: `timeout-minutes: 10` is trivial to add and operationally important

3. **Direct push to main**
   - Description: Automated commits to main; if branch protection is enabled this will fail silently
   - Decision: Defer to Future
   - Reasoning: Branch protection is not currently enforced; metrics auto-update pattern is conventional

4. **No failure notification**
   - Description: Scheduled job failures go unnoticed for a week
   - Decision: Defer to Future
   - Reasoning: Failure is visible in Actions tab; acceptable for non-critical metrics job

5. **actions/checkout not pinned to SHA**
   - Decision: Defer to Future — supply chain risk is low for this internal tooling workflow

### Low Priority

6. **NABLEDGE_SYNC_TOKEN optional handling**
   - Confirmed: script handles missing token gracefully (skips adoption section)

## Positive Aspects

- `permissions: contents: write` scoped to job only — minimal and correct
- `workflow_dispatch` enables manual testing and recovery
- Bot identity (`github-actions[bot]`) is correct pattern
- Idempotent commit step (`git diff --staged --quiet || git commit`) prevents empty commits
- JST equivalent noted in cron comment — helpful for Japanese team

## Recommendations

- Add `timeout-minutes` to all scheduled workflows in this repo as a standard practice
- Consider Dependabot for Actions version updates long-term
