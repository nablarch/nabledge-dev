Step 5-7: セクション内容を元に回答を生成し、検証します。

---

**結論**: `handle` メソッド内で全件 SELECT してループするのではなく、`createReader` で `DatabaseRecordReader` を返してフレームワークのループ制御に乗せることで、DBから1件ずつ読み込める。`UniversalDao.defer()` による遅延ロードも代替手段として使用できる。

**根拠**:

Nablarchバッチのアーキテクチャでは、DataReaderがデータレコードを **1件ずつ** 提供し、フレームワークがループを制御する設計になっている。

### よくあるアンチパターン（メモリ不足の原因）

```java
// NG: handle内で全件SELECTしてループ → 全件メモリ展開されトランザクションログも逼迫する
public Result handle(ExecutionContext context) {
    SqlResultSet sqlResultSet = search("SEARCH");  // 全件取得
    for (SqlRow row : sqlResultSet) {
        // 更新処理
    }
}
```

`NoInputDataBatchAction` を使ってこのようなループを書くのは典型的な誤り。

### 解決法1: createReader で DatabaseRecordReader を使う（推奨）

`handle` 内のSQLを `createReader` に移し、フレームワーク管理のループ処理で実現する。

```java
// アクションクラスでcreateReaderをオーバーライド
@Override
public DataReader<SqlRow> createReader(ExecutionContext context) {
    return new DatabaseRecordReader()
        .setStatement(/* SQLIDや条件を設定 */);
}

// handle は1件ずつ受け取って処理するだけ
@Override
public Result handle(SqlRow inputData, ExecutionContext context) {
    // 1レコード分の業務処理
    return new Result.Success();
}
```

フレームワーク（`DataReadHandler` + `TransactionLoopHandler`）が1件ずつ読み込み、一定間隔でコミットを行うため、メモリもトランザクションログも逼迫しない。

### 解決法2: UniversalDao.defer() による遅延ロード

バッチフレームワークのループを使わずに大量データを処理する場合は、`UniversalDao#defer` メソッドで遅延ロードできる。

```java
// try-with-resourcesでDeferredEntityListをclose
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

内部でサーバサイドカーソルを使用するため、`DeferredEntityList#close` の呼び出しが必要（try-with-resources 推奨）。

**注意点**:
- `UniversalDao.defer()` 使用中、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされてエラーになる場合がある。DBベンダーのマニュアルでカーソルの挙動を確認すること。
- `DatabaseRecordReader` を使う解決法1の方がフレームワークのトランザクション制御と整合するため、Nablarchバッチでは解決法1が基本パターン（DB to DBパターン）。

参照: `nablarch-batch-architecture.json:s3`, `nablarch-batch-architecture.json:s5`, `nablarch-batch-architecture.json:s7`, `libraries-universal-dao.json:s9`, `nablarch-patterns-Nablarchアンチパターン.json:s9`, `nablarch-patterns-Nablarchアンチパターン.json:s10`, `nablarch-patterns-Nablarchアンチパターン.json:s11`, `nablarch-patterns-Nablarchバッチ処理パターン.json:s4`

---