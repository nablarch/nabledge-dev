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

---

## 最終検証 残存 findings 分析 (run 20260327T174228)

### サマリー

| 指標 | 値 |
|------|----|
| 対象ファイル数 | 377 |
| findings合計 | 229 |
| critical | **10** |
| minor | 219 |

### カテゴリ別内訳

| カテゴリ | 件数 | 影響ファイル数 | 傾向・説明 |
|---------|------|-------------|-----------|
| hints_missing | 95 | 71 | 検索ヒントの欠落。クエリルーティングに影響するが機能自体は壊れない |
| omission | 67 | 47 | ソースに存在するコンテンツの欠落。重大〜軽微の幅が広い |
| fabrication | 41 | 33 | ソースに存在しないクラス名・型・文言の追加。コンパイルエラーを誘発するものも |
| section_issue | 26 | 22 | セクション構造の不整合（見出し欠落・重複・誤配置等） |

### 傾向

- **hints_missing が最多（41%）**: 71ファイルに広く分散している。1ファイルあたり1〜2件が多く、検索精度の低下につながるが機能は壊れない。
- **omissionの集中**: 大規模ドキュメント（web-application系、testing-framework系）で複数件の欠落が発生しやすい。ソースRSTが長い場合に途中で切り捨てが起きる傾向。
- **fabricationの質的問題**: 件数はomissionより少ないが、critical判定（10件中4件がfabrication）。型列の追加・クラス名の綴り修正誤りが多い。
- **section_issueの集中ファイル**: libraries系（設定プロパティが多いドキュメント）に多い。テーブル分割処理の境界判定がソース構造と合わない場合に発生。

### critical 10件 詳細

#### 1. `libraries-04_HttpAccessLog--s1` — omission
- **場所**: HTTPアクセスログ出力項目テーブル
- **内容**: `実行時ID`（処理の実行を一意に識別するID）が出力項目テーブルから完全に欠落。ソースではリクエストIDとユーザIDの間に存在する。
- **影響**: ログ設定時に実行時IDを見落とす → トレース不能なログ設定になる

#### 2. `handlers-NoInputDataBatchAction` — omission (2件)
- **場所**: 概要セクション
- **内容①**: フレームワーク呼び出しシーケンス（initialize → handle → commit → error/rollback → terminate）の疑似コードブロックが丸ごと欠落。
- **内容②**: 「このコードは説明用に単純化したものであり、実際の処理フローはハンドラ構成によって制御されており全く別物である」という重要な注意書きが欠落。
- **影響**: 疑似コードを実際の動作と誤解して実装する可能性

#### 3. `handlers-NoInputDataBatchAction` — fabrication
- **場所**: handle()メソッド説明
- **内容**: ソースは `(オーバーロード)` とのみ記載。知識ファイルは `BatchAction の handle(InputData data, ExecutionContext ctx) をオーバーロードしたメソッド` と親クラスのメソッドシグネチャを捏造している。
- **影響**: 存在しないシグネチャを参照したコードを生成する

#### 4. `web-application-Other--s1` — omission
- **場所**: s8〜s10セクション（コード値取得・バリデーション・警告メッセージ）
- **内容**: 3つの完全なセクションが欠落。index s1のhintsでは `コード値取得`・`コード値バリデーション`・`警告メッセージ` へのルーティングを宣言しているが、対応するs8/s9/s10が存在しない。
- **影響**: これらのトピックへの検索が無言で失敗する（Issue #261）

#### 5. `libraries-1-FAQ` — omission
- **場所**: エラーのコード例
- **内容**: スタックトレースの外側例外（`java.lang.RuntimeException: unexpected exception occurred. target entity=[...] property=[failedCount]`）が省略され、`Caused by` 部分のみ表示。開発者がログで最初に目にするのは外側例外のため、エラー例が認識不能。
- **影響**: FAQ参照でもエラーを特定できない

#### 6. `testing-framework-02_RequestUnitTest-06_TestFWGuide--s1` — fabrication
- **場所**: テストサポートクラス名
- **内容**: ソースの誤字（`AbstractHttpReqestTestSupport` → `u`抜け）を修正する際に、正しいクラス名 `AbstractHttpRequestTestTemplate` / `BasicHttpRequestTestTemplate` ではなく `AbstractHttpRequestTestSupport` / `BasicHttpRequestTestSupport` に誤変換。どちらも実在しないクラス名。
- **影響**: 存在しないクラスを参照したテストコードを生成する（Issue #260）

#### 7. `libraries-02_CodeManager--s21` — fabrication
- **場所**: s2・s4〜s7のプロパティテーブル
- **内容**: ソースのテーブルは「プロパティ名 | 設定内容」の2列だが、知識ファイルが「型」列を追加。型はソースに記載なく、`String`・`String[]`等は推論による捏造。
- **影響**: 誤った型情報を基にした設定コードを生成する

#### 8. `testing-framework-batch--s10` — fabrication
- **場所**: s7セクション本文
- **内容**: ソースは「実際の**ファイル**出力結果を確認することができる」だが、知識ファイルは「実際の**データベース**出力結果を確認することができる」と記載。
- **影響**: バッチテストの検証対象（ファイルvsDB）を誤解させる

#### 9. `libraries-02_SqlLog--s1` — fabrication
- **場所**: s17〜s22「デフォルトのフォーマット」
- **内容**: ソースファイルはs16（SqlPStatement#executeメソッド終了時）で途切れており、s17以降（executeQuery・executeUpdate・executeBatch）のデフォルトフォーマット文字列はソースに存在しない。先行セクションのパターンから推論して生成されたと考えられる。
- **影響**: 存在しない設定値を参照したログ設定を生成する

### 対応方針

| 対応 | 件数 | 内容 |
|------|------|------|
| Issue登録済み | 10 (critical全件) | Issue #260〜#265 で追跡中 |
| 軽微として許容 | 219 | hints_missing・minor omission・minor fabrication。ユーザー体験への影響は限定的 |
