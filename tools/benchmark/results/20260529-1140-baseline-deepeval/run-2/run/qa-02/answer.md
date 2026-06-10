**結論**: DB to DBパターンの都度起動バッチとして実装します。`DatabaseRecordReader` で入力テーブルを1件ずつ読み込み、`BatchAction#handle` で集計・変換し、`UniversalDao` で結果テーブルに書き込む構成です。

**根拠**:

**全体構成（ハンドラ設定）**

都度起動バッチ（DB接続あり）の最小ハンドラ構成を使用します：

```
[メインスレッド]
1. ステータスコード→プロセス終了コード変換ハンドラ
2. グローバルエラーハンドラ
3. データベース接続管理ハンドラ（初期処理/終了処理用）
4. トランザクション制御ハンドラ（初期処理/終了処理用）
5. リクエストディスパッチハンドラ
6. マルチスレッド実行制御ハンドラ

[サブスレッド]
7. データベース接続管理ハンドラ（業務処理用）
8. トランザクションループ制御ハンドラ  ← コミット間隔をcommitIntervalで設定
9. データリードハンドラ
   → アクションクラス（BatchAction）
```

コミット間隔の設定例：
```xml
<component class="nablarch.fw.handler.LoopHandler">
  <property name="commitInterval" value="1000" />
</component>
```

**データリーダ（DB読み込み）**

`DatabaseRecordReader` を使用し、入力テーブルからレコードを1件ずつ提供します。`createReader` メソッドでリーダを生成します。

**アクションクラス（業務ロジック）**

`BatchAction<T>` を継承し、`handle` メソッドで集計ロジックを実装します：

```java
public class AggregationAction extends BatchAction<InputData> {

    @Override
    public Result handle(InputData inputData, ExecutionContext ctx) {
        // 集計・変換処理
        ResultData result = aggregate(inputData);
        // 結果テーブルへ書き込み
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<InputData> createReader(ExecutionContext ctx) {
        // DatabaseRecordReaderを返す
        return new DatabaseRecordReader(...);
    }
}
```

大量データをまとめて書き込む場合は `UniversalDao.batchInsert` でパフォーマンスを向上できます。

**注意点**:

- **N+1問題を避ける**: `handle` メソッド内で追加SELECTを発行すると、処理件数分だけSQLが増加して深刻な性能劣化が起きます。必要なデータは `createReader` のSQLでJOINして一度に取得してください。
- **自前ループ禁止**: `handle` 内で自前のループ処理を書くと、フレームワーク管理のコミット間隔が効かなくなり、トランザクションログを逼迫します。ループはフレームワーク（トランザクションループ制御ハンドラ）に委ねてください。
- 大量データを遅延ロードする場合は `UniversalDao.defer()` を使用し、`DeferredEntityList#close` を必ず呼び出してください（try-with-resources推奨）。

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-patterns-Nablarchアンチパターン.json:s4, nablarch-patterns-Nablarchアンチパターン.json:s9, handlers-loop-handler.json:s5, libraries-universal-dao.json:s9, libraries-universal-dao.json:s14

---