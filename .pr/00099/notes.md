# Notes

## 2026-03-02 - Test Mode Execution Analysis

### Test Mode Execution Summary

Executed: `python tools/knowledge-creator/run.py --version 6 --test-mode`

**Results**:
- Generated: 21/21 files OK ✅
- Validation: 0/21 PASS ❌
  - Structure failures: 18/21
  - Content failures: 2/21
  - Errors: 1/21 (timeout)

### Split Files Analysis

**Test mode filtered** to 21 curated files from 256 total files.

**Split files in test set**:
- `libraries-tag-4.json` - Part 4 of 4 (カスタムタグのルール, タグリファレンス)
- `libraries-database-2.json` - Part 2 of 2 (現在のトランザクション〜, 7 sections total)

**Split file verification**: ✅ Both split files are correctly generated with proper section extraction

**Missing parts**: Parts 1-3 of tag, Part 1 of database are not in test set (expected behavior for curated test mode)

### Critical Issues

## ❌ CRITICAL: index.toon Format Error

**Problem**: Claude returns processing patterns wrapped in markdown code blocks (```)

**Evidence**:
```
tools/knowledge-creator/logs/v6/classify-patterns/setting-guide-CustomizeMessageIDAndMessage.json:
{
  "file_id": "setting-guide-CustomizeMessageIDAndMessage",
  "patterns": "```\n\n```"
}

tools/knowledge-creator/logs/v6/classify-patterns/blank-project-beforeFirstStep.json:
{
  "file_id": "blank-project-beforeFirstStep",
  "patterns": "```\nweb-application restful-web-service jakarta-batch nablarch-batch\n```"
}
```

**Impact**: Invalid index.toon format causes 8 S17 validation errors:
```
S17: Invalid processing_pattern '```' at line 3
S17: Invalid processing_pattern '```' at line 4
(... 6 more similar errors)
```

**Root Cause**: `tools/knowledge-creator/prompts/classify_patterns.md` includes example output in code block format:
```markdown
例:
```
nablarch-batch restful-web-service
```
```

Claude literally mimics the format including the code fence markers.

**Solution Options**:
1. **Remove code fences from prompt example** (simplest)
2. **Strip ``` from Claude output** in `step4_build_index.py:38-43`
3. **Add instruction to prompt**: "出力に```を含めないでください"

---

## Validation Errors by Category

### Structure Validation Failures (18/21 files)

#### S14: Section references not found (most common)

Files affected: 16/21 (62 total S14 errors)

**Pattern**: Generated sections reference IDs that don't exist in the knowledge file

**Root Cause Analysis** - S14 errors fall into 4 categories:

1. **External file references** (most common):
   - Example: `library`, `web_application`, `web_service`, `batch_application`
   - These are references to OTHER knowledge files, not sections within the same file
   - Validator incorrectly treats them as internal section references

2. **Backtick-wrapped terms**:
   - Example: `` `default-metrics` ``, `` `repository-dispose_object` ``
   - Pattern: Text mentions "詳細は`xxx`を参照"
   - Validator extracts `xxx` as a reference, but it's actually inline code formatting

3. **Markdown link text fragments**:
   - Example: "ガイド](https://docs.oracle.com/...)"
   - Validator's regex captures text BEFORE the closing bracket as a reference
   - False positive: link anchor text is not a section reference

4. **Long text fragments**:
   - Example: "では、パイプライン型の処理モデルに従ってすべてのデータ処理を行う。特に複数の処理方式を組み合わせて構築するシステムは、nablarch_architecture"
   - Validator's regex `(\S+)\s*を参照` captures too much text

**Conclusion**: Most S14 errors are **false positives** due to overly broad regex pattern in validator

**Files with S14 errors**:
1. about-nablarch-big_picture (7 errors)
2. about-nablarch-license (1 error)
3. about-nablarch-policy (5 errors)
4. adapters-jaxrs_adaptor (1 error)
5. adapters-micrometer_adaptor (8 errors)
6. blank-project-beforeFirstStep (3 errors)
7. cloud-native-azure_distributed_tracing (2 errors)
8. handlers-jaxrs_response_handler (6 errors)
9. http-messaging-feature_details (14 errors)
10. http-messaging-getting_started (3 errors)
11. libraries-database-2 (9 errors)
12. libraries-tag-4 (1 error)
13. nablarch-patterns-Nablarchでの非同期処理 (1 error - image file)
14. security-check (1 error)
15. setting-guide-CustomizeMessageIDAndMessage (1 error)
16. testing-framework-fileupload (3 errors)
17. toolbox-SqlExecutor (1 error)
18. web-application-client_create4 (3 errors)

#### S13: Section too short

Files affected: 2/21
- `handlers-jaxrs_response_handler`: "constraints" section (3 chars - just "なし。")
- `http-messaging-feature_details`: Multiple sections (14-47 chars)

**Root Cause**: Threshold may be too strict for genuinely short sections

#### S9: Section count mismatch

Files affected: 2/21
- `blank-project-beforeFirstStep`: 5 sections generated vs 7 in source
- `libraries-tag-4`: 5 sections generated vs 6 in source

**Root Cause**: Some source headings not converted to sections during generation

#### S15: Referenced asset file not found

Files affected: 1/21
- `nablarch-patterns-Nablarchでの非同期処理`: References image file that doesn't exist

---

### Content Validation Failures (2/21 files)

#### 1. blank-project-FirstStep

**fabricated_info** (overview section):
- Added: "初期セットアップの手順は、プロジェクトの種類によって異なります。"
- Added: "以下のプロジェクトタイプ別のセットアップ手順が用意されています："
- Added: "初期セットアップに関連する補足資料として、以下が用意されています："

**poor_hints** (overview section):
- Missing: "NablarchBatch_Dbless" (or "DB接続なし"/"DBレス")
- Missing: "ResiBatchReboot" (or "常駐バッチ再起動")
- Missing: "firststep_complement" (or "補足"/"complement")

These are explicitly listed in source toctree and should be searchable.

#### 2. nablarch-patterns-Nablarchバッチ処理パターン

**missing_info** (startup-classification section):
- Source includes link: `https://nablarch.github.io/docs/LATEST/doc/.../index.html`
- Knowledge file: Link removed, only text "Nablarchバッチでは..." remains

**bad_section_split** (io-classification section):
- Section exceeds 2000 chars but not split by h3
- Source has 4 h3 subsections: FILE to DB, DB to DB, DB to FILE, 上記以外の組み合わせ
- Knowledge file: Merged into single section

**poor_hints** (io-classification section):
- Missing: "FILE to FILE" (important keyword, appears as h3 in source)

#### 3. nablarch-patterns-Nablarchアンチパターン

**validation_error**:
- Claude -p timeout after 120 seconds
- Cannot determine content quality due to timeout

---

## Issue Checklist

### Priority 1: Critical (Blocking)

- [ ] **P1-1**: Fix index.toon format error (``` in processing_patterns)
  - Method: Remove code fences from prompt example OR strip ``` from output
  - File: `tools/knowledge-creator/prompts/classify_patterns.md` or `step4_build_index.py`
  - Impact: 8 S17 errors, prevents index.toon from being valid

### Priority 2: High (Quality Issues)

- [ ] **P2-1**: Fix fabricated info generation
  - Issue: Step 3 (generation) adds explanatory text not in source
  - File: Generation prompt for blank-project-FirstStep
  - Fix: Add explicit instruction "ソースファイルにない説明文を追加しないでください"

- [ ] **P2-2**: Fix poor hints - missing keywords
  - Issue: Important keywords from source not included in hints
  - Files: blank-project-FirstStep, nablarch-patterns-Nablarchバッチ処理パターン
  - Fix: Improve hint extraction logic to capture toctree entries and h3 headings

- [ ] **P2-3**: Fix bad section splitting
  - Issue: Sections >2000 chars not split by h3 despite h3 existing in source
  - File: nablarch-patterns-Nablarchバッチ処理パターン (io-classification)
  - Fix: Enforce h3 splitting rule in generation prompt

- [ ] **P2-4**: Fix missing info (links)
  - Issue: URLs and links removed from knowledge files
  - File: nablarch-patterns-Nablarchバッチ処理パターン
  - Fix: Ensure links are preserved in generation

### Priority 3: Medium (Validation Issues)

- [ ] **P3-1**: Fix S14 validation regex pattern
  - Issue: Overly broad regex `(\S+)\s*を参照` captures too much
  - Impact: 16/21 files, 62 total false positive S14 errors
  - Root causes:
    - External file refs: `library`, `web_application` (not section IDs)
    - Backtick terms: `` `default-metrics` `` (inline code, not refs)
    - Markdown links: "ガイド](URL)" (link text, not refs)
    - Long fragments: Multi-sentence text before "を参照"
  - Fix options:
    1. Tighten regex to match only kebab-case IDs: `([a-z0-9-]+)\s*を参照`
    2. Add exclusions for backtick-wrapped terms
    3. Handle markdown link patterns separately
    4. Implement whitelist of known external references

- [ ] **P3-2**: Review S13 threshold for section length
  - Issue: Legitimate short sections flagged as errors
  - Example: "constraints" section with just "なし。" (none)
  - Fix: Consider lowering threshold or special case handling

- [ ] **P3-3**: Fix S15 asset file references
  - Issue: Referenced image file doesn't exist
  - File: nablarch-patterns-Nablarchでの非同期処理
  - Check: Are assets supposed to be copied? Or is reference incorrect?

- [ ] **P3-4**: Fix S9 section count mismatches
  - Issue: Some source headings not converted to sections
  - Files: blank-project-beforeFirstStep, libraries-tag-4
  - Investigate: Why are sections being skipped during generation?

### Priority 4: Low (Improvements)

- [ ] **P4-1**: Increase content validation timeout
  - Issue: 1 file times out after 120 seconds
  - File: nablarch-patterns-Nablarchアンチパターン
  - Fix: Increase timeout or optimize validation prompt

---

## File-by-File Status

| File ID | Generation | Structure | Content | Notes |
|---------|-----------|-----------|---------|-------|
| about-nablarch-big_picture | ✅ OK | ❌ S14(7) | ⏭️ skip | 7 external refs |
| about-nablarch-license | ✅ OK | ❌ S14(1) | ⏭️ skip | 1 asset ref |
| about-nablarch-policy | ✅ OK | ❌ S14(5) | ⏭️ skip | 5 external refs |
| adapters-jaxrs_adaptor | ✅ OK | ❌ S14(1) | ⏭️ skip | 1 external ref |
| adapters-micrometer_adaptor | ✅ OK | ❌ S14(8) | ⏭️ skip | 8 external refs |
| blank-project-FirstStep | ✅ OK | ✅ pass | ❌ fabricated+poor_hints | **Content issues** |
| blank-project-beforeFirstStep | ✅ OK | ❌ S9+S14(3) | ⏭️ skip | Section count mismatch |
| cloud-native-azure_distributed_tracing | ✅ OK | ❌ S14(2) | ⏭️ skip | 2 external refs |
| handlers-jaxrs_response_handler | ✅ OK | ❌ S13+S14(6) | ⏭️ skip | Short section + refs |
| http-messaging-feature_details | ✅ OK | ❌ S13(7)+S14(14) | ⏭️ skip | Many short sections + refs |
| http-messaging-getting_started | ✅ OK | ❌ S14(3) | ⏭️ skip | 3 external refs |
| libraries-database-2 | ✅ OK | ❌ S14(9) | ⏭️ skip | Split file Part 2, 9 refs |
| libraries-tag-4 | ✅ OK | ❌ S9+S13+S14(1) | ⏭️ skip | Split file Part 4 |
| nablarch-patterns-Nablarchでの非同期処理 | ✅ OK | ❌ S15(1) | ⏭️ skip | Missing image asset |
| nablarch-patterns-Nablarchアンチパターン | ✅ OK | ✅ pass | ❌ timeout | **Validation timeout** |
| nablarch-patterns-Nablarchバッチ処理パターン | ✅ OK | ✅ pass | ❌ missing+split+hints | **Content issues** |
| security-check | ✅ OK | ❌ S14(1) | ⏭️ skip | 1 external ref |
| setting-guide-CustomizeMessageIDAndMessage | ✅ OK | ❌ S14(1) | ⏭️ skip | 1 external ref |
| testing-framework-fileupload | ✅ OK | ❌ S14(3) | ⏭️ skip | 3 external refs |
| toolbox-SqlExecutor | ✅ OK | ❌ S14(1) | ⏭️ skip | 1 external ref |
| web-application-client_create4 | ✅ OK | ❌ S14(3) | ⏭️ skip | 3 external refs |

**Legend**:
- ✅ pass/OK: No errors
- ❌: Has errors
- ⏭️ skip: Content validation skipped due to structure errors

---

## Additional Findings from Detailed Logs

### S14 Error Distribution by Type (estimated)

Analyzed all 62 S14 errors across 16 files:

| Error Type | Count (est.) | Example | False Positive? |
|------------|--------------|---------|-----------------|
| External file refs | ~30 | `library`, `web_application`, `validation` | ✅ Yes |
| Backtick terms | ~15 | `` `default-metrics` ``, `` `repository-xxx` `` | ✅ Yes |
| Markdown link text | ~5 | "ガイド](URL)" fragments | ✅ Yes |
| Long text fragments | ~7 | Multi-sentence captures | ✅ Yes |
| Legitimate errors | ~5 | Missing section IDs | ❌ No |

**Conclusion**: ~90% of S14 errors are false positives caused by overly broad regex

### Files with Most S14 Errors

| File | S14 Count | Other Errors | Total |
|------|-----------|--------------|-------|
| http-messaging-feature_details | 14 | S13(7) | 21 |
| libraries-database-2 | 9 | - | 9 |
| adapters-micrometer_adaptor | 8 | - | 8 |
| about-nablarch-big_picture | 7 | - | 7 |
| handlers-jaxrs_response_handler | 6 | S13(1) | 7 |

### Structure Validation Summary

**Total structure errors**: 83 errors across 18 files
- S14: 62 errors (75% of total, mostly false positives)
- S13: 13 errors (16% of total, short sections)
- S9: 2 errors (2% of total, section count mismatch)
- S15: 1 error (1% of total, missing asset)
- Other: 5 errors (6% of total)

**Real quality issues**: Estimated ~10-15 errors after filtering false positives

---

## Decision: Next Steps

### Immediate Actions (This PR)

Focus on **Critical (P1)** and **High (P2)** priority issues that affect quality:

1. ✅ **P1-1**: Fix index.toon format (CRITICAL)
2. ✅ **P2-1**: Fix fabricated info generation
3. ✅ **P2-2**: Fix poor hints extraction
4. ✅ **P2-3**: Fix bad section splitting
5. ✅ **P2-4**: Fix missing info (links)

### Future Work (Separate Issues/PRs)

Defer **Medium (P3)** and **Low (P4)** issues:

- **P3-1 to P3-4**: Validation logic improvements
  - Most S14 errors are false positives (external refs)
  - Need design decision on how to handle cross-file references
  - Create separate issue for validation improvements

- **P4-1**: Timeout handling
  - Rare occurrence (1/21 files)
  - Can be addressed after main quality issues are fixed

### Rationale

The P1-P2 issues affect the actual quality of generated knowledge files:
- Users will see fabricated information
- Users cannot search for important keywords
- Large sections are not properly organized
- Important links are missing

The P3-P4 issues are validation/tooling concerns:
- Don't affect end-user experience
- Require design decisions about architecture
- Can be improved iteratively

---

## Test Mode Coverage

**Test mode files** (21 curated files):
- Covers diverse file types: component, setup, about, guide, check, processing-pattern, development-tools
- Includes split files (tag-4, database-2)
- Good representation of generation scenarios

**Not covered in test mode**:
- Part 1-3 of split files
- Remaining 235+ files
- Will need full run validation after fixes

---

## Tools & Scripts Reference

**Run test mode**:
```bash
python tools/knowledge-creator/run.py --version 6 --test-mode
```

**Check logs**:
- Sources: `tools/knowledge-creator/logs/v6/sources.json`
- Classified: `tools/knowledge-creator/logs/v6/classified.json`
- Summary: `tools/knowledge-creator/logs/v6/summary.json`
- Pattern classification: `tools/knowledge-creator/logs/v6/classify-patterns/*.json`

**Key files to modify**:
- Generation prompts: `tools/knowledge-creator/prompts/`
- Steps: `tools/knowledge-creator/steps/step*.py`
- Index building: `tools/knowledge-creator/steps/step4_build_index.py`
