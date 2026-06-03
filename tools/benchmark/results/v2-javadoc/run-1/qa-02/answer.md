Step 4のセクション読み込みが完了しました。Step 5で回答を生成します。

**結論**: Nablarchバッチの「都度起動バッチ（DB to DBパターン）」で実装する。`DatabaseRecordReader`に集計SQLを渡して1件ずつ読み込み、`BatchAction#handle`で結果テーブルへ書き込む構成が基本形。

**根拠**:

### 全体構成

```
Main（共通起動ランチャ）
  └── ハンドラキュー
        ├── ステータスコード→プロセス終了コード変換ハンドラ
        ├── グローバルエラーハンドラ
        ├── データベース接続管理ハンドラ（初期処理/終了処理用）
        ├── トランザクション制御ハンドラ（初期処理/終了処理用）
        ├── リクエストディスパッチハンドラ
        ├── マルチスレッド実行制御ハンドラ
        ├── データベース接続管理ハンドラ（業務処理用）
        ├── トランザクションループ制御ハンドラ  ← コミット間隔制御
        └── データリードハンドラ
```

都度起動バッチ（DB接続あり）の最小ハンドラ構成そのままが基本形。起動は`-requestPath=アクションクラス名/リクエストID`で指定する。

### アクションクラスの実装

```java
public class AggregationBatchAction extends BatchAction<SalesForm> {

    @Override
    public Result handle(SalesForm inputData, ExecutionContext ctx) {
        // 1件分のデータをもとに集計結果テーブルへ書き込む
        SummaryEntity summary = BeanUtil.createAndCopy(SummaryEntity.class, inputData);
        UniversalDao.insert(summary);
        return new Result.Success();
    }

    @Override
    public DataReader<SalesForm> createReader(ExecutionContext ctx) {
        // 集計SQLをここで発行し、DatabaseRecordReaderに渡す
        DatabaseRecordReader reader = new DatabaseRecordReader();
        reader.setStatement(/* 集計SQLを設定 */);
        return reader;
    }
}
```

### 集計SQLの考え方

**推奨**: 集計処理（GROUP BY / 集約関数）はSQL側に寄せ、`createReader`の1クエリで完結させる。

```sql
SELECT
    dept_id,
    SUM(amount) AS total_amount,
    COUNT(*) AS record_count
FROM
    sales
WHERE
    sale_date = ?
GROUP BY
    dept_id
```

`handle`メソッドは1行分の集計結果を受け取って書き込むだけにすることで、SQLの強力な集計機能を活用できる。

### 注意点

**N+1問題の回避**: `handle`メソッド内で再度SELECTを発行するとN+1問題が発生し、件数増加で深刻な性能劣化になる。JOINや集計はcreateReader側のSQL1本に集約すること。

**自前ループ禁止**: `handle`内で自前のforループ＋UPDATE処理を実装すると、フレームワークのコミット間隔制御が効かず、トランザクションログを逼迫する。ループ処理はフレームワーク（トランザクションループ制御ハンドラ）に任せること。

**大量データの場合**: `UniversalDao.defer()` を使った遅延ロードは、バッチでの大量データ処理向けだが、カーソルオープン中のトランザクション制御でカーソルがクローズされる場合があるため、使用するRDBMSの仕様を確認すること。

---

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-patterns-Nablarchアンチパターン.json:s4, nablarch-patterns-Nablarchアンチパターン.json:s9

---