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

### 重大以外の残存問題 — 具体的な内容と傾向

#### fabrication（41件・33ファイル）— ソースにない情報の追加

fabricationには4つの類型がある。

**① タイポ修正の誤変換（クラス名破壊）**
ソースの誤字を補正しようとして、実在しない別の名前を生成するケース。
`testing-framework-02_RequestUnitTest-06_TestFWGuide--s1`: ソースのテーブルには `AbstractHttpReqestTestSupport`/`BasicHttpReqestTestSupport`（'u'抜け）と記載されているが、RSTの見出し構造が示す正しい名前は `AbstractHttpRequestTestTemplate`/`BasicHttpRequestTestTemplate`。知識ファイルはスペルを修正する際に「Template」を「Support」に変えてしまい、`AbstractHttpRequestTestSupport`/`BasicHttpRequestTestSupport` という実在しない名前を生成した。これは critical #6 として Issue #260 で追跡済みだが、同様のパターンが他ファイルのminor findingにも散在している。

**② 型列の推論追加（プロパティテーブル）**
ソースの設定プロパティテーブルが「プロパティ名 | 設定内容」の2列構成なのに、知識ファイルが「型」列を追加して `String`/`String[]`/`boolean` 等を記入するケース。型はソースに存在せず、文脈推論による捏造。
例: `libraries-02_CodeManager--s21` 全セクション。`tableName`・`idColumnName`・`valueColumnName`・`langColumnName`・`sortOrderColumnName` のすべてに `String` 型が付与されているが、ソースに型の記述は一切ない。この類型は libraries系ファイルに集中しており、同ファイルの複数セクションにまたがって発生している（critical #7 も同ファイル）。

**③ 文字列置換による意味の反転**
単純な単語置換が意味を逆転させるケース。
`testing-framework-batch--s10` s7: ソース「実際の**ファイル**出力結果を確認することができる」→ 知識ファイル「実際の**データベース**出力結果を確認することができる」。バッチテストの検証対象（ファイルvsDB）を完全に逆転させている（critical #8）。
この種の単純置換ミスはminor findingにも見られる。例: `nablarch-batch-04_fileInputBatch--s1` s5 で、ソースの記述語「RecordTypeBindingハンドラ」から `RecordTypeBindingHandler` というJavaクラス名を生成しているが、このクラス名はソースには現れない。

**④ 日本語表記からのJavaクラス名推論**
ソースが「バッチアクション」等の日本語概念名のみで記述しているのに、知識ファイルのhintsや本文に `BatchAction` 等のJavaクラス名を記入するケース。クラスがそのソースファイルに実際に現れていない場合、fabricationとなる。`nablarch-batch-04_fileInputBatch--s1` s2 で確認。

---

#### omission（67件・47ファイル）— ソースにある内容の欠落

**① 動作の前提・スコープ説明の欠落**
機能の適用範囲・前提条件を述べた文が丸ごと省略されるケース。開発者が機能を誤った文脈で使用するリスクがある。
- `testing-framework-01_UnitTestOutline--s1` s2: ソース「これらのクラスの実装およびクラス単体テストの概念は、バッチや画面オンラインといった処理の形態に依存しない共通のものとなっている。」→ 欠落。この文があるとForm/Componentクラス単体テストがすべての処理形態に共通であることがわかる。
- 同ファイル s3: リクエスト単体テストの範囲外項目を4つ列挙しているが、なぜ範囲外なのかの技術的理由「HTTPリクエスト送信を擬似しているだけであり、実際にブラウザ上からサブミットしている訳ではない」が欠落。

**② 機能・仕様の付帯説明の欠落**
画面・機能の目的を述べた短文が省略されるケース。
- `web-application-01_spec` s2: ソースは各画面に「○○を表示する。」という目的文を明示しているが、ユーザ情報登録画面・確認画面の両方で目的文が欠落。
- `testing-framework-01_Abstract--s8` s2: ソース「また、データの個数も複数記述できる。」→ 欠落。データシートに複数データを記述できるという重要な機能説明が失われる。

**③ コード例・エッジケースの欠落**
コードサンプルや境界条件の具体例が省略されるケース。
- `testing-framework-01_Abstract--s8` s6: ダブルクォート解析のエッジケース（`"ab"c"` → `ab"c`、`"abc""` → `abc"` 等）が全て欠落。外側クォートのみ除去するという挙動の正確な説明ができなくなる。
- `testing-framework-01_entityUnitTest--s1` s4/s6: `@Test` メソッド本体、`ENTITY_CLASS` 定数定義、`sheetName`/`id` 変数の具体的な代入例が丸ごと省略。メソッド名のみが残り、実際の使い方が不明になる。

**④ 重大処理フローの欠落（critical）**
`handlers-NoInputDataBatchAction` の疑似コードブロックと注意書きの欠落はcritical #2として上記に詳述。同類型のminorケースも testing-framework 系で複数発生している。

---

#### section_issue（26件・22ファイル）— セクション構造の不整合

**① セクションタイトルが空文字列**
indexのtitle項目が `""` になっており、RSTには明確な見出しが存在するケース。タイトルベースの参照ができなくなる。
- `testing-framework-01_Abstract--s1` s1: ソース見出し「特徴」→ title `""`
- `testing-framework-02_DbAccessTest--s1`: s2「全体像」→ title `""`、s10「DBに準備データのカラムを省略する場合」→ title `""`

この類型はtesting-framework系の複数ファイルに分散しており、見出しが `====` (h2相当) 以下のレベルで区切られる場合に起きやすい。

**② 独立した見出しが1セクションに統合**
RSTに複数の独立した `=====` 見出しがあるのに、1つのセクションにまとめられるケース。V3ルール（2000文字超・h3以下の見出しを持つ場合は分割）の境界判定がずれているときに発生。
- `testing-framework-02_RequestUnitTest--s12` s6: 「ThreadContextへの値設定は不要」と「テストクラスでのトランザクション制御は不要」という独立した2見出しが1セクションに統合。
- `libraries-02_CodeManager--s21` s7: 「エンティティの実装」「Validatorの設定」「設定内容詳細（CodeValueValidator）」の3見出しが1セクションに統合し、2000文字超に。

この類型はlibraries系（設定プロパティが多いドキュメント）に集中。プロパティテーブルが連続する場合にページ境界の判定がずれる。

**③ RST構文の残留**（件数は少ないが確認）
`:ref:` や `.. note::` 等のRSTディレクティブが変換されず知識ファイルに残るケース。1〜2件確認。

---

#### hints_missing（95件・71ファイル）— 検索ヒントの欠落

1ファイルあたり1〜2件が典型で、71ファイルに広く分散している。問題の本質は「そのセクションに到達できるはずのクエリがルーティングされなくなる」こと。

**① インタフェース名・実装クラス名の欠落**
ソース本文でインタフェース名が明示されているのに、hintsに入らないケース。Javaコードを書く際に最も参照したい名前が抜ける。
- `libraries-02_CodeManager--s21` s1: ソース「CodeManager インタフェースを実装したクラスを登録する必要がある」→ `CodeManager` がhintsに欠落。
- `nablarch-batch-04_fileInputBatch--s1` s4: コードブロックに `return new FileLayoutValidatorAction()` が存在→ `FileLayoutValidatorAction` がhintsに欠落。

**② テスト対象エンティティがhintsに入っていない**
テストクラス名はhintsに入るが、テスト対象のエンティティクラス名が入らないケース。
- `testing-framework-01_entityUnitTest--s7` s3/s4: コード例で `SystemAccountEntity` が多用されているが、hintsには `SystemAccountEntityTest`（テストクラス）のみ。エンティティ名での検索がルーティングされない。

**③ メソッド名・定数名の欠落**
ソースコード例に現れるメソッド名が抜けるケース。
- `libraries-02_CodeManager--s21` s7: ソースコードに `validateAndConvertRequest` メソッドが明示されているが hintsに欠落。
- `testing-framework-01_entityUnitTest--s7` s3: `testValidateCharsetAndLength` メソッド名がhintsに欠落。

**④ RST名前付きアンカーの欠落**
ソースが `:ref:\`anchor_name\`` 形式で内部参照しているアンカー名が抜けるケース。
- `testing-framework-01_Abstract--s8` s2: アンカー `default_values_when_column_omitted` がhintsに欠落。ドキュメント内クロスリファレンスを追う際のルーティングが機能しない。

**⑤ 日本語専用ソースでの英語用語欠落**
ソースが日本語のみで記述されている場合、対応するJava用語がhintsに入らない傾向がある。hints_missingが71ファイルに広く分散している主因はこれで、特にtesting-framework系（テスト概念の日本語説明が多い）とmom-messaging系（プロトコル・メッセージング用語の日本語解説が多い）に集中している。

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

---

## Phase D/E ラウンド挙動の事実調査 (2026-03-30)

### ラウンド構成（report.json より）

| ラウンド | Phase D検出 | Phase E修正 |
|---------|------------|------------|
| r1 | 92 critical, 453 minor（246ファイル） | 全246ファイルに修正実施 |
| r2 | 32 critical, 309 minor（182ファイル） | 全182ファイルに修正実施 |
| r3（最終確認） | 10 critical, 219 minor | 修正なし |

### Q1: 2ラウンド回してもcriticalが残る理由

事実から確認できた原因は2つ。

**① r1/r2で未検出（Phase Eへの入力なし）**

以下のcriticalはr1/r2のfindings jsonに存在せず、Phase Eが修正対象として一度も受け取らなかった：

| ファイル | r3のcritical | r1 | r2 |
|---------|------------|-----|-----|
| `libraries-04_HttpAccessLog--s1` | 実行時ID欠落 | 未報告 | 未報告 |
| `libraries-1-FAQ` | 外側RuntimeException欠落 | 未報告 | clean |
| `handlers-NoInputDataBatchAction` | 疑似コードブロック欠落（2件） | 未報告 | 未報告 |

**② `web-application-Other--s1` の振動（ソース切断による構造的不解決）**

ソースが途中で切れており、修正が物理的に不可能：

- r1: s8-s10欠落 → Phase E r1: 架空のs8-s10を生成
- r2: s8-s10が fabrication（3件 critical）→ Phase E r2: s8-s10を削除
- r3: s8-s10が再び欠落（omission に戻る）

omission → fabrication → omission のループ。ソースの切断問題を「修正」しようとする限り解決不能。

### Q2: ラウンド中に新たな問題を埋め込んでいるか

**事実：r3のcritical 10件中7件はPhase Eの修正が発生源。**

Phase E execution logの入力・出力を照合した結果：

| ファイル | 埋め込みラウンド | Phase Eへの指示（実際のfindings） | Phase Eが実際に行ったこと |
|---------|--------------|-------------------------------|------------------------|
| `handlers-NoInputDataBatchAction` | r2 | `(オーバーロード)` の記述追加（minor omission） | `handle(InputData data, ExecutionContext ctx)` というシグネチャを追記。`InputData` はソースに存在しない |
| `libraries-1-FAQ` | r1 | hintsに `SingleValidationTester` 追加（minor hints_missing） | hintsを追加しつつ、指示されていないスタックトレースをセクション本文に追記。外側 `RuntimeException` を省略した不完全な形 |
| `testing-framework-02_RequestUnitTest-06_TestFWGuide--s1` | r1 | 前提事項セクション追加（critical omission） | 新セクション追加時にクラス名を `AbstractHttpRequestTestTemplate` → `AbstractHttpRequestTestSupport` に誤変換 |
| `libraries-02_CodeManager--s21` | r1 | s7の空アンカーとhintsの修正（minor） | 指示外のs2/s4/s5/s6/s7プロパティテーブルに型列を追加 |
| `testing-framework-batch--s10` | r2 | s7を3セクションに分割（minor section_issue） | 分割時にs7本文を再生成し「データベース出力結果」と記述。r1で「ファイル出力結果」に修正済みだったものを再び誤変換 |
| `libraries-02_SqlLog--s1` | r2 | s17-s22の欠落セクション追加（critical omission） | ソースが切断されており内容が存在しないのに、前セクションのパターンから推論してフォーマット文字列を生成 |
| `web-application-Other--s1` | r1 | s8/s9/s10を追加（critical omission） | ソース切断にもかかわらずCodeUtil等を使った架空の内容を生成 |

### 埋め込みパターン（事実から観察）

**P-A: 指示範囲外の変更**
`libraries-02_CodeManager--s21`：型列追加は指示されていない。`libraries-1-FAQ`：hints修正の指示に対してセクション本文も変更した。

**P-B: ソース参照なしの補完**
`handlers-NoInputDataBatchAction`（`InputData` シグネチャ）、`testing-framework-02_RequestUnitTest-06_TestFWGuide--s1`（`Support` vs `Template`）、`libraries-02_SqlLog--s1`（フォーマット文字列）のいずれも、ソースに存在しない内容をPhase Eが自力生成している。

**P-C: セクション再生成時の誤変換**
`testing-framework-batch--s10`：既存の正しい文章をセクション分割の際に書き直して誤変換。r1で修正済みの fabrication が r2 で再発。
