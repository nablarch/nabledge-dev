**結論**: Nablarchバッチで大量データを1件ずつ読み込むには、`createReader` メソッドで `DatabaseRecordReader` を使う方法（フレームワーク管理のループ）が推奨です。フレームワーク外でDBアクセスが必要な場合は `UniversalDao.defer()` による遅延ロードを使います。

---

**根拠**:

#### 方法1（推奨）: createReader で DatabaseRecordReader を使う

`handle` メソッド内で自前の SELECT ループを回すのはアンチパターンです。フレームワークのループを使うには、SQLを `createReader` に移し、`DatabaseRecordReader` を返します。フレームワークが1件ずつ読み込んで `handle` を呼び出します。

```java
// アンチパターン（NG）
public Result handle(ExecutionContext context) {
    SqlResultSet sqlResultSet = search("SEARCH");
    for (SqlRow row : sqlResultSet) {
        // 更新処理
    }
}
```

上記は件数が増えるとトランザクションログを逼迫します。`createReader` に移すことで、フレームワークが一定間隔でコミットしながら1件ずつ処理します。

#### 方法2: UniversalDao.defer() による遅延ロード

`handle` 内で大量データを扱う必要がある場合は、`UniversalDao.defer()` で遅延ロードします。内部でサーバサイドカーソルを使用し、1件ずつロードします。

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

**注意点**:
- 方法2（遅延ロード）はサーバサイドカーソルを使用するため、`DeferredEntityList#close` の呼び出しが必須です（try-with-resources を使用すること）。
- 使用するRDBMSによっては、カーソルオープン中にトランザクション制御を行うとカーソルがクローズされ、エラーになる可能性があります。

参照: libraries-universal-dao.json:s9, nablarch-patterns-Nablarchアンチパターン.json:s9, nablarch-patterns-Nablarchアンチパターン.json:s10, nablarch-patterns-Nablarchアンチパターン.json:s11, nablarch-batch-architecture.json:s7

---