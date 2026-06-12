セクション内容を確認しました。回答を生成します。

---

**結論**: Nablarchバッチの **DB to DB パターン** で実装する。`DatabaseRecordReader` でDBからレコードを1件ずつ読み込み、`BatchAction#handle` メソッドで集計処理を行い、結果を `UniversalDao.batchInsert` で別テーブルに書き込む構成が基本形。

---

**根拠**:

### 1. ハンドラ構成（都度起動バッチ、DB接続有り）

定期的に起動する「都度起動バッチ」かつDB接続ありの最小ハンドラ構成：

| No. | ハンドラ | 役割 |
|-----|---------|------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | 終了コード変換 |
| 2 | グローバルエラーハンドラ | 例外ログ出力 |
| 3 | データベース接続管理ハンドラ（初期処理/終了処理用） | DB接続取得・解放 |
| 4 | トランザクション制御ハンドラ（初期処理/終了処理用） | 初期化トランザクション |
| 5 | リクエストディスパッチハンドラ | アクションクラスを特定 |
| 6 | マルチスレッド実行制御ハンドラ | サブスレッド制御 |
| 7 | データベース接続管理ハンドラ（業務処理用） | 業務DB接続 |
| 8 | **トランザクションループ制御ハンドラ** | **コミット間隔でループ制御** |
| 9 | データリードハンドラ | 1件ずつレコード読み込み |

コミット間隔はコンポーネント定義ファイルで設定する：

```xml
<component class="nablarch.fw.handler.LoopHandler">
  <!-- コミット間隔に1000を指定 -->
  <property name="commitInterval" value="1000" />
</component>
```

### 2. DB to DB パターンの処理フロー

- 入力はSELECT文の結果セットの各レコード
- `createReader` で `DatabaseRecordReader` を生成してDBから読み込む
- `handle` メソッドで1レコード分のデータを受け取り、別テーブルへ書き込む
- 1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しない

### 3. アクションクラスの実装イメージ

```java
public class AggregationBatchAction extends BatchAction<SomeEntity> {

    @Override
    public DataReader<SomeEntity> createReader(ExecutionContext context) {
        // 集計に必要なデータを1クエリで取得（JOINで必要なデータをまとめる）
        return new DatabaseRecordReader()...;
    }

    @Override
    public Result handle(SomeEntity inputData, ExecutionContext context) {
        // 集計・変換処理
        ResultEntity result = aggregate(inputData);
        // 別テーブルへ書き込み
        UniversalDao.insert(result);
        return new Result.Success();
    }
}
```

大量データの場合は `UniversalDao.defer()` で遅延ロードを使用する：

```java
try (DeferredEntityList<SomeEntity> records
        = (DeferredEntityList<SomeEntity>) UniversalDao.defer()
                                            .findAllBySqlFile(SomeEntity.class, "AGGREGATE_SQL")) {
    for (SomeEntity record : records) {
        // 処理
    }
}
```

複数件まとめて書き込む場合は `batchInsert` でラウンドトリップを削減できる：

```java
UniversalDao.batchInsert(resultList);
```

---

**注意点**:

- **N+1問題を避ける**: `handle` メソッド内で再度SELECTを発行してはいけない。集計に必要なデータは `createReader` のSQLでJOINして1クエリにまとめる。件数が増えるほど深刻な性能劣化を引き起こす
- **自前ループを作らない**: `handle` 内でSELECT+自前forループを書くと、フレームワークのコミット制御が効かずトランザクションログを逼迫する。複数件処理が必要な場合は `createReader` のSQLで対応する
- **遅延ロード使用時の注意**: `UniversalDao.defer()` 使用中にRDBMSによってはトランザクション制御でカーソルがクローズされる場合がある。データベースベンダーのマニュアルでカーソル挙動を確認すること
- **batchUpdateの排他制御なし**: `batchUpdate` では排他制御が行われないため、排他制御が必要な場合は1レコードずつの更新処理を使用すること

参照: `nablarch-batch-architecture.json:s3`, `nablarch-batch-architecture.json:s5`, `nablarch-batch-architecture.json:s7`, `nablarch-batch-architecture.json:s8`, `nablarch-patterns-Nablarchバッチ処理パターン.json:s4`, `nablarch-patterns-Nablarchアンチパターン.json:s4`, `nablarch-patterns-Nablarchアンチパターン.json:s9`, `nablarch-patterns-Nablarchアンチパターン.json:s11`, `libraries-universal-dao.json:s9`, `libraries-universal-dao.json:s14`, `handlers-loop-handler.json:s5`

---