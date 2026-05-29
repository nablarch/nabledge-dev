Step 5: 回答を生成します。

Step 6 (verify): 全てのNablarch固有の主張がセクション内容で裏付けられていることを確認 → PASS。

---

**結論**: 日次・月次などの定期処理には**都度起動バッチ（DB接続有り）**パターンを使用する。`DatabaseRecordReader`でDB入力データを1件ずつ読み込み、`BatchAction`の`handle`メソッドで集計・書き込みを行うのが基本構成。

---

**根拠**:

### 1. ハンドラキュー構成（都度起動バッチ DB接続有り）

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | 終了コード変換 |
| 2 | グローバルエラーハンドラ | 例外ログ出力 |
| 3 | データベース接続管理ハンドラ（初期化用） | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ（初期化用） | トランザクション開始・コミット |
| 5 | リクエストディスパッチハンドラ | アクションクラス決定 |
| 6 | マルチスレッド実行制御ハンドラ | サブスレッド生成 |
| 7 | データベース接続管理ハンドラ（業務処理用） | DB接続取得・解放 |
| 8 | トランザクションループ制御ハンドラ | コミット間隔制御・ループ継続 |
| 9 | データリードハンドラ | 1件ずつレコード読み込み |

### 2. アクションクラスの実装

`BatchAction`を継承し、`createReader`でDBからの読み込み設定、`handle`で1件分の業務ロジックを実装する。

```java
public class SummaryBatchAction extends BatchAction<SummaryInput> {

    @Override
    public DataReader<SummaryInput> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader を使ってDBから入力データを取得
        // 集計に必要な情報はここでJOINして一度に取得する（N+1回避）
        DatabaseRecordReader reader = new DatabaseRecordReader();
        ParameterizedSqlPStatement stmt = 
            DbConnectionContext.getConnection()
                .prepareParameterizedSqlStatementBySqlFile(
                    SummaryInput.class, "FIND_TARGET_RECORDS");
        reader.setStatement(stmt);
        return reader;
    }

    @Override
    public Result handle(SummaryInput inputData, ExecutionContext ctx) {
        // 集計ロジックを実装
        SummaryResult result = new SummaryResult();
        // ... 集計処理 ...

        // 結果を別テーブルに書き込む
        UniversalDao.insert(result);

        return new Result.Success();
    }
}
```

### 3. 大量データへの対応（遅延ロード）

大量レコードを扱う場合は `UniversalDao#defer` を使用してメモリ使用量を抑える。

```java
try (DeferredEntityList<SummaryInput> records
        = (DeferredEntityList<SummaryInput>) UniversalDao.defer()
                .findAllBySqlFile(SummaryInput.class, "FIND_TARGET_RECORDS")) {
    for (SummaryInput record : records) {
        // 処理
    }
}
```

### 4. コミット間隔の設定

`LoopHandler`の`commitInterval`プロパティでコミット間隔を調整し、スループットを向上させる。

```xml
<component class="nablarch.fw.handler.LoopHandler">
  <!-- コミット間隔に1000を指定 -->
  <property name="commitInterval" value="1000" />
</component>
```

### 5. 起動方法

```properties
-requestPath=com.sample.SummaryBatchAction/BATCH0001
```

---

**注意点**:

- **N+1問題を避ける**: `handle`メソッド内で入力データを元に再度SELECTを発行すると、処理対象件数分のSQLが追加発行されて性能劣化が起きる。集計に必要なデータは`createReader`のSQLでJOINして一度に取得すること。
- **フレームワーク外ループを使わない**: `handle`メソッド内で自前のSELECT+ループ処理を実装するとフレームワークのコミット制御が機能せず、トランザクションログが逼迫する。ループはフレームワーク（LoopHandler）に任せること。解決策は`handle`内のSQLを`createReader`に移すこと。
- **遅延ロード中のトランザクション制御**: RDBMSによってはカーソルオープン中にトランザクション制御が行われるとカーソルがクローズされエラーになる場合があるため注意。

参照: `nablarch-batch-architecture.json:s5`, `nablarch-batch-architecture.json:s7`, `nablarch-batch-architecture.json:s8`, `nablarch-patterns-Nablarchバッチ処理パターン.json:s1`, `nablarch-patterns-Nablarchバッチ処理パターン.json:s4`, `nablarch-patterns-Nablarchアンチパターン.json:s4`, `nablarch-patterns-Nablarchアンチパターン.json:s9`, `nablarch-patterns-Nablarchアンチパターン.json:s11`, `libraries-universal-dao.json:s9`, `libraries-universal-dao.json:s14`, `handlers-loop-handler.json:s5`

---