**結論**: DB to DB パターンの都度起動バッチとして実装する。`DatabaseRecordReader`でDBからデータを読み込み、`BatchAction`を継承したアクションクラスの`handle()`メソッドで集計処理と別テーブルへの書き込みを行う。

---

**根拠**

**① 処理パターンの選択**

定期的にプロセスを起動する場合は「都度起動バッチ」を使用する（日次・月次など）。DB読み込み→DB書き込みは「DB to DB」パターンに該当し、SELECT結果セットの各レコードを1件ずつ受け取ってDBを更新する構成になる。

> 1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません

**② ハンドラ構成（都度起動バッチ・DB接続有り）**

```
No. | ハンドラ                                | スレッド
 1  | ステータスコード→プロセス終了コード変換ハンドラ | メイン
 2  | グローバルエラーハンドラ                   | メイン
 3  | データベース接続管理ハンドラ（初期処理用）     | メイン
 4  | トランザクション制御ハンドラ（初期処理用）     | メイン
 5  | リクエストディスパッチハンドラ               | メイン
 6  | マルチスレッド実行制御ハンドラ               | メイン
 7  | データベース接続管理ハンドラ（業務処理用）     | サブ
 8  | トランザクションループ制御ハンドラ            | サブ
 9  | データリードハンドラ                       | サブ
```

**③ 実装クラスの構成**

```java
public class AggregationBatchAction extends BatchAction<AggregationEntity> {

    // データリーダ生成: DatabaseRecordReader でSELECT結果をフィード
    @Override
    public DataReader<AggregationEntity> createReader(ExecutionContext ctx) {
        DatabaseRecordReader reader = new DatabaseRecordReader();
        // 集計に必要なデータをJOINして1回のSQLで取得する
        reader.setStatement(
            ParameterizedSqlPStatement.getSqlClause("AGGREGATE_SELECT"), ...);
        return reader;
    }

    // 1レコードの業務ロジック（集計 → 別テーブルへINSERT/UPDATE）
    @Override
    public Result handle(AggregationEntity inputData, ExecutionContext ctx) {
        ResultEntity result = buildResult(inputData);
        UniversalDao.insert(result);    // 結果テーブルへ書き込み
        return new Result.Success();
    }
}
```

**④ 大量データの場合**

`DatabaseRecordReader`はサーバサイドカーソルを使い1件ずつフィードするため、全件メモリに乗せる必要はない。`UniversalDao.defer()` も同様の遅延ロードを提供している（カーソルオープン中のトランザクション制御には注意）。

---

**注意点**

- **N+1問題を避ける**: `handle()`内で追加SELECTを発行してはいけない。必要なデータは`createReader()`のSQLにJOINして一括取得する。処理対象が10,000件の場合、N+1があると10,001件のSQLが発行される。
- **自前ループを作らない**: `handle()`内で`for`ループを書くと、フレームワークのトランザクション制御（コミット間隔）が効かず、トランザクションログを逼迫する。まとめてSELECTしてループする構造は典型的なアンチパターン。
- **主キー以外の条件で更新/削除する場合**: `UniversalDao`は主キー指定のCRUDのみ対応。集計結果を条件付きでUPDATEする場合はJDBCラッパー（データベースアクセスライブラリ）を使用する。
- **起動コマンド**: `-requestPath=com.example.AggregationBatchAction/BATCH0001` のように `-requestPath` でアクションとリクエストIDを指定する。

参照: nablarch-batch-architecture.json:s1, nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-patterns-Nablarchアンチパターン.json:s4, nablarch-patterns-Nablarchアンチパターン.json:s9, nablarch-patterns-Nablarchアンチパターン.json:s11, libraries-universal-dao.json:s9