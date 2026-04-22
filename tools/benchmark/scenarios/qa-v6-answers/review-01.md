**質問**: ファイルの明細レコードを読み込んで DB テーブルに取り込む夜間バッチを作りたい。Nablarch でこういうバッチを実装するときの推奨構成を知りたい。

---

**結論**: 夜間バッチには **都度起動バッチ** を使用し、`BatchAction` を継承したアクションクラス・フォームクラス・エンティティクラスの3層でデータを流す。ハンドラキューは DB 接続ありの標準構成を使う。 — `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s1`

**① バッチ種別の選択**
Nablarch バッチには「都度起動バッチ」と「常駐バッチ」の2種類があり、日次・月次など定期的に起動するケースは都度起動バッチを選ぶ。常駐バッチはマルチスレッド実行時に遅延問題があり、新規開発では代替（db_messaging）が推奨される。 — `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s1`

**② 推奨ハンドラキュー構成（DB 接続あり）**
主要ハンドラは `StatusCodeConvertHandler`、`GlobalErrorHandler`、`DatabaseConnectionManagementHandler`（初期化用・業務用の2段）、`TransactionManagementHandler`、`RequestPathJavaPackageMapping`、`MultiThreadExecutionHandler`、`LoopHandler`、`DataReadHandler`。サブスレッド側に `LoopHandler` → `DataReadHandler` を置き、1レコードずつ業務アクションに渡す。 — `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s1`

**③ クラス設計（3層）**
- **フォームクラス**: データリーダが読み込んだレコードをマッピング。プロパティは全て `String` 型（Bean Validation の都合）。外部ファイルのような安全でない入力には `@Required` / `@Domain` などのバリデーションアノテーションを付与する。 — `processing-pattern/nablarch-batch/nablarch-batch-application_design.json#s1`
- **エンティティクラス**: テーブルと1対1対応。 — `processing-pattern/nablarch-batch/nablarch-batch-application_design.json#s1`
- **アクションクラス**: `BatchAction` を継承。`createReader` でデータリーダを返し、`handle` で `BeanUtil.createAndCopy` によりフォーム→エンティティ変換後に `UniversalDao.insert` で DB 登録し、`new Result.Success()` を返す。 — `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json#s3`

**④ データリーダの作成**
`DataReader` を実装したクラスを用意する。CSV の場合は `FilePathSetting.getInstance()` でファイルパスを解決し、`ObjectMapperFactory.create(Form.class, ...)` で `ObjectMapper` を生成、`ObjectMapperIterator` でラップして `read` / `hasNext` / `close` を実装する。 — `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json#s2`

**⑤ フォームクラス（CSV の場合）**
`@Csv`（`type=CsvType.CUSTOM`）と `@CsvFormat`（`quoteMode=QuoteMode.NORMAL`）を付与し、行番号が必要な場合はゲッタに `@LineNumber` を付与する。 — `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json#s2`

**⑥ 処理の流れ**
Main がハンドラキューを起動 → `DataReader` が1件ずつレコードを提供 → `DispatchHandler` がアクションを特定（`-requestPath` 引数でアクションクラス/リクエスト ID を指定）→ アクションが業務ロジックを実行 → `Result` を返却 → データが尽きるまでループ → `StatusCodeConvertHandler` が終了コードを返す。 — `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s3`、`processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s2`

**注意点**
- `data_bind` で CSV を読む場合は `FileBatchAction` を使ってはならない（`FileBatchAction` は `data_format` ライブラリ前提で、`data_bind` と混在不可）。`BatchAction` を使うこと。 — `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s3`
- `@ValidateData` インターセプタを使うと `handle` に常にバリデーション済みデータが渡り、バリデーションをバッチ間で共通化できる。 — `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json#s3`
- 標準提供のファイル用データリーダ（`FileDataReader`、`ValidatableFileDataReader`、`ResumeDataReader`）の利用も検討できる。 — `processing-pattern/nablarch-batch/nablarch-batch-feature_details.json#s5`
