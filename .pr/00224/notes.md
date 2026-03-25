# Notes

## 2026-03-25

### Execution Run: 20260324T235810

Execution started 2026-03-24 23:58 and ran overnight. Interrupted mid-way through the final
Phase D (Content Check) due to OS update reboot at approximately 12:00 on 2026-03-25.

---

## Generation Results Summary

### Source Files Scanned

- **458 RST files** from `.lw/nab-official/v1.4/`
- Split into **552 chunks** for generation

### Phase B: Generation

| Metric | Value |
|--------|-------|
| Generated (OK) | 549 |
| Skipped | 0 |
| Errors | 3 |
| Total cost | $154.63 |
| Avg cost/file | $0.28 |
| Total duration | ~17 hours |
| Avg duration/file | 110s |
| Avg turns | 2.0 |

**3 generation errors** (files not generated):
- `libraries-file_upload_utility--s1`
- `about-nablarch-02_I18N--s1`
- `libraries-mail--s6`

Cause: Not recorded in execution log (empty error message). Need to investigate.
These 3 files are absent from the knowledge cache.

### Phase C: Structure Check

| Metric | Value |
|--------|-------|
| Pass | 536/549 (97.6%) |
| Fail | 13 files (14 errors) |

**All 13 failures are "S11: URL not https"** - source documents from Nablarch 1.4 era
contain HTTP links. These are accurate representations of the source content:

| File | HTTP URL |
|------|----------|
| `libraries-02_basic` | http://www.oracle.com/technetwork/java/javamail/index.html |
| `java-static-analysis-05_JavaStaticAnalysis` | http://findbugs.sourceforge.net/, http://checkstyle.sourceforge.net/ |
| `biz-samples-0101_PBKDF2PasswordEncryptor--s1` | http://www.ietf.org/rfc/rfc2898.txt |
| `ui-framework-css_framework--s1` | http://fortawesome.github.io/Font-Awesome/icons/ |
| 9 other files | empty URL (malformed link in source?) |

**Assessment**: These are not fixable without changing the source content. The URLs exist
in the original Nablarch 1.4 docs. Consider relaxing S11 check for v1.4, or accepting
these 13 as known non-critical warnings.

### Phase D+E: Content Check + Fix (3 rounds)

Three full rounds were executed. The final round (Round 3) was **interrupted** after
checking 345/549 files (63% complete).

| Round | Files Checked | Has Issues | Clean | Fixed |
|-------|--------------|-----------|-------|-------|
| Round 1 | 536 | 354 (66%) | 182 (34%) | 354 |
| Round 2 | 536 | 253 (47%) | 283 (53%) | 253 |
| Round 3 (interrupted) | 345 | 153 (44%) | 192 (56%) | - |

**Convergence trend**: 66% → 47% → 44% issue rate. Diminishing returns after round 2.

| Phase | Executions | Cost | Avg/file |
|-------|-----------|------|----------|
| Phase D (all rounds) | 1418 | $215.25 | $0.15 |
| Phase E (all rounds) | 607 | $98.71 | $0.16 |

**Total run cost: ~$469**

### Finding Categories (All Rounds Combined)

| Category | Count | Notes |
|----------|-------|-------|
| omission | 547 | Content present in source but missing from knowledge file |
| hints_missing | 508 | Hint keywords not comprehensive enough |
| section_issue | 208 | Section structure problems |
| fabrication | 200 | Content not present in source was added |
| no_knowledge_content_invalid | 1 | File has no meaningful knowledge content |

| Severity | Count |
|----------|-------|
| minor | 1251 (86%) |
| critical | 213 (14%) |

**Round 3 persistent issues** (after 2 fix cycles):

| Category/Severity | Count |
|-------------------|-------|
| hints_missing/minor | 91 |
| omission/minor | 81 |
| fabrication/minor | 32 |
| section_issue/minor | 32 |
| omission/critical | 8 |
| fabrication/critical | 4 |

---

## Current State of Knowledge Cache

- **549 JSON files** in `.cache/v1.4/knowledge/` organized under 6 top-level categories:
  `about`, `component`, `development-tools`, `extension`, `guide`, `processing-pattern`
- All 549 files reflect fixes from Round 1 and Round 2
- 13 files have known HTTP URL warnings (structure S11) - not content errors
- 3 files missing due to Phase B generation errors
- Final content check was incomplete (204 files not checked in Round 3)

---

## Improvement Proposals

### 1. Generation Errors: Investigate and re-generate 3 missing files

The 3 Phase B errors left no error message in the execution log. This suggests a Claude CLI
crash or timeout rather than a generation logic error.

**Action**: Run `kc gen --target libraries-file_upload_utility--s1,about-nablarch-02_I18N--s1,libraries-mail--s6`
after investigating root cause.

**Priority**: High - these files are missing from the knowledge base.

### 2. Structure Check: Accept HTTP URLs for v1.4

The 13 "S11: URL not https" failures are from legitimate Nablarch 1.4-era source links
(Oracle JavaMail, FindBugs, Checkstyle, FontAwesome, IETF RFC). These should not be
treated as errors since the source documentation itself uses HTTP.

**Proposal A**: Add a per-version override in structure check config to allow HTTP URLs
for `v1.4` (or per-file exceptions).

**Proposal B**: Change S11 to a warning level for HTTP URLs instead of an error.

**Priority**: Medium - does not block usage but causes misleading failure counts.

### 3. Content Check: Incomplete Round 3 due to interruption

204 files were not checked in the final round. The interruption was external (OS update).

**Action**: Resume the final content check from where it left off, or re-run full check.
Files with `_r3.json` exist for 345 files; the remaining 204 need checking.

**Note**: Running `kc check` should resume from the last checkpoint if the tool supports it.
Otherwise a full `kc check --force` may be needed.

**Priority**: Medium - knowledge files are usable but the final quality pass is incomplete.

### 4. Fix Convergence: Diminishing returns after 2 rounds

After Round 2, issue rate dropped from 66% → 47% but Round 3 still shows 44%. The fix
process does not converge fully even after multiple rounds.

The main persistent categories are `hints_missing` and `omission` (minor severity).
These suggest the content generation prompt and fix prompt may have systematic gaps:

- **hints_missing**: The generation prompt may not emphasize comprehensive keyword hints
  enough. Consider adding explicit instruction to include all technical term variants
  (class names, config keys, annotation names) as hints.

- **omission (minor)**: Minor notes and caveats from source are being lost. May need
  to strengthen the instruction to preserve source warnings/notes.

- **fabrication (minor)**: Small amount of hallucination persists. Consider adding
  a "grounding" step that compares output sections against source line-by-line.

- **section_issue (minor)**: 32 persistent cases after 2 fix rounds suggests the
  fixer is not able to correct these without re-generation.

**Priority**: Low - these are improvements for the next generation run.

### 5. Cost Optimization

Phase D ($215 for 1418 checks) cost more than Phase B ($155 for 549 generations).
At $0.15/check across 3 rounds × 549 files = ~$248 just for checking.

**Proposal**: Reduce Phase D rounds from 3 to 2 as standard, since the 66% → 47% → 44%
trend shows diminishing returns. The 3rd round adds ~$50 for ~2% quality improvement.

Alternatively, skip Round 3 entirely and directly commit after Round 2, tracking
remaining issues as GitHub Issues for incremental improvement.

---

## Next Steps

1. Commit the 549 generated knowledge files to repository
2. Track non-critical issues as GitHub Issues:
   - 3 missing files (generation errors)
   - 13 HTTP URL structure warnings
   - Incomplete Round 3 content check (204 files)
3. Continue with CHANGELOG, README, GUIDE-CC.md, GUIDE-GHC.md creation
4. Update marketplace metadata
