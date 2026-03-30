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

---

## 2026-03-26

### Issue #230 Fix Impact Analysis

With #230 merged (commit de2cbae9), the split logic bugs are fixed. Analysis of the impact:

#### v5/v6 Affected Files (1 each)

| Version | File ID | Lines | Status |
|---------|---------|-------|--------|
| v5 | `blank-project-FirstStepContainer--s1` | 13 | Has cache, wrong ID |
| v6 | `blank-project-FirstStepContainer--s1` | 13 | Has cache, wrong ID |

Both have `total_parts=1` with `--s1` suffix — the split bug manifestation. After #230 fix,
these become single entries `blank-project-FirstStepContainer` (no suffix). `kc regen` will
update catalog (Phase A), delete stale `--s1` cache, and regenerate under new ID.

#### v1.4 Affected Files (7 total)

**Split bug only** (4 files):

| File ID | Lines in part 1 | Old catalog structure |
|---------|-----------------|----------------------|
| `libraries-01_FailureLog--s1` | 3 | --s1(3) + --s2(807) → after fix: single entry |
| `about-nablarch-top-nablarch--s1` | 11 | --s1(11) + --s2(847) + --s3(48) → after fix: may have different grouping |
| `web-application-02_flow--s1` | 13 | --s1(13), total_parts=1 → after fix: single entry |
| `web-application-09_confirm_operation--s1` | 16 | --s1(16), total_parts=1 → after fix: single entry |

**Split bug + timeout** (2 files — timed out in original run AND affected by split bug):

| File ID | Lines | Note |
|---------|-------|------|
| `libraries-file_upload_utility--s1` | 392 | total_parts=1, timed out at 31min |
| `about-nablarch-02_I18N--s1` | 168 | total_parts=1, timed out at 33min |

**Timeout only** (1 file):

| File ID | Lines | Note |
|---------|-------|------|
| `libraries-mail--s6` | 394 | Part 2/2 of mail.rst, timed out at 31min |

### S11 Investigation and Decision

S11 check validates that `official_doc_urls` entries start with `https://`.
13 v1.4 files fail S11 after original generation:

- 4 files: Real HTTP URLs from 2014-era source docs (Oracle, FindBugs, Checkstyle, FontAwesome, IETF)
- 9 files: Empty string in `official_doc_urls` — likely AI inserting `""` for missing URLs

**Decision**: Keep S11 check as-is. Two separate approaches:
- Real HTTP URLs: Accept as known issues for v1.4 era docs. Track as GitHub Issue.
- Empty URLs: Fix by removing empty strings during Phase E (content fix). The fix prompt should
  be explicit about not including empty strings in `official_doc_urls`.

**Not implementing v1.4 bypass**: S11 check is valuable for detecting non-https URLs in new
content. A bypass would mask real issues. Better to track the 13 known v1.4 issues explicitly.

### kc Regen Commands (for user to run)

```bash
# Run from repository root (so CC settings in .claude/settings.json take effect)
# Use --target repeatedly for multiple targets (comma-separated does NOT work)

# Step 1: v5 regen (1 file affected by split bug)
./tools/knowledge-creator/kc.sh regen 5 --target blank-project-FirstStepContainer

# Step 2: v6 regen (1 file affected by split bug)
./tools/knowledge-creator/kc.sh regen 6 --target blank-project-FirstStepContainer

# Step 3: v1.4 regen (7 targets: 4 split bug + 2 split bug+timeout + 1 timeout-only)
# Consider --max-rounds 2 for better quality given earlier high issue rates
./tools/knowledge-creator/kc.sh regen 1.4 \
  --target libraries-01_FailureLog \
  --target about-nablarch-top-nablarch \
  --target web-application-02_flow \
  --target web-application-09_confirm_operation \
  --target libraries-file_upload_utility \
  --target about-nablarch-02_I18N \
  --target libraries-mail--s6
```

After regen completes: review reports, then commit all generated files.

---

## 最終検証 残存問題の分析 (2026-03-30)

Round 3最終検証（345/549ファイル）で残存した336件の軽微問題と19件の重大問題について分析する。

---

### 1. 重大 (Critical) 19件 — 全件詳細

重大問題は「AIが誤った回答をする」または「重要な実装情報が完全に欠落する」ケース。

**[1] handlers-KeitaiAccessHandler--s1 / fabrication / sections.s1 — NablarchTagHandlerの配置ルール行**

知識ファイルs1のハンドラキュー配置順テーブルで、NablarchTagHandlerの説明に `nablarch_sumbit` というパラメータ名を使用しているが、ソースファイルでは一貫して `nablarch_sumit`（bなし）が使われている。`nablarch_sumbit` はソースファイルのどこにも存在しない。

> Evidence: ソースの関連するハンドラ表: 「本ハンドラで設定したリクエストパラメータ **nablarch_sumit** の値をもとに」。ハンドラ処理フロー ステップ2でも同様に「リクエストパラメータ **nablarch_sumit** の値を設定する」と記載。

---

**[2] handlers-MessageResendHandler--s1 / fabrication / s1 — 再送制御の4ケース, case 4**

Knowledge file describes case 4 as "業務処理が異常終了しエラー応答電文が未達" but the source's behavior section heading reads "業務処理が正常終了したがエラー応答電文が未達". The knowledge file changed "正常終了" to "異常終了", which contradicts the source text.

> Evidence: Source behavior section: "4. 業務処理が正常終了したがエラー応答電文が未達 / 再送要求電文を初回電文として処理する。"

---

**[3] http-messaging-03_userQueryMessageAction / omission / s1 — 電文受信時の処理**

The source Javadoc for onReceive states: "精査エラーとなった場合は、処理をロールバックしてエラー応答を送信する。" This rollback-on-validation-error behavior is substantive implementation information not captured anywhere in s1's prose.

> Evidence: Source Javadoc: 「精査エラーとなった場合は、処理をロールバックしてエラー応答を送信する。」

---

**[4] libraries-02_CodeManager--s1 / omission / s9**

Missing screen display usage guidance for getName vs getShortName. The source explains when to use getName (detail screen) vs getShortName (list screen).

> Evidence: コード名称を画面表示する際は、詳細画面では完全な名称、一覧画面では略称で表示することがある。このように使用する箇所に応じてコード値の表示を変更するために、本機能では1つのコード値に対して複数のコード名称を持たせることができる。

---

**[5] libraries-04_Connection--s1 / fabrication / sections.s3 — DbConnectionContext row**

The knowledge file states "任意の名前（データベースコネクション名）を付加して複数のAppDbConnectionを管理できる" but the source only says a name can be attached to the held AppDbConnection; it never says multiple AppDbConnections can be managed.

> Evidence: 保持するAppDbConnectionには、任意の名前(データベースコネクション名)を付加することができる。

---

**[6] libraries-04_HttpAccessLog--s1 / fabrication / sections.s5**

Section s5のプレースホルダ一覧（endFormatで $statusCode$, $contentPath$ を指定できる）はソースに存在しない。ソースファイルはディスパッチ先クラス決定後のフォーマットセクションで終了しており、「リクエスト処理開始時のプレースホルダ一覧に加えて下記のプレースホルダを指定できる」という文言はソースに根拠がない。

> Evidence: ソースファイルは「ディスパッチ先クラス決定後のログ出力に使用するフォーマット」のデフォルトフォーマットで終了しており、その後の「リクエスト処理終了時のログ出力に使用するフォーマット」セクションは存在しない。

---

**[7] libraries-messaging_sender_util--s1 / omission / s6 — メッセージID採番処理の追加**

The warning that the example implementation does not guarantee uniqueness of generated IDs is missing. The source explicitly states: 「以下は簡易的な実装であり、IDがユニークである保証は無い。」 This is decision-necessary information.

> Evidence: 「以下は簡易的な実装であり、IDがユニークである保証は無い。」— appears in source immediately before the DefaultHttpMessageIdGenerator code block

---

**[8] libraries-record_format--s11 / fabrication / s2 — XMLデータ例**

The XML code example was modified. The source uses `<header>` and `<data>` (opening-tag syntax) as closing tags, while the knowledge file changed them to `</header>` and `</data>` (proper closing tags). The code was not faithfully reproduced.

> Evidence: Source: `  <header>\n    <msg_id>123456</msg_id>\n  <header>` — knowledge file shows `</header>` instead.

---

**[9] libraries-record_format--s11 / fabrication / s3 — XMLデータ例**

Same issue as s2 — XML closing tags were corrected from `<header>/<data>` (source) to `</header>/</data>` (knowledge file).

> Evidence: Source uses `<data>` (not `</data>`) as the closing tag in repeated `<data>` blocks.

---

**[10] testing-framework-01_UnitTestOutline--s1 / omission / s3 — JSP構文チェック**

Source specifically calls out `<jsp:include>` and `Tiles` as particularly high-risk scenarios for generating invalid HTML. This context is entirely absent from the knowledge file.

> Evidence: 特に、**\<jsp:include>** や、**Tiles** といった仕組みを使用している画面では、各モジュールが生成したHTMLを組み合わせて表示することになるので、結果として不正なHTMLを生成してしまう危険性が高い。

---

**[11] testing-framework-03_DealUnitTest / omission / テスト実施 section**

The テスト実施 section and its main instruction are missing. The source states: 'テストケースに従ってテストを実施する。' The knowledge file preserves the DBダンプ note but drops the section heading and main instruction.

> Evidence: テスト実施\n==========\nテストケースに従ってテストを実施する。

---

**[12] testing-framework-batch--s10 / fabrication / s11 — データベースの結果検証**

Knowledge file states 'そのグループIDのテストデータで実際のDB状態を確認する' but the source says 'ファイル出力結果を確認することができる' in the database verification section. The knowledge file silently corrected what appears to be a copy-paste error in the original docs.

> Evidence: データベースの結果検証: 'テストケース一覧のexpectedTable欄にグループIDを記載することにより、そのグループIDのテストデータで実際のファイル出力結果を確認することができる。'

---

**[13] testing-framework-batch-03_DealUnitTest--s1 / fabrication / s1 — import文**

The knowledge file states a rule about when to use `BatchRequestTestSupport` vs `nablarch.test.core.messaging.BatchRequestTestSupport` (single-sheet vs multi-sheet). The source never states this distinction — the knowledge file invented a rule from an unexplained coincidence in example code.

> Evidence: Source uses different imports in two separate example classes without explanation. Knowledge file invented an explicit usage rule from this coincidence.

---

**[14] web-application-01_DbAccessSpec_Example--s16 / fabrication / sections.s1**

The prose description "`ParameterizedSqlPStatement.executeUpdateByMap(Map)` でMapのデータを1件更新する。" has no basis in the source. The source section contains only a code example with an inline comment, no descriptive sentence.

> Evidence: Source section "1件のデータを更新する場合" contains only the code block — no descriptive sentence is present.

---

**[15] web-application-01_spec--s1 / fabrication / sections.s3 (精査仕様の注意ブロック)**

「全バリデーションがデフォルトのメッセージIDを使用するため、カスタムメッセージIDの設定は不要。」という記述はソースに存在しない。ソースのnoteはメッセージIDについての説明のみで、カスタムメッセージIDが不要という結論は導かれていない。

> Evidence: ソースnote: 「メッセージIDを一意に特定するもの」「容易に管理できる」という説明のみ。

---

**[16] web-application-07_confirm_view--s1 / omission / s1 — テストコード**

The test method implementation using Nablarch's `execute()` API is omitted. The source provides the full test body showing the `execute("testRW11AC0202")` call pattern, which is the correct way to invoke a request unit test.

> Evidence: `@Test\npublic void testRW11AC0202() {\n    execute("testRW11AC0202");\n}`

---

**[17] web-application-11_exclusiveControl--s1 / omission / s4**

`@OnDoubleSubmission(path = "forward://RW11AC0303", statusCode = 400)` annotation on `doRW11AC0304` is missing from the code example. The source shows this annotation alongside `@OnErrors`, demonstrating double submission prevention combined with exclusive control.

> Evidence: `@OnDoubleSubmission(path = "forward://RW11AC0303", statusCode = 400)\npublic HttpResponse doRW11AC0304(HttpRequest req, ExecutionContext ctx) {`

---

**[18] web-application-Other--s1 / omission / sections s7 and beyond**

The knowledge file covers only 6 of the 13 h2 sections. Two sections are completely absent: `other_example_code_get` (コード値の取得方法) and `other_example_warn_message` (警告メッセージ). At least 7 sections with substantive implementation content are entirely missing.

> Evidence: ToC in source lists: `other_example_code_get`, `other_example_warn_message` as distinct h2 sections. Automated check: Section count 6 < source headings 13.

---

**[19] workflow-WorkflowArchitecture--s2 / omission / s2 — ワークフローインスタンステーブル / インスタンスID**

ソースには「インスタンスIDは、業務側のワークフローデータを保持するテーブルに格納する**必要がある**」と必須制約が記載されているが、知識ファイルでは「業務側テーブルに格納し」と行為として記述されており、必須制約（must）が省略されている。

> Evidence: 「インスタンスIDは、業務側のワークフローデータを保持するテーブルに格納する必要がある。業務側テーブルに格納することで、ワークフローの進行状態と業務データを紐付けて管理することができる。」

---

### 2. 軽微 (Minor) 336件 — 問題の傾向分析

#### 2-1. hints_missing (165件): ヒントキーワードの欠落傾向

**傾向1: タグ属性名の網羅的欠落（最多パターン）**

最も件数が多いのは、HTMLタグ・カスタムタグの属性テーブル第1列（属性名）がhintsに含まれていないケース。特に `libraries-07_TagReference--s11` 配下では、compositeKeyCheckbox / compositeKeyRadioButton / file / select / radioButtons / checkboxes / submit / button / submitLink / popupSubmit / popupButton の各タグで、`autofocus`, `disabled`, `onchange`, `name`, `value`, `type` などのHTML標準属性が軒並み欠落している（件数60〜71の計11件）。また `libraries-07_TagReference--s1` のtext/textarea/password/radioButton/checkboxタグでも `onselect`, `onchange`, `autocomplete`, `autofocus`, `placeholder`, `maxlength` が欠落（件数73〜77）。

ルール上「テーブル第1列のプロパティ名はhintsに含める」とされているが、汎用的すぎる属性名（`name`, `type`, `disabled`など）については生成AIが選別して省いている可能性がある。

**傾向2: コードブロック内のPascalCaseクラス名の欠落**

Java実装例・XML設定例に登場するクラス名が、そのセクションのhintsに含まれていないケースが多数。例：
- `MultiThreadExecutionHandler`, `RequestPathJavaPackageMapping`（architectural_patternのXML）
- `BasicLogFormatter`, `FileLogWriter`（log.propertiesの設定例）
- `SystemAccountEntity`, `CM311AC1Component`, `MessageLevel`（バリデーション・一覧検索のAction実装例）
- `SqlResultSet`, `SqlRow`（web-applicationの複数Action実装例）

これらは各セクションに固有のコード例に登場するが、「そのセクション固有のキーワード」として認識されずhintsに含められていない。コードブロックとhintsの紐付けが弱い。

**傾向3: 同一クラス名が別セクションにのみ登録されている**

`TransactionManagementHandler.Callback` のように、s1のhintsにはあるがs2のコードブロックでも使用されているにもかかわらずs2のhintsに含まれていないケース（件数25）。セクション横断での重複登録がなされていない。`ValidationContext` も s3 hintsにはあるが s2 コードで使用される箇所のhintsに含まれていない（件数146）。

**傾向4: 設定プロパティ名の欠落**

XMLコンポーネント設定のプロパティ名（`<property name="xxx">`）がhintsに含まれていないケース。例：
- `lockFilePath`, `failureCodeCreateLockFile` など（SynchronousFileLogWriter）
- `duplicateErrorSqlState`, `duplicateErrorErrCode`（BasicSqlStatementExceptionFactory）
- `defaultLanguage`, `defaultTimeZone`（LanguageAttribute/TimeZoneAttribute）
- `dataTypeDefinitionLoader`（EntityGenerator）

これらはユーザーが設定ファイルを書く際に検索するキーワードとなりうるが、生成AIが「プロパティ名=hintsに必要」と認識できていない。

**傾向5: UIフレームワーク固有タグ名の欠落**

`n:checkbox`, `n:code`, `tab:content`, `box:content`, `spec:condition` など、UIフレームワークのカスタムタグ名がhintsに含まれていない（件数119〜120, 137）。特に `libraries-07_TagReference--s1` の s1 では、カスタムタグ一覧テーブルに全タグが列挙されているにもかかわらず、s1のhintsには一部の主要タグのみしか含まれていない（件数72）。これはタグ参照ファイル系で一貫した問題。

---

#### 2-2. omission (103件): 省略・欠落傾向

**傾向1: コードコメントの省略（最多パターン）**

ソースコードブロック内のインラインコメントが知識ファイルで省略されるケースが多い。特に重要なのは：
- `req = receive(); // (フレームワークが要求電文を受信)` のような「フレームワーク管理か否か」を示すコメント（件数21）
- `#フレームワーク制御項目(自動追加)` のような「開発者が手動設定不要」を示すコメント（件数26〜27）
- ディレクトリツリーのインラインコメント（件数75, 77）— `include/ # 共通インクルードJSP` のような用途説明

これらのコメントはコードの意味理解に直結するが、コードブロックの「コンテンツ」として扱われず省略される傾向がある。

**傾向2: 注意・警告ブロックの内容削減**

noteブロックの内容が一部しか取り込まれず、重要な制約が欠落するケース：
- DiContainerを直接使用するコードの大きな警告文（通常はSystemRepositoryを使え）が丸ごと省略（件数32）
- JSON設定ファイルにコメントが記述できないという制約（件数69）
- POST再送信防止の機構説明（セッション格納→リダイレクトで破棄のメカニズム）が省略（件数22）
- `\u0020` より大きいコードの文字はトリムされないという一般原則が、全角スペースの具体例だけに縮小（件数53）

**傾向3: 設計意図・アーキテクチャ的説明の省略**

なぜその設計になっているかの説明が省略される傾向：
- AuthenticationUtilが存在する理由（リポジトリから毎回取得するのを避けるため）（件数9）
- noCacheタグがinclude JSPで使えない理由（Servlet APIの仕様）（件数43）
- metaタグとレスポンスヘッダを両方生成する理由（古いブラウザ対応）（件数42）
- ウィンドウスコープを使うと「特段の考慮なし」に並行操作が可能という重要なメリット（件数18）

**傾向4: チュートリアル・サンプルの補足情報省略**

- Componentクラスを作成しない理由の説明（シンプルなSQLかつリクエスト単体テストで十分のため）（件数94）
- `tutorial_project` は架空のプロジェクト名であるという注記（件数82）
- Eclipseワークスペース形式で提供されるという具体的な配布形式（件数6）

**傾向5: メソッドシグネチャ・Javadocの省略**

- `prepareVersions` の `List<? extends ExclusiveControlContext>` というジェネリクス境界を含む正式シグネチャが省略（件数48）
- `.. function::` ディレクティブの形式シグネチャ全般
- `@ValidateFor` の「いずれか1つが一致すれば呼び出される」というセマンティクス説明（件数47）

**傾向6: サンプルデータの省略**

コード動作を理解するために必要なテーブルデータが省略されるケース：
- CODE_PATTERNテーブルとCODE_NAMEテーブルのサンプルデータ（codeSelectタグの出力を理解するために必須）（件数40）
- フォーマット定義ファイルの各フィールドのビジネス意味コメント（件数51）

---

#### 2-3. fabrication (36件): 捏造・誤変換傾向

**傾向1: コードコメントの書き換え（最多パターン）**

ソースのコードコメントを「より詳細に説明した」コメントに置き換えるケースが複数。
- `// OS名およびOSタイプにより判定する` → `// OS名が"ipad"、またはandroidでOSタイプが"tablet"の場合`（件数8〜10、3件）
- これは「要約コメント」を「実装詳細コメント」に変換したケース。コメントの内容が変わっており、元コードとの差異が生じる。

**傾向2: テーブル列の追加**

ソースに存在しない列を設定テーブルに追加するケース：
- `デフォルト値` 列をhandlers-MessagingContextHandlerとhandlers-ResourceMappingの設定テーブルに追加（件数14〜15）
- `型` 列をCodePatternSchema/CodeNameSchema/CodeValueValidatorのプロパティテーブルに追加（件数18）

ソーステーブルが「設定項目 | プロパティ名 | データ型 | 備考」という構成であるにもかかわらず、より使いやすいと判断して列が追加されている。

**傾向3: 暗示・推論の明示化**

ソースが暗黙的に示しているだけの内容を、明示的なルールとして記述するケース：
- 2つのimportクラスの使い分けルール（single-sheet vs multi-sheet）— ソースはルールを述べていないが知識ファイルは規則を発明（件数13）
- RDBMSカラム型とバリデーションアノテーションの対応ルール（`CHAR(8)` → `@Length(min=8, max=8)`）— ソースは例を示すだけ（件数23）
- `ValidationManager` が `ValidatorManager` と書かれているソースのミスを「ValidationManager」に無断修正（件数22）

**傾向4: ソース文書のバグの「修正」**

ソースドキュメント自体の誤りを黙って修正してしまうケース：
- XMLのタグが `<header>` と不正に閉じられている箇所を `</header>` に修正（件数8〜9）— ソースのまま再現すべき
- `ValidationContext<CustomerEntity context` という構文エラーを `ValidationContext<CustomerEntity> context` に修正（件数33）

これらは「正しいコード」として生成されるが、ソースの記述を変えてしまっている。

**傾向5: 存在しない説明文の追加**

コードセクションに説明文が存在しないにもかかわらず、生成AIがコードから推測した説明を追加するケース：
- `ParameterizedSqlPStatement.executeUpdateByMap(Map)` の説明文（件数14）
- `source` ディレクトリの使用場面説明（件数3）
- `レスポンシブ` というヒントキーワード（ソースに語句が存在しない、件数31）

**傾向6: 否定命題の逆転**

ソースの「不要である」という記述を、条件付きで「必要な場合がある」に反転させるケース：
- カスタムバリデータ固有の設定は「不要」がソースの記述だが、知識ファイルは「必要な場合がある」と反対の主張（件数25）
- `SessionConcurrentAccessHandler` が「整合性を実装する」をソースが述べているのに対し、知識ファイルは「整合性を保証する」と強い主張に変換（件数16）

---

#### 2-4. section_issue (32件): セクション構造の問題傾向

**傾向1: 分割不足（V3ルール違反）— 最多パターン**

2000文字以上のh2セクション内に独立したh3サブセクションが存在する場合は分割すべきというV3ルールに違反しているケースが多い：
- `libraries-08_04_validation_form_inheritance--s1` のs2（3つのh3サブセクション、コード例含む大量コンテンツ）（件数14）
- `libraries-99_Utility--s1` のs1（`クラス概要` と `機能一覧` の2つのh3を統合）（件数16）
- `web-application-basic--s1` のs3（Map型とList型の2つのh3サブセクションを統合）（件数30）
- `libraries-file_upload_utility` のs7（8つのサブセクションを1つに統合）（件数19）

**傾向2: セクション順序の逆転**

ソースの章の順序と異なる順序でセクションが配置されるケース：
- `handlers-HttpResponseHandler--s1` でs3（ステータスコード変換）とs4（ハンドラ処理フロー）が逆転（件数5）
- `web-application-07_insert--s1` でs4〜s7が二重サブミット→自動設定という順序だが、ソースは逆（件数28）

**傾向3: 空・極小セクション（`なし` コンテンツ）**

実質的なコンテンツなしでセクションが生成されるケース：
- `testing-framework-batch--s10` のs6, s8, s10（各々「なし」、見出しのみのソースセクション対応）（件数23）
- `handlers-BatchAction--s1` のs1とs3（42文字・2文字のコンテンツ）（件数2〜3）
- `workflow-WorkflowArchitecture--s2` のs4（アンカー定義のみのセクション）（件数32）

これらは「ソースに内容がない」という事実の正確な反映であるが、V3チェック基準（< 50文字）に該当する。

**傾向4: RST記法の残存**

Sphinxの `:ref:`, `:download:` などのRST固有マークアップがMarkdownに変換されずそのまま残るケース：
- `handlers-DataReadHandler--s1` のs2に `:ref:\`実行時ID<execution_id>\`` が残存（件数4）
- `web-application-10_submitParameter--s1` のs3にテーブルセル内に `:download:` 記法が残存（件数29）
- `web-application-01_sampleApplicationExplanation--s1` のs2に `:ref:` 記法が残存（件数26）

**傾向5: 複数ソースセクションの誤った統合**

独立したh2レベルのセクションが誤って1つのセクションに統合されるケース：
- `biz-samples-01_ConnectionFramework--s10` でHTTP/HTTPS通信とJSONコンバータが1セクションに（件数1）
- `mom-messaging-01_userRegisterMessageReceiveSpec--s1` で電文仕様とエンティティ情報が1セクションに（件数21）
- `web-application-03_listSearch--s10` でリクエストメソッド作成とView(JSP)作成が1セクションに（件数27）

---

### 傾向分析まとめ

| 問題 | 根本原因の推定 | 改善アプローチ |
|------|--------------|--------------|
| hints: タグ属性名の欠落 | 汎用属性名（disabled等）を「重要でない」と判断する傾向 | 生成プロンプトに「テーブル第1列は全件hintsに含める」を強調 |
| hints: コードブロック内クラス名 | コードブロックとhintsの関連付けが弱い | セクション固有コードのPascalCase識別子を明示的に収集する指示 |
| omission: コードコメント | コードの「コンテンツ」部分として認識されない | 「// (...)」形式のコメントも保持する指示 |
| omission: 設計意図の説明 | 「実装情報」を優先し「背景情報」を低重要視 | 「なぜ〜か」の説明文を必ず保持する指示 |
| fabrication: コードコメントの書き換え | コメントを「要約→詳細化」する傾向 | コードブロックはソースをそのまま再現する強い指示 |
| fabrication: テーブル列追加 | 「より有用」な形式への自動改善 | テーブル構造はソースのまま維持する指示 |
| fabrication: ソースバグの修正 | 構文エラーを自動修正する傾向 | 「ソースの誤りは修正せず原文を保持する」指示 |
| section_issue: 分割不足 | 2000文字ルールの判定精度 | V3ルール判定ロジックの強化 |
| section_issue: RST記法残存 | RSTからMarkdownへの変換漏れ | `:ref:`, `:download:` の変換ルールを明示化 |

---

## 重大問題の残存原因調査 (2026-03-30)

19件の重大問題について、初回実行（20260324T235810）の全ラウンドログと照合し、なぜ修正サイクルを経てもなお残ったかを調査した。

### 調査方法

- 初回実行の phase-d findings（r1/r2/r3）と最終検証 findings（20260325T191919 r3）を全件突き合わせ
- 重大問題を持つ各ファイルのラウンド推移を追跡
- 代表ファイルについて phase-e の出力（out.json）を直接確認し、修正内容を検証

### 根本原因の分類

#### 原因A: 修正が新たな重大問題を導入（Fix-induced regression）— 4件

phase-e（修正フェーズ）が元の問題を直そうとした際に、新たな事実誤りを埋め込んだ。修正後のファイルが次ラウンドでクリーンと判定されたため、最終検証まで気づかれなかった。

**handlers-KeitaiAccessHandler--s1**
- r1: minor（ハンドラ配置ルールの軽微な問題）→ phase-e が修正
- r2/r3 (初回): clean
- 最終検証 r3: critical — s1のNablarchTagHandler行で `nablarch_sumit`（正しい）を `nablarch_sumbit`（存在しないパラメータ名）に書き換えていた
- phase-e の out.json を確認: s2 hints に `nablarch_sumit` と `nablarch_sumbit` の両方が存在、s1テキストには `nablarch_sumbit` が記載されていた → **修正中に誤字が混入**

**handlers-MessageResendHandler--s1**
- r1: minor（2件）, r2: minor（1件）→ phase-e が順次修正
- r3 (初回): clean
- 最終検証 r3: critical — case 4の説明で「業務処理が**正常終了**したがエラー応答電文が未達」（ソース）を「**異常終了**し」と反転させていた
- phase-e r1の out.json を確認: 既にcase 4に「異常終了」と記載されていた → **r1修正時に意味を反転**

**libraries-04_HttpAccessLog--s1**
- r1: critical（出力項目3件欠落）+ minor → phase-e が修正
- r2: 元のcriticalは解消されたが、**新たな critical が2件発生**（プレースホルダ表に存在しない項目を追加）→ phase-e が修正
- r3 (初回): minor のみ
- 最終検証 r3: critical（fabrication）— s5プレースホルダが依然として不正確
- 連鎖的な修正誘発エラーが蓄積

**testing-framework-batch-03_DealUnitTest--s1**
- r1: critical（`execute()` 呼び出しパターンの欠落）→ phase-e が修正
- r2: minor（1件）→ phase-e が修正
- r3 (初回): critical — 修正時に「1シートテストでは `batch.BatchRequestTestSupport`、複数シートでは `messaging.BatchRequestTestSupport` を使用する」というルールを**ソースに存在しない形で明文化**（ソースは単に異なるexampleクラスが異なるimportを使っているだけで理由を説明していない）
- 最終検証 r3: 同一の critical が残存（後述の原因Cと重複）

---

#### 原因B: 評価の非一貫性（LLM evaluation inconsistency）— 8件

初回実行では minor または clean と判定されたが、最終検証で critical として検出された。同一ファイルに対してLLMの評価が異なるラウンドで食い違った。

**libraries-04_Connection--s1**
- 初回 r1-r3: minor のみ（fabrication の minor で `複数のAppDbConnectionを管理できる` という記述への指摘はなし）
- 最終検証: critical — 同記述が「ソースには存在しない拡張解釈」として critical 判定
- 同じ問題を r1-r3 では minor または検出なし → 最終検証で重大と判定

**http-messaging-03_userQueryMessageAction**
- 初回 r1-r3: minor（1件残留）
- 最終検証: critical — `onReceive` のロールバック挙動の欠落を critical と判定
- 初回は同じ欠落を minor と見なし修正優先度が低かった

**testing-framework-01_UnitTestOutline--s1**
- 初回 r1: critical（2件）→ phase-e で修正
- 初回 r2: minor（1件）→ phase-e で修正
- 初回 r3: minor（5件）— criticalはなし
- 最終検証: critical（`<jsp:include>` / Tiles の高リスク記述の欠落）
- 初回 r3 では同じ問題が minor または検出なし

**testing-framework-03_DealUnitTest**
- 初回 r2: clean
- 最終検証: critical（「テスト実施」セクションの手順が欠落）
- 初回では clean と判定されたが最終検証で new critical

**web-application-07_confirm_view--s1**
- 初回 r1-r3: minor のみ（3件 → 2件で推移）
- 最終検証: critical — `execute("testRW11AC0202")` のテストメソッド実装が欠落
- 初回の checks は同じ欠落を minor として扱った

**web-application-11_exclusiveControl--s1**
- 初回 r2: clean
- 最終検証: critical — `@OnDoubleSubmission` アノテーションがコード例から欠落
- 初回 r2 で clean 判定後、最終検証で new critical

**libraries-02_CodeManager--s1**
- 初回 r1: critical（「要求 > 未検討」セクション欠落）→ phase-e で修正
- 初回 r3: clean
- 最終検証: critical（別の問題: `getName` vs `getShortName` の画面用途ガイダンス欠落）
- 初回 r1 の critical とは別箇所。初回 r3 で clean になった後、最終検証が異なる問題を発見

**libraries-messaging_sender_util--s1**
- 初回 r2: critical（`generateId` 戻り値が `void` → `String` に誤記）→ phase-e で修正
- 初回 r3: minor（1件）
- 最終検証: critical（一意性保証なしの警告文が欠落）
- 初回 r2 の critical とは完全に別の問題。初回では minor と判定した箇所が最終検証で critical

---

#### 原因C: 中断により修正未実施 — 3件

初回実行の r3 で既に critical が検出されていたが、OS reboot による中断で phase-e（round 3）が実行されなかった。そのまま最終検証でも同じ問題が残留。

**web-application-01_spec--s1**
- 初回 r3: critical（fabrication）— 「カスタムメッセージIDの設定は不要」という根拠なき結論
- 最終検証 r3: 完全に同一の critical が残存
- phase-e round 3 が中断で未実行

**testing-framework-batch-03_DealUnitTest--s1**（原因Aとの重複）
- 初回 r3: critical（fabrication — import ルールの捏造）← 原因Aで導入
- phase-e round 3 が中断で未実行
- 最終検証 r3: 同一の critical が残存

**web-application-Other--s1**
- 初回 r3: critical（omission — s7, s8セクション欠落）
- 最終検証 r3: 同一の critical が残存（セクション数が6/13という構造的欠落）
- phase-e round 3 が中断で未実行

---

#### 原因D: 修正困難なコンテンツ — 2件（libraries-record_format--s11、web-application-Other--s1）

セクション全体の大規模欠落や複雑な構造を持つファイルで、phase-e が修正を試みるたびに新たな fabrication が生まれる連鎖が発生した。

**libraries-record_format--s11**
- r1: critical 7件（取り扱い対象のデータ、階層構造、繰り返しデータ、データ型、DTD、名前空間、XML属性要素コンテンツ — 7セクションが全欠落）
- phase-e r1: 大量の内容を追加 → r2 では critical 1件（XMLデータ例の欠落）に削減
- 最終検証: critical 2件（fabrication — XMLの閉じタグ）
- ソースのXMLサンプルが意図的に `<header>` のような開きタグ構文を閉じタグとして使用している（v1.4時代の特殊な記法）。phase-e がこれを「誤り」と判断して `</header>` に「修正」したが、これ自体が fabrication

**web-application-Other--s1**（原因Cとの重複）
- r1: critical（s7, s8欠落）→ phase-e が追加 → r2: critical（fabrication — 存在しないメソッドシグネチャの捏造）→ phase-e が修正 → r3: critical（omission — 依然としてセクション欠落）
- 13セクション中6セクションしか生成されていない根本的な欠落で、fix サイクルでは解消できなかった

---

### サマリー

| 原因 | 件数（ファイル数） | 概要 |
|------|----------------|------|
| A: Fix-induced regression | 4 | phase-eが修正中に新たな事実誤りを埋め込み、後続チェックで見逃された |
| B: LLM評価の非一貫性 | 8 | 初回runではminor/cleanだった問題が、最終検証で重大と判定 |
| C: 中断により未修正 | 3 | 初回r3で既知のcriticalがあったが、phase-e round 3が未実行 |
| D: 修正困難なコンテンツ | 2 | 大規模欠落や特殊なソース記法でfixサイクルが収束しない |

**重複あり**: testing-framework-batch-03_DealUnitTest--s1（原因A+C）、web-application-Other--s1（原因C+D）

### 示唆

- **原因Aへの対策**: phase-e 実行後のファイルに対して、修正箇所周辺を限定した narrow re-check を追加する
- **原因Bへの対策**: 最終検証でのseverity引き上げは想定内だが、critical率が高い（19/540 = 3.5%）。評価プロンプトのcritical基準を初回チェックから統一する
- **原因Cへの対策**: 今回は運用上の問題（中断）。再実行で対処可能
- **原因Dへの対策**: 生成時（Phase B）にソースの特殊記法（意図的な非標準XMLなど）を検出し、phase-e に注意情報として渡す

---

### 漏れていた3件の補足 (2026-03-30)

前節の分析で原因分類に含めていなかった3件を追加する。

**testing-framework-batch--s10 → 原因B**
- 初回 r1: minor 3件（s2のfabrication、s1/s11のhints_missing）
- 初回 r2: minor 2件（s2のfabricationが続く、s7のhints_missing）
- 初回 r3: minor 3件（s11のログ結果検証テーブル欠落、s6/s8/s10の空セクション、s11のhints_missing）
- 最終検証 r3: **critical**（s11「データベースの結果検証」のテキスト: ソースは「実際のファイル出力結果を確認することができる」だが知識ファイルは「実際のDB状態を確認する」）
- 初回 r3 が指摘していた s11 の問題（ログ結果検証テーブルの欠落）とは別箇所の別問題。最終検証が初回では minor/見逃しだった fabrication を critical として新たに検出。**評価の非一貫性（原因B）**

**web-application-01_DbAccessSpec_Example--s16 → 原因A**
- 初回 r1: minor（セクション構造：ソースに2つのh2があるが知識ファイルが1セクションしか持たない）
- 初回 r2: minor 2件（s2のコメント欠落、s2の説明文 `executeBatch` → fabrication）
- 初回 r3: **clean**
- 最終検証 r3: critical（s1の説明文「`ParameterizedSqlPStatement.executeUpdateByMap(Map)` でMapのデータを1件更新する」がソースに根拠なし）
- r1 の修正で phase-e がセクション構造を直した際に、s1 に根拠のない説明文を付加した可能性が高い。r3 では clean 判定されたが最終検証が critical として検出。**Fix-induced regression（原因A）**

**workflow-WorkflowArchitecture--s2 → 原因B（原因C的側面も）**
- 初回 r1: minor 2件（s2のタイトル不一致、s2のhints_missing）
- 初回 r2: minor 3件（s2の画像配置問題、s1イベントテーブルの型 `java.lant.String`→`java.lang.String` のソース誤植を「修正」= fabrication、同様にゲートウェイテーブル）
- 初回 r3: **ファイルなし（中断）**
- 最終検証 r3: critical（s2のインスタンスID説明で「格納する**必要がある**」という必須制約がソースにあるが「格納し」と行為記述に弱められている）
- r3 が中断で未実行のため、この critical が初回 r3 でも発見されたかは不明。最終検証が新たに critical と判定。r2 で指摘されていたのは別の問題（ソース誤植の黙示的修正）。**評価の非一貫性（原因B）に分類するが、中断（原因C）の可能性も排除できない**

### 修正済み分類表

| 原因 | 件数（ファイル数） | 概要 |
|------|----------------|------|
| A: Fix-induced regression | 5 | handlers-KeitaiAccess, handlers-MessageResend, libraries-04_HttpAccessLog, testing-framework-batch-03_DealUnitTest--s1, web-application-01_DbAccessSpec_Example--s16 |
| B: LLM評価の非一貫性 | 9 | http-messaging-03, libraries-02_CodeManager, libraries-04_Connection, libraries-messaging_sender_util, testing-framework-01, testing-framework-03, testing-framework-batch--s10, web-application-07, web-application-11, workflow-WorkflowArchitecture |
| C: 中断により未修正 | 3 | web-application-01_spec, testing-framework-batch-03（AとCの重複）, web-application-Other |
| D: 修正困難なコンテンツ | 2 | libraries-record_format--s11, web-application-Other（CとDの重複） |

※ 19件（18ファイル）: libraries-record_format--s11 のみ2件カウント

---

## 重大問題の残存原因・新規埋め込みの事実調査 (2026-03-30)

前節の分析（推測含む）を廃棄し、ログデータから確認できる事実のみで再調査した。

### 調査対象

初回実行（20260324T235810）の phase-d findings r1/r2/r3 全件（536ファイル分）を集計・照合。

---

### Q1: 2ラウンド回しているのに重大が残るのはなぜか

#### ラウンド別 critical 件数の推移（事実）

| ラウンド | 対象ファイル | clean | critical件数 | minor件数 | fabrication | omission |
|---------|------------|-------|------------|---------|------------|---------|
| r1 | 536 | 182 | **153** | 617 | 91 | 298 |
| r2 | 536 | 283 | **48** | 398 | 73 | 160 |
| r3 | 345 | 192 | **12** | 236 | 36 | 89 |

r1→r2でcriticalは153件→48件（68%削減）。残り48件のうち内訳:

#### r1でcriticalがあった99ファイルのr2結果（事実）

| r2結果 | 件数 |
|--------|------|
| clean（criticalが解消、minorも消えた） | 34件 |
| minorに降格（criticalは解消） | 52件 |
| **criticalが残留**（同一または別の問題） | **13件** |

→ **99件中13件でcriticalが解消されなかった**

#### critical残留13件の実態（事実）

r1→r2でcriticalが残留した13件のうち、**r1とr2のcriticalカテゴリが一致しないケースが多数**:

- `libraries-01_FailureLog--s1`: r1=no_knowledge_content_invalid → r2=fabrication×7+omission×6（**r1の問題とは無関係の新critical群**）
- `libraries-04_HttpAccessLog--s1`: r1=omission（出力項目3件欠落）→ r2=fabrication×2（プレースホルダ表の捏造）
- `libraries-07_DisplayTag--s20`: r1=omission（確認画面の出力例欠落）→ r2=fabrication（確認画面の出力を捏造）
- `libraries-08_ExclusiveControl--s17`: r1=omission（一括更新2件）→ r2=fabrication（組み合わせキーの更新チェック捏造）
- `ui-framework-spec_layout`: r1=omission（内部構造セクション欠落）→ r2=fabrication（コードサンプル捏造）
- `web-application-Other--s1`: r1=omission（s7,s8欠落）→ r2=fabrication×2（s7,s8のコンテンツを捏造）
- その他7件: r1のcritical問題と同一または一部が残留

**パターン**: omission(critical)を修正しようとした結果、phase-eが内容を生成し fabrication(critical) が発生している。修正前後でcriticalが消えず、問題の「種類が変わった」ケースが多い。

#### r1にcriticalなし → r2でcritical新規発生（事実）

r2で新規にcriticalが発生したファイルが **20件** あった（r1はminorまたはclean）:

代表例:
- `libraries-messaging_sender_util--s1`: r1=minor(omission×2) → r2=critical(fabrication: `generateId`戻り値を`void`→`String`に誤記)
- `handlers-MessagingAction--s1`: r1=minor(section_issue+hints_missing) → r2=critical(fabrication: try-catch-finally構造をコード例から削除)
- `readers-DatabaseRecordReader`: r1=clean → r2=critical(fabrication: 必須列を追加して両行に○を付与)
- `nablarch-batch-8`: r1=clean → r2=critical(fabrication: `手動で`という語をソースにない箇所に追加)
- `testing-framework-03_Tips--s1`: r1=minor(omission+hints_missing) → r2=critical(omission: 4セクションが16セクション中の4つしか含まれない)

→ **phase-eの修正によって、それ以前には存在しなかったcriticalが20件新たに生まれた**

---

### Q2: 2ラウンドで新たな問題を埋め込んでいるか

#### 事実：新規問題の発生数

**r1→r2 遷移（phase-e round 1の影響）:**

| 遷移パターン | 件数 |
|------------|------|
| r1 clean → r2 minor新規発生 | **30件** |
| r1 clean → r2 critical新規発生 | **5件** |
| r1にcriticalなし → r2でcritical新規 | **20件** |
| r1にfabricationなし → r2でfabrication新規 | **50件** |

**r2→r3 遷移（phase-e round 2の影響）:**

| 遷移パターン | 件数 |
|------------|------|
| r2 clean → r3 minor新規発生 | **33件** |
| r2 clean → r3 critical新規発生 | **1件** |
| r2にcriticalなし → r3でcritical新規 | **7件** |
| r2にfabricationなし → r3でfabrication新規 | **32件** |

→ **毎ラウンド、cleanだったファイルを含む多数のファイルで新たな問題が発生している**

#### 根本原因（事実から導かれるもの）

fabricationの件数推移: **r1=91 → r2=73 → r3=36**

phase-eはfabricationを純粋に削減しているように見えるが、上記の通り「新規fabrication発生ファイル数」はr1→r2で50件、r2→r3で32件。削減と発生が同時に起きている。

確認された事実のパターン:
1. **omissionを修正する際にfabricationを生成する**: phase-eに「この内容が欠落している」と指摘すると、ソースを参照して追加しようとするが、ソースにない記述や誤った情報を混入させる。r1→r2で omission(critical) → fabrication(critical) に変化したケースが複数確認できる。
2. **関係のないセクションも変更する**: 特定箇所の修正指示を受けたphase-eが、指示外のセクションのコンテンツも書き換えるケースがある（r2 cleanだったファイルがr3でfabricationを持つケース）。
3. **修正の規模が問題に比例しない**: 1件のminor修正でも、セクション全体を再生成する場合があり、その過程で新たなエラーが混入する。

