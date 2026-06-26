**結論**: NablarchバッチでDB→集計→別テーブル書き込みを実現するには、`DatabaseRecordReader`（データリーダ）と アクションクラス（`ActionClass`）の2つを実装します。読み込み元テーブルのレコードを1件ずつ処理し、アクションクラス内の業務ロジックで集計してUniversalDao経由で書き込みます。

**根拠**:

**実装構成の3要素**:

1. **DataReader（入力）**: `DatabaseRecordReader` でDBから1件ずつレコードを読み込む
2. **アクションクラス（業務ロジック）**: `DataReader`が返すレコードをもとに集計し、結果をエンティティクラスにセットして別テーブルへ書き込む
3. **エンティティクラス**: 入力テーブル用と書き込み先テーブル用をそれぞれ用意する

```
// アクションクラスの構造イメージ
public class AggregationBatchAction extends BatchAction<SqlRow> {

    // 入力DataReaderの生成
    @Override
    public DataReader<SqlRow> createReader(ExecutionContext context) {
        return new DatabaseRecordReader()
            .setStatement(
                UniversalDao.findAllBySqlFile(InputEntity.class, "READ_TARGET_DATA"),
                new Object[0]
            );
    }

    // 1件ごとの業務ロジック（集計 → 書き込み）
    @Override
    public Result handle(SqlRow inputRecord, ExecutionContext context) {
        // エンティティに変換して集計処理
        ResultEntity result = aggregateAndMap(inputRecord);
        // 別テーブルへ書き込み（INSERT or UPDATE）
        UniversalDao.insert(result);
        return new Result.Success();
    }
}
```

**ハンドラキュー構成**（`batch-component-configuration.xml`）:

```xml
<!-- データベース接続管理（必須） -->
<component class="nablarch.common.handler.DbConnectionManagementHandler"/>
<!-- トランザクションループ制御（コミット間隔を制御する） -->
<component class="nablarch.fw.handler.LoopHandler">
    <property name="commitInterval" value="1000"/>
</component>
<!-- データリードハンドラ（DataReaderを呼び出す） -->
<component class="nablarch.fw.handler.DataReadHandler"/>
<!-- リクエストディスパッチ（アクションクラスの特定） -->
<component class="nablarch.fw.handler.RequestPathJavaPackageMapping">
    <property name="basePackage" value="com.example.batch"/>
</component>
```

**入力データがDBの場合（安全なデータ源）**: フォームクラスは不要。`SqlRow`や入力エンティティクラスから直接集計ロジックに渡せる。

**注意点**:
- `トランザクションループ制御ハンドラ`の`commitInterval`で適切なコミット間隔を設定しないと、大量データ処理時にメモリ・ロック問題が発生しやすい
- 集計結果の書き込みが INSERT/UPDATE のどちらかによって、バッチ実行前のテーブルクリア処理（初期化）が必要になる場合がある
- 定期起動（ジョブスケジューラ等）との連携はNablarch外の仕組み（cron, Jenkins等）で行う

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s4, nablarch-batch-application-design.json:s1, nablarch-batch-feature-details.json:s4