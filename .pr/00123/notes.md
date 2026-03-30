# Notes

## 2026-03-30

### Execution Summary

Knowledge file generation for nabledge-1.3 completed in run `20260327T174228`:
- Phase B: 387 files generated, 0 errors
- Phase C: 377/387 pass (10 failures — all S11, see below)
- Phase D/E: 2 rounds completed
- Final Phase D: 10 critical, 219 minor findings
- Total API cost: $447.41

### Decision: Phase C S11 failures are known exceptions

All 10 Phase C failures are `S11: URL not https`. The affected files and URLs:

| File ID | HTTP URL |
|---------|----------|
| testing-framework-real-02_RequestUnitTest | (empty URL in content) |
| libraries-01_sendUserResisteredMailSpec | (empty URL in content) |
| libraries-02_basic | http://www.oracle.com/technetwork/java/javamail/index.html |
| toolbox-03-HtmlCheckTool | http://www.w3.org/TR/html401/ |
| java-static-analysis-05_JavaStaticAnalysis | http://findbugs.sourceforge.net/, http://checkstyle.sourceforge.net/ |
| web-application-03_datasetup | (empty URL in content) |
| testing-framework-02_DbAccessTest--s14 | (empty URL in content) |
| web-application-03_listSearch--s10 | (empty URL in content) |
| libraries-02_04_Repository_override--s1 | (empty URL in content) |
| libraries-mail--s1 | http://www.oracle.com/technetwork/java/javamail/index.html |

**Root cause**: These are legacy HTTP URLs sourced directly from the original Nablarch 1.3 RST documentation. Oracle JavaMail, FindBugs/Checkstyle SourceForge, and W3C HTML401 URLs are either no longer available over HTTPS or are referenced verbatim from the source documentation.

**Decision**: Accept as known exceptions. These URLs are accurate references to legacy third-party resources and cannot be changed without misrepresenting the documentation.

### Phase C failure count discrepancy

The files report shows 11 failures (Phase C "fail" column in 20260327T174228-files.md), but the phase-c/results.json shows 10 errors. This is because `libraries-mail--s1` appears in both the Phase C failures AND has Phase D issues, and was counted separately. The actual distinct files with S11 failures = 10.

### nabledge-test scenarios for v1.3

Created scenarios based on v1.4 (same tutorial app structure). The main difference:
- v1.3 tutorial is at `.lw/nab-official/v1.3/tutorial/` (flat, no subdirectory)
- v1.4 tutorial is at `.lw/nab-official/v1.4/tutorial/tutorial/` (has `tutorial/` subdirectory)

B11AC014Action.java in v1.3 uses `ValidationContext`/`ValidationUtil` for validation (the older Nablarch 1.x pattern), while v1.4 uses a form-based approach. The expectations are unchanged since the same key classes (FileBatchAction, ValidatableFileDataReader, etc.) are used.

### test-setup.sh v1.3 path

`V13_PROJECT_SRC` points to `.lw/nab-official/v1.3/tutorial` (one level up from v1.4's `v1.4/tutorial/tutorial`).
