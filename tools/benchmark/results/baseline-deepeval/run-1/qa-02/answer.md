Step 5〜8: 回答を生成し、検証します。

**Verify確認：**
- 都度起動バッチ（定期処理に使用）→ s1バッチパターンで確認済み
- DB to DBパターン（SELECT結果を1件ずつ受け取りDB更新）→ s4バッチパターンで確認済み
- `DatabaseRecordReader`（DB読み込み）→ s7アーキテクチャで確認済み
- `BatchAction`（汎用テンプレート）→ s8アーキテクチャで確認済み
- ハンドラ構成（都度起動バッチ最小構成）→ s5アーキテクチャで確認済み
- `UniversalDao.findAllBySqlFile`、`UniversalDao.insert`/`batchInsert` → s7/s14ユニバーサルDAOで確認済み
- `UniversalDao.defer()` 遅延ロード → s9で確認済み

verify_result = PASS

---

**結論**: DBからデータを読み込んで集計し、結果を別テーブルに書き込む定期処理は、Nablarchバッチの**都度起動バッチ（DB to DBパターン）**として実装します。`DatabaseRecordReader` でSELECT結果を1件ずつ読み込み、`BatchAction` の `handle` メソッドで集計・書き込み処理を行う構成が基本です。

**根拠**:

### 全体構成

```
javaコマンド
  └─ Main（共通起動ランチャ）
       └─ ハンドラキュー
            ├─ [メインスレッド] ステータスコード変換、グローバルエラー、DB接続(初期)、TX制御(初期)、ディスパッチ、マルチスレッド
            └─ [サブスレッド]  DB接続(業務)、トランザクションループ制御、データリード
                                  └─ BatchAction#handle（業務ロジック）
```

### ① 起動方法の選択

日次・月次などの定期処理には **都度起動バッチ** を使用します（cronやジョブスケジューラから起動します）。

### ② ハンドラ構成（都度起動バッチ、DB接続あり）

コンポーネント定義ファイルに以下のハンドラを設定します：

| No | ハンドラ | スレッド |
|----|----------|----------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | メイン |
| 2 | グローバルエラーハンドラ | メイン |
| 3 | データベース接続管理ハンドラ（初期処理用） | メイン |
| 4 | トランザクション制御ハンドラ（初期処理用） | メイン |
| 5 | リクエストディスパッチハンドラ | メイン |
| 6 | マルチスレッド実行制御ハンドラ | メイン |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブ |
| 8 | トランザクションループ制御ハンドラ | サブ |
| 9 | データリードハンドラ | サブ |

### ③ データリーダ（入力側: DB読み込み）

入力テーブルのSELECT結果を1件ずつ読み込むには `DatabaseRecordReader` を使用します。

### ④ アクションクラス（集計・書き込み）

`BatchAction` を継承し、`handle` メソッドに1件分の集計・書き込みロジックを実装します：

```java
public class AggregationBatchAction extends BatchAction<SalesEntity> {

    @Override
    public DataReader<SalesEntity> createReader(ExecutionContext ctx) {
        // DatabaseRecordReaderを使い、入力テーブルをSELECT
        return new DatabaseRecordReader()
                .setStatement(/* 入力テーブルのSQL */, ctx);
    }

    @Override
    public Result handle(SalesEntity inputData, ExecutionContext ctx) {
        // 集計処理を実施し、結果エンティティを生成
        AggregationResult result = aggregate(inputData);

        // 結果テーブルに書き込む（単件insert）
        UniversalDao.insert(result);

        return new Result.Success();
    }
}
```

大量データを処理する場合は `UniversalDao.defer()` で遅延ロードを使用します：

```java
try (DeferredEntityList<SalesEntity> sales
        = (DeferredEntityList<SalesEntity>) UniversalDao.defer()
                .findAllBySqlFile(SalesEntity.class, "SELECT_FOR_AGGREGATION")) {
    for (SalesEntity s : sales) {
        // 1件ずつ処理
    }
}
```

まとめて書き込む場合は `batchInsert` でラウンドトリップを削減できます：

```java
UniversalDao.batchInsert(resultList);  // パフォーマンス改善
```

**注意点**:
- `batchInsert` / `batchUpdate` では排他制御（楽観ロック）が機能しないため、排他制御が必要な更新は1件ずつの更新処理を使用してください
- 大量データの遅延ロード中にトランザクション制御が行われると、RDBMSによってはカーソルがクローズされる場合があります。使用するDBのマニュアルで挙動を確認してください

参照: nablarch-batch-architecture.json:s1, nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, libraries-universal-dao.json:s7, libraries-universal-dao.json:s9, libraries-universal-dao.json:s14

---