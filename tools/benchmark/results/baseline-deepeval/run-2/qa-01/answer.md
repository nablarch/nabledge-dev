回答を生成します。

---

**結論**: Nablarchバッチで大量データを1件ずつ読み込む方法は2つあります。標準的な方法は `createReader` で `DatabaseRecordReader` を返すことで、フレームワークが自動的に1件ずつ読み込み・コミット制御を行います。データリーダの外で遅延ロードが必要な場合は `UniversalDao.defer()` を使用します。

---

**根拠**:

### 方法1: DatabaseRecordReader（推奨）

Nablarchバッチのフレームワークは `DataReader` → `DataReadHandler` → アクションという流れで1件ずつデータを提供します。`createReader` でデータリーダを返すと、`トランザクションループ制御ハンドラ` が一定間隔でコミットしながら全件処理します。

```java
@Override
public DataReader<SqlRow> createReader(ExecutionContext context) {
    DatabaseRecordReader reader = new DatabaseRecordReader();
    ParameterizedSqlPStatement statement = 
        DbConnectionContext.getConnection()
            .prepareParameterizedSqlStatementBySqlId("SELECT_LARGE_DATA");
    reader.setStatement(statement);
    return reader;
}

@Override
public Result handle(SqlRow inputData, ExecutionContext context) {
    // inputDataが1件ずつ渡される
    // ...
    return new Result.Success();
}
```

> **注意**: `handle` メソッド内で `SELECT` を発行して自前でループするアンチパターンは避けること。フレームワーク管理外のループではコミットが行われないため、件数増加でトランザクションログを逼迫します。

### 方法2: UniversalDao の遅延ロード

`handle` 内で大量データを扱う必要がある場合は `UniversalDao.defer()` を使用します。

```java
// try-with-resourcesを使ったclose呼び出し。
// DeferredEntityListはダウンキャストして取得する。
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

---

**注意点**:

- **方法1が基本**: Nablarchバッチは `createReader` でデータを渡し、フレームワークループで処理するのが正しい設計です
- **方法2の注意**: `DeferredEntityList#close()` の呼び出しが必須です（try-with-resources を使うこと）
- **方法2のトランザクション制約**: 使用するRDBMSによっては、カーソルオープン中にトランザクション制御を行うとカーソルがクローズされてエラーになる場合があります。データベースベンダーのマニュアルを確認してください
- **ユニバーサルDAOの設定**: 方法2を使用するには `BasicDaoContextFactory` のコンポーネント定義が必要です

```xml
<component name="daoContextFactory" class="nablarch.common.dao.BasicDaoContextFactory" />
```

参照: `component/libraries/libraries-universal-dao.json:s9`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s3`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s7`, `guide/nablarch-patterns/nablarch-patterns-Nablarchアンチパターン.json:s9`, `guide/nablarch-patterns/nablarch-patterns-Nablarchアンチパターン.json:s11`, `component/libraries/libraries-universal-dao.json:s6`

---