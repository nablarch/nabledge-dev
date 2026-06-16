**結論**: DBからデータを読んで集計し別テーブルに書き込む定期処理は、Nablarchバッチの「都度起動バッチ」＋「DB to DBパターン」で実装します。`DatabaseRecordReader` で入力テーブルをSELECTし、`BatchAction#handle` で1レコードずつ集計ロジックを実行し、`UniversalDao` で結果テーブルに書き込む構成が標準です。

**根拠**:

### 全体構成の概要

```
javaコマンド起動
  └─ Main（共通起動ランチャ）
       └─ ハンドラキュー
            ├─ データベース接続管理ハンドラ（初期処理/終了処理用）
            ├─ トランザクション制御ハンドラ（初期処理/終了処理用）
            ├─ リクエストディスパッチハンドラ
            ├─ マルチスレッド実行制御ハンドラ
            ├─ データベース接続管理ハンドラ（業務処理用）
            ├─ トランザクションループ制御ハンドラ  ← コミット間隔制御
            └─ データリードハンドラ → BatchAction#handle（1件ずつ）
```

処理方式は**DB to DB**です（入力はSELECT結果セット、出力はDBへのINSERT/UPDATE）。1レコードの処理中の更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません。

### 実装する主なクラス

**1. データリーダ（入力テーブルの読み込み）**

`DatabaseRecordReader` を使うと、指定したSQLの結果を1件ずつ `BatchAction` に渡せます。大量データを扱う場合は `UniversalDao.defer()` による遅延ロードも利用できます。

```java
// 遅延ロードを使う場合の例（大量データ向け）
try (DeferredEntityList<SummaryInput> list
        = (DeferredEntityList<SummaryInput>) UniversalDao.defer()
                .findAllBySqlFile(SummaryInput.class, "SELECT_FOR_SUMMARY")) {
    for (SummaryInput row : list) {
        // rowを使った処理
    }
}
```

**2. アクションクラス（集計ロジック＋書き込み）**

`BatchAction` を継承し、`handle` メソッドに集計ロジックと結果テーブルへの書き込みを実装します。

```java
public class SummaryBatchAction extends BatchAction<SummaryInput> {

    @Override
    public Result handle(SummaryInput inputData, ExecutionContext ctx) {
        // 集計ロジックを実行
        SummaryResult result = new SummaryResult();
        // ... inputData を元に集計値を計算 ...

        // 結果テーブルに書き込み
        UniversalDao.insert(result);  // 新規登録の場合
        // または UniversalDao.update(result); // 更新の場合

        return new Result.Success();
    }

    @Override
    public DataReader<SummaryInput> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader を返す
        return new DatabaseRecordReader()
                .setSqlId("SELECT_FOR_SUMMARY");
    }
}
```

### 複数レコードをまとめて書き込む場合

集計結果を一括で書き込む場合は `UniversalDao.batchInsert` / `batchUpdate` を使います（ラウンドトリップ回数を削減できます）。

```java
// 例：List<SummaryResult> にまとめてから一括挿入
UniversalDao.batchInsert(summaryResultList);
```

### 起動コマンド例

```bash
java nablarch.fw.launcher.Main \
  -requestPath com.example.SummaryBatchAction/SUMMARY_BATCH \
  -diConfig classpath:summary-batch.xml \
  -userId batch_user
```

**注意点**:
- `UniversalDao.defer()` を使う場合、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされる可能性があります（RDBMSによる）。トランザクションループ制御ハンドラの `commitInterval` 設定とカーソルの挙動を合わせて確認してください。
- `UniversalDao.batchUpdate` による一括更新では排他制御が行われないため、排他制御が必要な場合は1レコードずつ更新してください。

参照: nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-batch-getting-started-nablarch-batch.json:s3, libraries-universal-dao.json:s9, libraries-universal-dao.json:s14