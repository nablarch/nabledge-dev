**結論**: DBからデータを読み込んで集計し別テーブルに書き込む定期処理は、Nablarchバッチの「都度起動バッチ」として「DB to DB」パターンで実装します。`DatabaseRecordReader`でSELECT結果を1件ずつ読み込み、`BatchAction`の`handle`メソッドで集計・書き込みを行う構成が基本です。

---

**根拠**:

**全体構成（DB to DBパターン）**

入力はSELECT文の結果セットの各レコードで、1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません。

**処理の流れ**

1. `Main`（共通起動ランチャ）がハンドラキューを実行する
2. `DatabaseRecordReader`が入力テーブルからデータを1件ずつ提供する
3. `BatchAction`の`handle`メソッドが1件ごとに集計・書き込みロジックを実行する
4. 処理対象データがなくなるまで2〜3を繰り返す

**ハンドラ構成（都度起動バッチ・DB接続有りの最小構成）**

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | 終了コード変換 |
| 2 | グローバルエラーハンドラ | 例外ログ出力 |
| 3 | データベース接続管理ハンドラ（初期処理用） | DB接続取得/解放 |
| 4 | トランザクション制御ハンドラ（初期処理用） | 初期処理のトランザクション管理 |
| 5 | リクエストディスパッチハンドラ | アクションクラス決定 |
| 6 | マルチスレッド実行制御ハンドラ | サブスレッド起動 |
| 7 | データベース接続管理ハンドラ（業務処理用） | 業務DB接続管理 |
| 8 | トランザクションループ制御ハンドラ | コミット間隔制御・ループ継続 |
| 9 | データリードハンドラ | 1件読み込み→アクションへ渡す |

**アクションクラスの実装例**

```java
public class SummaryBatchAction extends BatchAction<SummaryForm> {

    @Override
    public Result handle(SummaryForm inputData, ExecutionContext ctx) {
        // 集計処理
        SummaryResult result = BeanUtil.createAndCopy(SummaryResult.class, inputData);
        // 集計値を計算してセット
        result.setSummaryValue(calculate(inputData));
        // 別テーブルに書き込み
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<SummaryForm> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader で読み込み元テーブルをSELECT
        DatabaseRecordReader reader = new DatabaseRecordReader();
        reader.setStatement(/* SQLを設定 */);
        return reader;
    }
}
```

**起動コマンド例**

```bash
java nablarch.fw.launcher.Main \
  -requestPath=com.example.SummaryBatchAction/BATCH001 \
  -diConfig=classpath:batch-config.xml \
  -userId=batch_user
```

---

**注意点**:
- `DatabaseRecordReader`はデフォルトで遅延ロードを使用するため、大量データでも一括でメモリに読み込まれない
- コミット間隔は`トランザクションループ制御ハンドラ`の設定で調整できる（処理件数が多い場合は適切な間隔を設定すること）
- 集計処理でGROUP BYが必要な場合は、入力SQL自体に集計クエリを持たせる方法も有効（`DB to DB`パターンの推奨アプローチ）

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-batch-getting-started-nablarch-batch.json:s3