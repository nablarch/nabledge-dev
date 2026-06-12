セクション内容を元に回答を生成します。

---

**結論**: `UniversalDao.defer()` を使って遅延ロードすることで、大量の検索結果をすべてメモリに展開せず1件ずつ処理できます。また、`handle` メソッド内で自前ループを組む実装はアンチパターンなので、`createReader` でデータリーダを提供してフレームワーク管理のループを使う必要があります。

---

**根拠**:

**① `UniversalDao.defer()` による遅延ロード**

`UniversalDao.defer()` を先に呼び出してから検索すると、内部でサーバサイドカーソルを使用し、結果を1件ずつロードします。戻り値は `DeferredEntityList` になります。

```java
// サーバサイドカーソルを利用するため、try-with-resources で必ず close する
try (DeferredEntityList<Project> searchList =
        (DeferredEntityList<Project>) UniversalDao
            .defer()
            .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition)) {
    for (Project project : searchList) {
        // projectを利用した処理
    }
}
```

**② `createReader` でフレームワーク管理のループを使う**

`handle` メソッド内で自前の SELECT + ループを組むのはアンチパターンです。フレームワーク管理のループではコミットが一定間隔で行われますが、自前ループではコミットされないため、更新件数が増えるとトランザクションログが逼迫します。

解決法は、`handle` 内で発行しているSQLを `createReader` で行い、フレームワーク管理のループに委ねることです。

```java
public class ImportZipCodeFileAction extends BatchAction<ZipCodeForm> {
    @Override
    public Result handle(ZipCodeForm inputData, ExecutionContext ctx) {
        // DataReaderから1件ずつ渡されたデータに対する処理のみを書く
        ZipCodeData data = BeanUtil.createAndCopy(ZipCodeData.class, inputData);
        UniversalDao.insert(data);
        return new Result.Success();
    }

    @Override
    public DataReader<ZipCodeForm> createReader(ExecutionContext ctx) {
        return new ZipCodeFileReader(); // データリーダを返す
    }
}
```

---

**注意点**:

- `DeferredEntityList` はサーバサイドカーソルを内部で使用するため、**`close()` の呼び出しが必須**です（`try-with-resources` を使用してください）
- RDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされ、エラーになる場合があります。大量データ処理中のトランザクション制御に注意してください

参照: `libraries-universal-dao.json:s9`, `javadoc-nablarch-common-dao-UniversalDao.json:s27`, `nablarch-patterns-Nablarchアンチパターン.json:s9`, `nablarch-patterns-Nablarchアンチパターン.json:s11`, `nablarch-batch-getting-started-nablarch-batch.json:s3`

---