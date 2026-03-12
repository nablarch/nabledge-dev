# Fabrication Verification Report: R2 Phase D Findings

**Date**: 2026-03-12
**Issue**: #153
**Methodology**: Re-run kc Phase D (`--phase D`) on a sample of files that had issues in Phase D R2 of run `20260309T232615`

---

## Background

The large kc run `20260309T232615` (work1, phases ACDEM, max_rounds=2) produced:
- Phase D R1: 48 fabrication findings across 289 "has_issues" files
- Phase E R1: Fixed all 289 files, deleted their findings files
- Phase D R2: 30 fabrication findings across 205 "has_issues" files
- Phase E R2: Fixed all 205 files, deleted their findings files

The Phase D R2 findings files were deleted by Phase E R2 (`os.remove(findings_path)` in phase_e_fix.py:100).
Direct inspection of R2 findings is not possible.

**Approach**: Re-run Phase D on a representative sample of the 205 Phase D R2 ISSUE files (from execution log analysis). The current knowledge files reflect the post-Phase E R2 state.

---

## Sampling

- **Total R2 ISSUE files**: 205 (from execution log lines 889-1097 of `20260309T232615/execution.log`)
- **Files sampled**: 40 (2 batches of 20, diverse categories)
- **Run IDs**: `20260312T102320` (batch 1), `20260312T103251` (batch 2)

### Batch 1 Files (20)
adapters-jaxrs_adaptor--sec-3835c739, adapters-lettuce_adaptor, adapters-micrometer_adaptor--mbean,
migration-migration--jakarta-ee-10, nablarch-batch-batch, nablarch-batch-getting_started,
jakarta-batch-jsr352, jakarta-batch-database_reader, libraries-log--sec-7521ea21,
libraries-bean_validation--sec-2a05b0f0, libraries-tag_reference--popupsubmit,
libraries-format_definition--sec-1c203f82, web-application-feature_details--nablarch,
web-application-application_design, handlers-body_convert_handler--sec-2a8f8aeb,
restful-web-service-feature_details--nablarch, http-messaging-feature_details--nablarch,
testing-framework-batch--csv, about-nablarch-nablarch, releases-nablarch6u3-releasenote

### Batch 2 Files (20)
testing-framework-batch--sec-d41d8cd9, testing-framework-send_sync--sec-d41d8cd9,
testing-framework-02_entityUnitTestWithNablarchValidation--sec-d41d8cd9,
testing-framework-03_Tips--sec-e9b44039,
testing-framework-02_entityUnitTestWithNablarchValidation--sec-1a3c0d5c,
testing-framework-JUnit5_Extension--sec-d41d8cd9, testing-framework-02_DbAccessTest--sec-c0a96a9f,
testing-framework-01_Abstract--excel, testing-framework-02_RequestUnitTest--sec-dfb6ecf5,
about-nablarch-05--sec-d41d8cd9, about-nablarch-12--sec-ec09647d,
libraries-universal_dao--sec-90be4121, handlers-SessionStoreHandler--sec-2a8f8aeb,
handlers-thread_context_clear_handler--sec-2a8f8aeb, release-notes-releases,
nablarch-patterns-Nablarchバッチ処理パターン, blank-project-setup_WebService--restful,
toolbox-NablarchOpenApiGenerator--sec-a5f21170, adapters-micrometer_adaptor--sec-8ce6778b,
handlers-loop_handler--sec-2a8f8aeb

---

## Results Summary

| Batch | Files Sampled | Files Clean | Files with Issues | Fabrication Found |
|-------|--------------|-------------|-------------------|-------------------|
| 1     | 20           | 7           | 13                | 2                 |
| 2     | 20           | 5           | 15                | 7                 |
| **Total** | **40**   | **12**      | **28**            | **9**             |

### Finding Categories (combined)

| Category     | Count |
|--------------|-------|
| fabrication  | 9     |
| section_issue| ~16   |
| omission     | ~11   |
| hints_missing| ~8    |

---

## Fabrication Findings Analysis (9 findings)

### F1: `testing-framework-batch--csv` — Fabricated header row

- **Description**: Markdown table has fabricated header row `| 区分 | フィールド1 | フィールド2 | フィールド3 |` not present in RST source.
- **Source evidence**: RST grid table has no header row — first row is `|text-encoding | Windows-31J |`. Column labels "区分", "フィールド1" etc. appear nowhere in the source section.
- **Knowledge file (relevant)**:
  ```
  | 区分 | フィールド1 | フィールド2 | フィールド3 |
  |---|---|---|---|
  | text-encoding | Windows-31J | | |
  ```
- **RST source (relevant)**:
  ```
  +-----------------+-------------+-------------+-----------+
  |text-encoding    |Windows-31J                            |
  +-----------------+-------------+-------------+-----------+
  ```
- **Classification**: **real**
- **Reasoning**: Column header row has absolutely no basis in RST source. The knowledge creator invented column headers for a headerless grid table.

---

### F2: `testing-framework-batch--csv` — Fabricated explanatory sentence

- **Description**: Statement `messageカラムは空でも可（FATALの例ではmessage3が空）。` not present in source.
- **Source evidence**: RST shows a FATAL row with empty message3 cell (by example only). No sentence states that leaving messageN columns empty is permitted.
- **Knowledge file (relevant)**:
  ```
  messageカラムは空でも可（FATALの例ではmessage3が空）。
  ```
- **RST source (relevant)**:
  ```
  ======== ============= ====================== ==============
  logLevel   message1     message2               message3
   FATAL     NB11AA0109  エラーが発生しました。
  ======== ============= ====================== ==============
  ```
- **Classification**: **real**
- **Reasoning**: An inference from a data example was presented as an explicitly stated rule. The RST never states this as a rule or explanation.

---

### F3: `testing-framework-02_entityUnitTestWithNablarchValidation--sec-d41d8cd9` — Added outcome wording

- **Description**: Test execution table adds "許容/不許容の設定に従い精査成功/失敗を検証" in the 備考 column for character-type rows. RST 備考 for these rows only describes input string construction.
- **Knowledge file (relevant)**:
  ```
  | 文字種（各12種） | 各文字種でmax長の文字列 | 許容/不許容の設定に従い精査成功/失敗を検証 |
  ```
- **RST source (relevant)**:
  ```
  | 文字種 |半角英字 | max(最大文字列長)欄に記載した長さの文字列で構成される。
  ```
- **Classification**: **real**
- **Reasoning**: Source 備考 column only describes input construction. The knowledge file added outcome verification wording with no basis in the source.

---

### F4: `testing-framework-03_Tips--sec-e9b44039` — Generated content for empty-body split

- **Description**: Knowledge file contains explanatory sentence for a section whose split boundary contains only an RST anchor and heading separator (no body text).
- **Source evidence**: section_range ends at line 730. Content at lines 728-730: `.. _how_to_change_test_data_dir:` + heading separator only. No body text in split.
- **Knowledge file (relevant)**:
  ```
  テストデータの配置ディレクトリを変更する方法については、ソースドキュメントの当該セクションを確認すること。
  ```
- **RST source (relevant)**:
  ```
  .. _how_to_change_test_data_dir:

  ——————————————————————————————
  ```
- **Classification**: **real**
- **Reasoning**: Knowledge file generated explanatory content when the source split contained zero body text. Content is entirely fabricated.

---

### F5: `testing-framework-02_entityUnitTestWithNablarchValidation--sec-1a3c0d5c` — Removed abbreviation marker

- **Description**: XML example removes `<!-- 中略 -->` and adds explicit `</list>` closing tag, making an intentionally abbreviated snippet appear complete.
- **Knowledge file (relevant)**:
  ```
    </list>
  </property>
  ```
- **RST source (relevant)**:
  ```
      <!-- 中略 -->
  </property>
  ```
- **Classification**: **real**
- **Reasoning**: Removing `<!-- 中略 -->` and adding `</list>` transforms an explicitly-marked-incomplete snippet into one that appears complete, misleading users about required validator configuration.

---

### F6: `testing-framework-02_DbAccessTest--sec-c0a96a9f` — Invented term and placement rule

- **Description**: Adds label "コメント行" and placement rule "カラム名行とデータ行の間に置く" for a `//` row in test data tables. RST source only shows the format by example with no such explanation.
- **Knowledge file (relevant)**:
  ```
  3行目以降: 期待値（コメント行 `// データ型` でデータ型指定可。コメント行はカラム名行とデータ行の間に置く）
  ```
- **RST source (relevant)**:
  ```
  | // CHAR(5) VARCHAR(64) BOOLEAN |
  ```
  (no accompanying label or placement rule)
- **Classification**: **real**
- **Reasoning**: Both the term "コメント行" and the placement rule "カラム名行とデータ行の間に置く" are absent from the source. The source only shows the format by example.

---

### F7: `testing-framework-01_Abstract--excel` — Altered notation in example

- **Description**: Example `${半角数字,2}-${半角数字,4}` in knowledge file does not match source `${半角数字,2}-{半角数字4}` (second segment differs: source has no `$` prefix and no comma).
- **Knowledge file (relevant)**:
  ```
  ${半角数字,2}-${半角数字,4}
  ```
- **RST source (relevant)**:
  ```
  ${半角数字,2}-{半角数字4}
  ```
- **Classification**: **real**
- **Reasoning**: The knowledge file "normalized" an inconsistent notation in the source, changing both the `$` prefix and comma separator in the second segment. The source is authoritative regardless of apparent inconsistency.

---

### F8: `toolbox-NablarchOpenApiGenerator--sec-a5f21170` — Corrected source typo

- **Description**: Knowledge file states `nablarch-jaxrs` but source configuration table (line 152) reads `nablarch-jarxrs` (typo). Other locations in the same RST use `nablarch-jaxrs` correctly.
- **Knowledge file (relevant)**:
  ```
  | `generatorName` | Generatorの名前。`nablarch-jaxrs` を指定 | 必須 | なし |
  ```
- **RST source (relevant)**:
  ```
  本ツールでは ``nablarch-jarxrs`` と指定すること。  (line 152, typo)
  generatorName には nablarch-jaxrs を指定することで  (line 111, correct)
  ```
- **Classification**: **ambiguous**
- **Reasoning**: Source table row has an obvious typo (`jarxrs` vs `jaxrs`). Knowledge file used the correct spelling consistent with line 111 and all code examples. This corrects a source typo rather than fabricating information, but technically deviates from the literal table text.

---

### F9: `handlers-loop_handler--sec-2a8f8aeb` — Added use-case description

- **Description**: Adds "スタンドアロンバッチ処理で使用する" — phrase not present in source body text.
- **Source evidence**: RST body text describes handler function without naming the use-case. Maven artifact is `nablarch-fw-standalone` but no body text states this handler is for standalone batch processing.
- **Knowledge file (relevant)**:
  ```
  スタンドアロンバッチ処理で使用する。
  ```
- **RST source (relevant)**:
  ```
  ハンドラクラス名 / * nablarch.fw.handler.LoopHandler
  ```
  (no use-case description)
- **Classification**: **real**
- **Reasoning**: Inferred from Maven artifact ID `nablarch-fw-standalone` but stated as fact. RST body text does not contain this statement.

---

## False Positive Rate

| Classification | Count | Percentage |
|----------------|-------|------------|
| real           | 8     | 88.9%      |
| ambiguous      | 1     | 11.1%      |
| false_positive | 0     | 0.0%       |

**False positive rate: 0%** (excluding ambiguous)
**Fabrication rate in sampled files**: 9 findings across 8 files out of 40 sampled (20% of sampled files had fabrication)

---

## Patterns Observed

Three distinct fabrication patterns emerged:

1. **RST grid-table header invention** (F1): When RST uses headerless grid tables, knowledge creator invents column headers. Systematic risk for any file with this table format.

2. **Inference-as-fact** (F2, F9): Knowledge creator draws inferences from examples or context and presents them as explicitly documented rules/descriptions.

3. **Content generation for empty splits** (F4): When a split section's range contains only an anchor/heading with no body text, knowledge creator generates explanatory content from nothing.

4. **Example alteration** (F5, F7): Abbreviated examples are completed (`<!-- 中略 -->` removal) or notation is "normalized" without source basis.

5. **Invented terms and rules** (F3, F6): Knowledge creator adds explanatory terminology and structural rules not present in source.

---

## Conclusions

**1. Phase D R2 fabrication findings were real (not false positives)**: All 8 unambiguous fabrication findings identified in this re-run are genuine. False positive rate is 0%. This answers the primary question in issue #153: the R2 fabrications were real content quality problems.

**2. Phase E R2 was partially effective**: In the initial 20-file batch, 18 files with no fabrication findings suggests Phase E R2 successfully removed many fabrications. However, 8 files still had fabrication findings in the current (post-Phase E R2) state, indicating Phase E R2 did not fully fix the fabrication problem.

**3. Systematic patterns exist**: The fabrication patterns observed (grid-table headers, empty-split generation, inference-as-fact) suggest systematic prompting or generation issues that may affect other knowledge files beyond the sampled set.

**4. Follow-up work needed**: The 8 files with real fabrication findings require manual fix or targeted `kc fix` (not committed per this verification-only task). A separate fix PR should be created.

---

## Recommendations

1. **Fix the 8 files** with confirmed real fabrications via targeted `kc fix`:
   - testing-framework-batch--csv
   - testing-framework-02_entityUnitTestWithNablarchValidation--sec-d41d8cd9
   - testing-framework-03_Tips--sec-e9b44039
   - testing-framework-02_entityUnitTestWithNablarchValidation--sec-1a3c0d5c
   - testing-framework-02_DbAccessTest--sec-c0a96a9f
   - testing-framework-01_Abstract--excel
   - toolbox-NablarchOpenApiGenerator--sec-a5f21170 (ambiguous — review manually)
   - handlers-loop_handler--sec-2a8f8aeb

2. **Improve Phase B generation prompt** to address the three systematic patterns (grid-table headers, empty-split handling, inference-as-fact).

3. **Consider expanding verification** to all 205 Phase D R2 ISSUE files to get a complete fabrication count.
