**結論**: ファイル明細レコードをDBテーブルに取り込む夜間バッチは、Nablarchバッチの **都度起動バッチ（FILE to DBパターン）** で実装するのが推奨構成。ポイントは「ファイル → テンポラリテーブルへのINSERT」に処理を限定し、業務処理は加えないことと、`data_bind` を使う場合はテンプレートクラス・データリーダの選択に注意すること。

---

**根拠**:

**① 都度起動バッチを選択する**
夜間バッチのように定期的にプロセスを起動して実行するケースは「都度起動バッチ」が適切。常駐バッチはDB監視用であり、FILE to DB構成とは組み合わせない。
(`processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1`, `guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json:s2`)

**② 推奨パターン：ファイル → テンポラリテーブルINSERT**
FILE to DBでは、ファイルのレイアウトと1対1に対応するカラムを持つテンポラリテーブルにINSERTする。業務処理はできるだけ加えないこと。これによりRDBのトランザクション・SQLが活用でき、マッチング処理はSQLのJOINで、コントロールブレイクはGROUP BYで代替できる。
(`guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json:s2`)

**③ アクションクラスの実装**
アクションクラスはDataReaderを生成し、読み込んだレコードに対して以下の業務ロジックを実行して `Result` を返す。
1. データレコードからフォームクラスを作成してバリデーション実行
2. フォームクラスからエンティティクラスを作成してDBにデータ追加
3. `Success` を返す
(`processing-pattern/nablarch-batch/nablarch-batch-application_design.json:s1`)

**④ データリーダの選択**
標準データリーダとして以下が提供される。
- `FileDataReader` — ファイル読み込み
- `ValidatableFileDataReader` — バリデーション機能付き
- `ResumeDataReader` — 障害発生時の再開機能付き（ファイル入力限定）

ただし `FileDataReader` / `ValidatableFileDataReader` は `data_format` を使用。`data_bind`（CSV等）を使う場合はこれらを使わず、`DataReader` インタフェースを自前実装し `ObjectMapper`/`ObjectMapperIterator` でCSVをバインドするカスタムDataReaderを作成する。
(`processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s2`, `processing-pattern/nablarch-batch/nablarch-batch-feature_details.json:s5`, `processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2`)

**⑤ 最小ハンドラ構成（DB接続有り、都度起動）**
メインスレッド: `StatusCodeConvertHandler` → `GlobalErrorHandler` → `DatabaseConnectionManagementHandler`（初期処理用）→ `TransactionManagementHandler`（初期処理用）→ `RequestPathJavaPackageMapping` → `MultiThreadExecutionHandler`
サブスレッド: `DatabaseConnectionManagementHandler`（業務用）→ `LoopHandler` → `DataReadHandler` → アクションクラス
(`processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1`)

**⑥ ファイルの移動・コピーはバッチ処理に含めない**
ファイルの移動・コピーを取り込みバッチと別ジョブにすることで、処理失敗時の再実行前に入力ファイルを元のディレクトリへ戻す手動オペレーションが不要になり、テストも容易になる。
(`guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json:s3`)

---

**注意点**:
- `data_bind` でCSVを扱う場合、フォームクラスに `@Csv`/`@CsvFormat` を付与し、カスタムDataReader（`ObjectMapperIterator` ラッパー）を実装する必要がある。`FileBatchAction` / `FileDataReader` は `data_format` 専用のため混在不可。(`processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s2`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s3`)
- `LoopHandler` でコミット間隔を設定することで大量データのメモリ問題を回避できる。(`processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1`)
- 再開機能が必要な場合は `ResumeDataReader` を使用するが、ファイル入力限定。DB入力の再開はアプリ側で設計が必要。(`processing-pattern/nablarch-batch/nablarch-batch-functional_comparison.json:s1`)

参照: processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s2, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s3, processing-pattern/nablarch-batch/nablarch-batch-application_design.json:s1, processing-pattern/nablarch-batch/nablarch-batch-feature_details.json:s5, processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2, processing-pattern/nablarch-batch/nablarch-batch-functional_comparison.json:s1, guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json:s2, guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json:s3