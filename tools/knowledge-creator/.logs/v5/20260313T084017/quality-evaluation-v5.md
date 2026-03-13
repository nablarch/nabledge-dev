# Nabledge-5 知識ファイル品質評価レポート

生成日時: 2026-03-13 12:53:31 JST

## A. 当たり前品質（全量定量チェック）

### 概要

| 指標 | 値 |
|------|------|
| ファイル数 | 454 |
| セクション数 | 1729 |
| 平均セクション数/ファイル | 3.8 |
| no_knowledge_content | 46 |
| 合計サイズ | 3.2 MB |
| 平均ファイルサイズ | 8.1 KB |
| 最小/最大ファイルサイズ | 0.2 / 93.3 KB |
| 平均hints数/セクション | 9.1 |

### チェック結果

| チェック | 説明 | 件数 | 判定 |
|---------|------|------|------|
| 構造整合性 | index[]とsections{}の不一致 | 0 | OK |
| hints空 | hints = [] のセクション | 0 | OK |
| A1: hints最低量 | hints < 3 のセクション | 21 | 要注意(21件) |
| A2: hints日本語 | 日本語hintsなしのセクション | 7 | 要注意(7件) |
| A3: サイズ過小 | < 300B のファイル | 2 | 要注意(2件) |
| A3: サイズ過大 | > 50KB のファイル | 3 | 要注意(3件) |
| A4: index.toon整合 | index.toonにないファイル | 1 | NG |
| 短セクション | < 50文字のセクション | 41 | 要注意(41件) |

### セクション長分布

| パーセンタイル | 文字数 |
|-------------|--------|
| P10 | 99 |
| P25 | 181 |
| P50(中央値) | 421 |
| P75 | 938 |
| P90 | 1932 |
| P99 | 6729 |

### カテゴリ分布

| カテゴリ | ファイル数 | セクション数 |
|---------|----------|------------|
| about-nablarch | 19 | 42 |
| adapters | 16 | 60 |
| biz-samples | 15 | 90 |
| blank-project | 23 | 123 |
| cloud-native | 5 | 10 |
| configuration | 1 | 1 |
| db-messaging | 9 | 23 |
| etl | 3 | 11 |
| handlers | 65 | 290 |
| http-messaging | 6 | 18 |
| jakarta-batch | 13 | 40 |
| java-static-analysis | 1 | 3 |
| libraries | 48 | 237 |
| mom-messaging | 5 | 16 |
| nablarch-batch | 12 | 27 |
| nablarch-patterns | 3 | 8 |
| release-notes | 1 | 1 |
| releases | 21 | 62 |
| report | 1 | 6 |
| restful-web-service | 11 | 28 |
| security-check | 1 | 1 |
| setting-guide | 7 | 27 |
| testing-framework | 136 | 506 |
| toolbox | 6 | 24 |
| web-application | 24 | 57 |
| workflow | 2 | 18 |

### A1: hints最低量 詳細（上位20件）

- blank-project-CustomizeDB#s16: 2 hints
- web-application-feature_details#s3: 2 hints
- restful-web-service-feature_details#s3: 2 hints
- mom-messaging-feature_details#s3: 2 hints
- testing-framework-inbrowser_jsp_rendering#s1: 2 hints
- libraries-exclusive_control#s5: 2 hints
- libraries-service_availability#s4: 2 hints
- handlers-http_response_handler#s3: 2 hints
- handlers-request_path_java_package_mapping#s3: 1 hints
- handlers-session_concurrent_access_handler#s3: 2 hints
- handlers-hot_deploy_handler#s3: 2 hints
- handlers-file_record_writer_dispose_handler#s3: 2 hints
- handlers-request_handler_entry#s3: 2 hints
- handlers-messaging_context_handler#s3: 2 hints
- handlers-database_connection_management_handler#s3: 2 hints
- handlers-multi_thread_execution_handler#s3: 2 hints
- handlers-thread_context_handler#s3: 2 hints
- biz-samples-01#s3: 2 hints
- biz-samples-05#s2: 2 hints
- biz-samples-OnlineAccessLogStatistics#s5: 2 hints
- ... 他 1 件

### 短セクション詳細（上位20件）

- blank-project-beforeFirstStep#s1: 2 chars
- blank-project-CustomizeDB#s8: 2 chars
- blank-project-CustomizeDB#s16: 2 chars
- blank-project-CustomizeDB#s17: 2 chars
- blank-project-MavenModuleStructures#s14: 2 chars
- setting-guide-ManagingEnvironmentalConfiguration#s7: 41 chars
- setting-guide-CustomizeAvailableCharacters#s5: 41 chars
- db-messaging-architecture#s7: 43 chars
- http-messaging-feature_details#s7: 42 chars
- http-messaging-feature_details#s8: 25 chars
- http-messaging-architecture#s5: 49 chars
- web-application-feature_details#s9: 22 chars
- web-application-feature_details#s14: 25 chars
- web-application-feature_details#s18: 26 chars
- restful-web-service-feature_details#s9: 49 chars
- jakarta-batch-feature_details#s3: 49 chars
- testing-framework-guide-development-guide-08-TestTools-03-HtmlCheckTool#s2: 41 chars
- testing-framework-03_Tips#s9: 36 chars
- testing-framework-RequestUnitTest_batch#s9: 40 chars
- testing-framework-spec_updated_by#s2: 47 chars
- ... 他 21 件

## B. 魅力的品質（findings分析）

### findings推移

| 指標 | R1 | R2 |
| --- | --- | --- |
| total | 539 | 539 |
| clean | 185 | 306 |
| has_issues | 354 | 233 |
| clean_rate | 34.3% | 56.8% |
| findings_total | 701 | 380 |
| critical | 114 | 36 |
| minor | 587 | 344 |
| fabrication | 75 | 50 |
| hints_missing | 263 | 166 |
| omission | 298 | 133 |
| section_issue | 65 | 31 |

### ファイル集中度（最終ラウンド findings上位20件）

| ファイルID | findings数 | カテゴリ |
|-----------|-----------|---------|
| releases-nablarch5u13-releasenote | 9 | fabrication, hints_missing, omission |
| releases-nablarch5u10-releasenote | 7 | hints_missing |
| testing-framework-04_MasterDataRestore--s1 | 5 | section_issue, omission |
| adapters-micrometer_adaptor--s14 | 5 | hints_missing, omission |
| adapters-micrometer_adaptor--s1 | 4 | section_issue, hints_missing, omission |
| releases-nablarch5u6-releasenote | 4 | hints_missing, omission |
| blank-project-setup_ContainerBatch--s1 | 4 | hints_missing, omission |
| blank-project-setup_Jbatch--s1 | 4 | section_issue, hints_missing, omission |
| releases-nablarch5u19-releasenote | 4 | fabrication, hints_missing, omission |
| libraries-tag_reference--s46 | 4 | hints_missing |
| releases-nablarch5u16-releasenote | 3 | fabrication, hints_missing, omission |
| testing-framework-03_Tips--s1 | 3 | fabrication, hints_missing, omission |
| libraries-bean_validation--s8 | 3 | hints_missing |
| testing-framework-table_row | 3 | section_issue, omission |
| testing-framework-initial_setup--s1 | 3 | omission |
| testing-framework-ui-dev-doc-reference-ui-standard--s1 | 3 | hints_missing, omission |
| releases-nablarch5u11-releasenote | 3 | fabrication, hints_missing, omission |
| blank-project-MavenModuleStructures--s1 | 3 | section_issue, hints_missing |
| releases-nablarch5u18-releasenote | 3 | hints_missing |
| biz-samples-08--s1 | 3 | hints_missing |

### fabrication頻出パターン（上位10件）

| パターン | 件数 |
|---------|------|
| knowledge fileのNo.12説明に「新規プロジェクトを作成する際はGetting Startedを出発点としてアプリケーションを改修する用途では使用 | 1 |
| 知識ファイルは「インデックスページ（全テスト一覧）に遷移する」と記述しているが、ソースのテキストには「以下のような画面に遷移する」とあるのみで「全テスト一覧」と | 1 |
| The knowledge file silently corrects three bugs present in the source code: (1) | 1 |
| 知識ファイルに「Content-Security-PolitcyヘッダやJSP内への埋め込みが可能」と記載されているが、ソースの正しい表記は「Content-S | 1 |
| The knowledge file labels the second http_messaging constraint as「レスポンスヘッダのカスタマイ | 1 |
| The knowledge file marks `transactionFactory` as 必須: ○ in the property table, bu | 1 |
| ナレッジファイルはクラス名を `RequestResponseCookieManager` と記載しているが、ソースには `RequestResponceCoo | 1 |
| 「起因バージョン: 1.0.0〜1.2.3」の「〜」表記は、ソースの2列（モジュール起因バージョン=1.0.0、Nablarch起因バージョン=1.2.3）を「 | 1 |
| The class name 'CsrfTokenVerificationHandler' appears in the hints but is never | 1 |
| Semicolons were added to two Java statements that do not have them in the source | 1 |

### omission頻出パターン（上位10件）

| パターン | 件数 |
|---------|------|
| The rationale for using this pattern is missing. The source states: "以下に示す例を参考に実 | 1 |
| The tip about testing a Form whose property holds another Form omits the first s | 1 |
| ソースファイルの「Example」カテゴリに記載されている4件の変更（No.20: ウェブアプリケーションをステートレス設定に変更、No.21: HTTPメッセ | 1 |
| The source has a dedicated `TestCaseInfo` section under 構造 with the following ac | 1 |
| The source states that HTML resources (stylesheets, images, etc.) are also outpu | 1 |
| The source includes the original `idGenerator` component XML code block (showing | 1 |
| The source introduction states 'この作業は、UI開発基盤の担当者が実施すればよく、各担当者が個別に実施する必要はない。' (Th | 1 |
| The knowledge file covers only 4 of the 16 sections listed in the source TOC. Th | 1 |
| The source includes a description table immediately before the XML code example, | 1 |
| The source explicitly includes Eclipse configuration steps for setting the `-Dna | 1 |

## C. 実行情報

| 項目 | 値 |
|------|------|
| 実行時間 | 4.0時間 (14332秒) |
| 総コスト | $397.53 |
| 並列数 | 6 |
| 最大ラウンド | 2 |

| R1 Phase D コスト | $80.50 |
| R2 Phase D コスト | $158.68 |
| R1 Phase E コスト | $58.34 |
| R2 Phase E コスト | $99.55 |

## D. Critical Findings 詳細分析（R2終了時点）

R2のPhase E修正後は未検証のため、以下はR2 Phase D検出時点の状態。

| 区分 | 件数 | ユーザーインパクト |
|------|------|----------------|
| fabrication (critical) | 9 | **高**: エージェントがソースに根拠のない実装指示を出す |
| omission (critical) | 27 | **高**: エージェントが重要な制約・前提条件を知らずに回答する |
| hints_missing (minor) | 166 | **中**: 検索ヒット率が低下、正しい情報に到達しにくい |
| section_issue (minor) | 31 | **低**: 構造の問題、正確性には影響しない |
| fabrication (minor) | 41 | **低**: マークアップの誤りなど、実装判断に影響しない |
| omission (minor) | 106 | **低〜中**: 補助的情報の欠落、実装は可能だが不完全 |

### Critical Fabrication（9件）— ソースにない情報の捏造

| # | ファイル | 内容 |
|---|---------|------|
| 1 | biz-samples-03--s20#s10 | 次へ セクションのタグ属性（useNextSubmit=true、nextSubmitCss="nablarch_nextSubmit"、nextSubmitLabel="次へ"、nextSubmitName="nextSubmit"）はソースファイルに記載がない。ソースは前へ（s9）の属性定義で切 |
| 2 | biz-samples-03--s20#s11 | 最後 セクションのタグ属性（useLastSubmit=false、lastSubmitCss="nablarch_lastSubmit"、lastSubmitLabel="最後"、lastSubmitName="lastSubmit"）はソースファイルに記載がない。提供されたソースには 最後 の属 |
| 3 | biz-samples-03--s20#s12 | ページ番号 セクションのタグ属性（usePageNumber=true、pageNumberCss="nablarch_pageNumber"）はソースファイルに記載がない。ソースには「ページ番号全体(1..n)は、総ページ数が2以上の場合のみ表示される」という動作説明はあるが、usePageNum |
| 4 | biz-samples-12--s8#s4 — IDトークンの検証 | The knowledge file states: '`Initializable`はNablarch固有のライフサイクルインタフェースであり、DIコンテナが起動時に`initialize()`メソッドを自動的に呼び出す。' Neither of these claims (Nablarch-sp |
| 5 | handlers-post_resubmit_prevent_handler--s1#s5 | The knowledge file adds the parenthetical '（セッションデータが既に消費されたエラー/フォールバックケース）' to describe forwardPathMapping's purpose, but no such description appears |
| 6 | handlers-request_path_java_package_mapping--s1#sections.s7 | The explanation of the `//` suffix mechanism is not present in the source. The knowledge file states: "`requestPattern` の `//` サフィックス（例: `/admin//`）によ |
| 7 | libraries-failure_log--s1#s3 — 派生元実行時情報の補足ノート | The knowledge file states: "failureLogFormatter.derivedRequestIdPropName および failureLogFormatter.derivedUserIdPropName を使用することで、処理対象データから派生元のリクエストIDとユ |
| 8 | releases-nablarch5u13-releasenote#s2 No.29（nablarch-archetype-parentからh2依存関係削除） | 知識ファイルが「プロジェクトで使用するデータベースのJDBCドライバを pom.xml に明示的に定義していない場合、ビルドや実行時にエラーが発生する可能性があるため確認すること」という警告を追加しているが、ソースは「システムへの影響の可能性: なし」と明示している。この警告はソースに根拠がなく、ソ |
| 9 | testing-framework-http_send_sync-03_DealUnitTest--s1#s2 | The knowledge file adds the statement "HTTPメッセージボディのエンコーディングではなく、ログ出力時の文字コードを制御するプロパティである。" about the `charset` property. The source only states that  |

### Critical Omission（27件）— 判断に必要な情報の欠落

| # | ファイル | 内容 |
|---|---------|------|
| 1 | etl-etl_maven_plugin--s1#source introduction paragraph | 「Oracle SQL*Loader」という具体的な対象が知識ファイル全体から欠落している。ソースは「Oracle SQL*Loader用のコントロールファイルを自動生成するMavenプラグイン」と明記しており、このプラグインがOracle固有であることはユーザーが使用可否を判断する上で不可欠な情報 |
| 2 | handlers-multi_thread_execution_handler--s1#s6 | Source states that BOTH parent thread and sub-threads require a transaction control handler alongside the DB connection management handler: '(親スレッド、サブ |
| 3 | jakarta-batch-architecture--s1#s1 (バッチアプリケーションの構成) | jBatch（参照実装）がJSR352実装の選択肢として記載されていない。ソースでは「実装は、主に以下の2つから選択することになるが」として jBeret と 参照実装のjBatch の2つを明示している。ナレッジファイルは jBeret のみ言及しており、jBatch の存在が完全に省略されている |
| 4 | libraries-exclusive_control--s3#s3 — 複合主キーの場合 | 複合主キー向け ExclusiveControlContext 実装クラスの定義が省略されている。s1 は単一主キーのみを示しており、s3 の利用コードだけでは複合主キー対応クラスの作り方が分からない。AI が複合主キーの排他制御実装を支援するには、この実装例が必要。 |
| 5 | libraries-failure_log--s5#s3 — CustomDataItem の get() メソッド実装 | ソースの CustomDataItem には context.getData() で処理対象データを取得し、instanceof Map チェック、TreeMap によるソート済み出力、mapValueEditor.edit(key, value) によるマスク処理を行う get() メソッドの完全 |
| 6 | libraries-log--s11#s1 — outputBufferSize property in configuration example | The knowledge file includes `writer.monitorLog.outputBufferSize=8` in the config example but omits the unit and default value. Without this context, a |
| 7 | libraries-universal_dao--s1#s6 (検索結果を遅延ロードする) | JDBC fetch size information is omitted. Source states that with lazy loading, Universal DAO loads one record at a time, but memory usage varies based  |
| 8 | nablarch-batch-getting_started#前提条件 section | The prerequisites section states two items that are absent from the knowledge file: (1) this chapter is based on example_application (「本章は :ref:`examp |
| 9 | nablarch-batch-nablarch_batch_pessimistic_lock#Introduction paragraph | The rationale for using this pattern is missing. The source states: "以下に示す例を参考に実装することで、ロック時間が短縮され他プロセスへの影響を抑えることができる。" This explains the benefit and p |
| 10 | releases-nablarch5u13-releasenote#s2 (source: No.20 APIドキュメント) | No.20「非推奨APIの見直しと非推奨理由を追記」が知識ファイルに存在しない。Nablarchの非推奨APIポリシーが解説書に追記され、9モジュール（nablarch-common-exclusivecontrol 1.1.0、nablarch-fw-web-tag 1.1.0、nablarch- |
| 11 | releases-nablarch5u6-releasenote#No.41 デフォルトコンフィグレーション — nablarch-testing-default-configurationのメッセージIDに不適切なものがある | 本番稼働アプリケーションへの影響はないが「影響あり（テスト設定）」と分類されており、対処として具体的なBefore/After XML設定が提示されている。バージョンアップ後にテスト設定の動作を変えたくない場合に entityTestConfiguration の maxAndMinMessageI |
| 12 | testing-framework-01_Abstract--s8#s2 — セルへの特殊な記述方法 table | ソースの特殊記述方法テーブルに明示的に列挙されている4つの記述方法が知識ファイルのテーブルから欠落している: `"1⊔"` → `1⊔`（半角スペース付き文字列）、`"⊔"` → `⊔`（半角スペース単体）、`"１△"` → `１△`（全角スペース付き文字列）、`"△△"` → `△△`（全角スペー |
| 13 | testing-framework-02_ConfigMasterDataSetupTool--s1#s1 — 提供方法 section, end | The second occurrence of the mvn commands is omitted. The source explicitly ends the 提供方法 section with '本ツールを実行する前に以下のコマンドを実行する' followed by `mvn comp |
| 14 | testing-framework-03_Tips--s1#TOC / sections s5–s16 | The knowledge file covers only 4 of the 16 sections listed in the source TOC. The following 12 sections are completely absent: how_to_numbering_sequen |
| 15 | testing-framework-04_MasterDataRestore--s1#概要 section (source lines 11-22) | The 概要 section is entirely absent from the knowledge file. It explains the motivation: master maintenance testing requires changing master data, but t |
| 16 | testing-framework-04_MasterDataRestore--s1#特徴 section (source lines 25-29) | The 特徴 section is entirely absent. It lists three key characteristics: (1) tests can always use correct master data regardless of execution order; (2) |
| 17 | testing-framework-04_MasterDataRestore--s1#必要となるスキーマ section (source lines 32-48) | The 必要となるスキーマ section is entirely absent. It specifies that two schemas are required: (1) 自動テスト用スキーマ — schema used for automated testing; (2) バックアップ用ス |
| 18 | testing-framework-04_MasterDataRestore--s1#動作イメージ section (source lines 51-63) | The 動作イメージ section is entirely absent. It describes the operational mechanism: the framework retrieves the watched table list from the component confi |
| 19 | testing-framework-RequestUnitTest_real--s1#s3 (TestShot) | ソースの TestShot セクション末尾にある「入力データ準備や結果確認ロジックはバッチや各種メッセージング処理ごとに異なるので方式に応じたカスタマイズが可能となっている。」という記述が欠落している。これは TestShot の拡張性・カスタマイズ可否に関する重要な設計情報であり、実装判断に必要。 |
| 20 | testing-framework-architecture_overview--s1#source: introduction section (before first h2) | The source file's introduction section contains substantive descriptions of 5 components that are not captured in the knowledge file. Each component d |
| 21 | testing-framework-develop_environment--s1#intro paragraph (before first h2 section) | The source intro paragraph states "Nablarchでは、標準の開発環境として、Eclipseを提供している。" — that Eclipse is the standard development environment provided by Nablarch. |
| 22 | testing-framework-fileupload--s1#Introduction paragraph (before first h2) | The source states a prerequisite constraint: file upload testing requires web application testing prerequisites ('ウェブアプリケーションの index が前提となる'). This pr |
| 23 | testing-framework-initial_setup--s1#Section 1-4: ブランクプロジェクトのセットアップ → s7 | The source tip warns that if Maven is not installed or configured, the reader should follow the maven install and beforeFirstStep docs before running  |
| 24 | testing-framework-jsp_widgets--s1#s2 (構造 - タグファイル実装例) | field:calendarタグのカレンダーボタンが `<n:forInputPage>` でラップされているという重要な動作制約が記載されていない。これにより、カレンダーボタンは入力ページでのみレンダリングされ、参照画面・出力画面では表示されない。ウィジェットの動作を理解する上で必要な情報。 |
| 25 | testing-framework-plugin_build--s12#s1 — libraryDeployMappings description | Two implementation-relevant constraints for libraryDeployMappings are missing: (1) 展開元のファイルはパッケージ内の相対パスで指定する (source path is relative to within the pa |
| 26 | testing-framework-send_sync-03_DealUnitTest--s1#s2 — 要求電文のログ出力 | Log output examples (concrete code blocks showing actual log message format) are missing. The source contains two code-block samples — one for Map for |
| 27 | testing-framework-ui-dev-doc-reference-ui-standard--s1#s3 — 画面の配色変更 | Default CSS color variable values (actual RGB defaults) are omitted. The source contains a code block showing the exact default values for all four co |

### Critical Omission の傾向

- testing-framework関連: **16件** / 27件（59%）
- その他: 11件

testing-frameworkの知識ファイルにcritical omissionが集中している。
特に `testing-framework-04_MasterDataRestore` は概要・特徴・必要スキーマ・動作イメージの4セクションがまるごと欠落。
また `testing-framework-03_Tips` は16セクション中12セクションが欠落。

## E. 結論

### 判断に必要な事実

- 全454ファイル中、R2時点でclean 306件（56.8%）、has_issues 233件（43.2%）
- R2のPhase E修正（233件）は未検証。修正後にcriticalが何件解消されたかは不明
- critical 36件の内訳: fabrication 9件 + omission 27件
- critical omissionの75%（27件中20件）がtesting-framework関連
- 改善ループのコスト: 4.0時間 / $397.53
- 最終検証の追加コスト見込み: 約1〜1.5時間 / $80〜$160

### 対処が必要な問題

1. **最終検証が未実行**: R2 Phase E修正後の状態が検証されていない。critical 36件がいくつ解消されたか不明
2. **critical fabrication 9件**: ソースにない情報を捏造。エージェントが誤った実装指示を出すリスク
3. **critical omission 27件**: 重要な制約・前提条件の欠落。特にtesting-frameworkで大量欠落

### 対処不要な問題

- hints_missing 166件: 検索効率の問題。情報の正確性には影響しない
- section_issue 31件: 構造の問題。ユーザー影響なし
- minor fabrication/omission: 補助的情報の軽微な問題
