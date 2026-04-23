**結論**: ファイル明細レコードをDBに取り込む夜間バッチは、**Nablarchバッチフレームワーク（都度起動バッチ）** で実装するのが推奨構成。フレームワーク選択→ハンドラ構成→クラス設計の3層で設計する。

---

**根拠**:

**① フレームワーク選択**
Nablarchはバッチに2種類のフレームワークを提供するが、「Nablarchバッチ」を使用することが推奨されている。Jakarta Batchは2020年時点で情報・有識者が少なく学習コストが高い。 (processing-pattern/nablarch-batch/nablarch-batch-batch.json:s1)

夜間定期実行には「都度起動バッチ」を使用する。常駐バッチはマルチスレッド時の遅延リスクがあり新規開発では非推奨。 (processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1)

**② 最小ハンドラ構成（DB接続あり・都度起動バッチ）**
以下の順でハンドラをキューに並べる（メインスレッド→サブスレッドの順）: (processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1)

| No. | ハンドラ | スレッド | 役割 |
|-----|---------|---------|------|
| 1 | StatusCodeConvertHandler | メイン | 終了コード変換 |
| 2 | GlobalErrorHandler | メイン | 例外ログ出力 |
| 3 | DatabaseConnectionManagementHandler（初期処理用） | メイン | DB接続取得/解放 |
| 4 | TransactionManagementHandler（初期処理用） | メイン | トランザクション管理 |
| 5 | RequestPathJavaPackageMapping | メイン | アクションクラス決定 |
| 6 | MultiThreadExecutionHandler | メイン | サブスレッド制御 |
| 7 | DatabaseConnectionManagementHandler（業務処理用） | サブ | 業務用DB接続 |
| 8 | LoopHandler | サブ | レコードループ・コミット制御 |
| 9 | DataReadHandler | サブ | レコード1件読み込み |

**③ クラス設計（3クラス構成）**
ファイル取り込みバッチの業務ロジック: (processing-pattern/nablarch-batch/nablarch-batch-application_design.json:s1)
1. データレコードからフォームクラスを作成してバリデーション実行
2. フォームクラスからエンティティクラスを作成してDBに登録
3. `Success` を返す

- **フォームクラス**: `DataReader` が読み込んだレコードをマッピング。プロパティは全て `String` 型で定義し、バリデーションアノテーションを付与する。
- **エンティティクラス**: DBテーブルと1対1で対応するクラス。
- **アクションクラス**: `BatchAction` を継承し、`handle` メソッドで業務ロジックを実装、`createReader` でデータリーダを返す。

**④ 実装例（CSVファイル取り込みの場合）**

データリーダ: `ObjectMapperFactory.create(ZipCodeForm.class, ...)` で `ObjectMapper` を生成し、`ObjectMapperIterator` でラップして1行ずつ読み込む。`FilePathSetting.getInstance()` でファイルパスを取得する。 (processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2)

アクション: `BeanUtil.createAndCopy(ZipCodeData.class, inputData)` でフォームをエンティティに変換し、`UniversalDao.insert` でDB登録。`@ValidateData` インターセプタで `handle` メソッドには常にバリデーション済みデータが渡される。 (processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s3)

処理の流れ: Main → DataReader（レコード1件読み込み）→ DispatchHandler（アクション特定）→ アクション（業務ロジック実行）→ Result返却、をレコードがなくなるまで繰り返す。 (processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s3)

**⑤ 標準提供のデータリーダ**
ファイル読み込み用として `FileDataReader`、バリデーション機能付きの `ValidatableFileDataReader`、レジューム機能付きの `ResumeDataReader` が標準提供されている。 (processing-pattern/nablarch-batch/nablarch-batch-feature_details.json:s5)

---

**注意点**:
- `FileBatchAction` はデータアクセスに `data_format` を使用している。`data_bind`（CSVバインド等）を使う場合は `BatchAction` など他のアクションクラスを使うこと。 (processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s3)
- 入力ファイルは外部由来のため安全でないデータとみなし、必ずフォームクラス経由でバリデーションを実施すること。DBなど安全な入力源の場合はフォームクラスを省略できる。 (processing-pattern/nablarch-batch/nablarch-batch-application_design.json:s1)
- 常駐バッチはマルチスレッド時に処理遅延が発生する可能性があるため、新規開発では使用しないこと。 (processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1)

参照: processing-pattern/nablarch-batch/nablarch-batch-batch.json:s1, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s3, processing-pattern/nablarch-batch/nablarch-batch-application_design.json:s1, processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s2, processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.json:s3, processing-pattern/nablarch-batch/nablarch-batch-feature_details.json:s5