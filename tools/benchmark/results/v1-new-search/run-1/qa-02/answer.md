**結論**: DB to DBの定期処理は「都度起動バッチ」として実装します。`BatchAction`を継承したアクションクラスを作成し、`createReader`でSQLによるデータ読み込み（集計クエリをJOINで行う）、`handle`メソッドで書き込み先テーブルへの登録・更新を実装するのが基本構成です。

**根拠**:

### 処理方式の選択

「DB to DB」の定期処理（日次・月次など）は**都度起動バッチ**が適合します。

> 都度起動バッチ：日次や月次など、定期的にプロセスを起動してバッチ処理を実行する。

### 全体構成

```
Main (共通起動ランチャ)
  └─ ハンドラキュー
       ├─ ステータスコード→プロセス終了コード変換ハンドラ
       ├─ グローバルエラーハンドラ
       ├─ データベース接続管理ハンドラ（初期処理/終了処理用）
       ├─ トランザクション制御ハンドラ（初期処理/終了処理用）
       ├─ リクエストディスパッチハンドラ
       ├─ マルチスレッド実行制御ハンドラ
       ├─ データベース接続管理ハンドラ（業務処理用）  ← サブスレッド
       ├─ トランザクションループ制御ハンドラ          ← サブスレッド（コミット間隔制御）
       └─ データリードハンドラ                       ← サブスレッド
```

### アクションクラスの実装

`BatchAction`を継承して実装します。

```java
public class SummaryBatchAction extends BatchAction<SummaryInputForm> {

    @Override
    public DataReader<SummaryInputForm> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader を使って集計対象データを読み込む
        // 集計はSQLのGROUP BYやJOINで行い、handleメソッド内での追加SELECTを避ける
        return new DatabaseRecordReader()
            .setStatement(ParameterizedSqlStatementFactory.createParameterized(
                DbConnectionContext.getConnection(), "BATCH001", new Object()));
    }

    @Override
    public Result handle(SummaryInputForm inputData, ExecutionContext ctx) {
        SummaryResult result = BeanUtil.createAndCopy(SummaryResult.class, inputData);
        UniversalDao.insert(result);  // または update
        return new Result.Success();
    }
}
```

### 起動方法

```bash
java nablarch.fw.launcher.Main \
  -requestPath=com.example.SummaryBatchAction/SUMMARY001 \
  -diConfig=classpath:batch-config.xml \
  -userId=batch_user
```

**注意点**:

1. **handleメソッド内でのSELECT禁止（N+1問題）**: `handle`メソッド内で入力データを元に再度SELECTを発行するとN+1問題が発生します。集計に必要なデータはすべて`createReader`のSQLでJOINまたはGROUP BYして取得してください。

2. **自前ループの禁止**: `handle`内で自前のループ処理（`for`ループでSELECT→UPDATEを繰り返すなど）を実装しないでください。フレームワークが管理するループ（`トランザクションループ制御ハンドラ`）の外で大量更新すると、トランザクションログが逼迫します。

3. **コミット間隔**: `トランザクションループ制御ハンドラ`の設定でコミット間隔（何件ごとにコミットするか）を制御できます。大量データの場合は適切な間隔を設定してください。

参照: nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchアンチパターン.json:s4, nablarch-patterns-Nablarchアンチパターン.json:s9