**結論**: 大量データを1件ずつ読み込むには、UniversalDAOの**遅延ロード**（`UniversalDao.defer()`）を使用します。

**根拠**:

UniversalDAOの遅延ロードを使うと、内部でサーバサイドカーソルを使用して1件ずつロードします。JDBCのフェッチサイズによってメモリ使用量は変わりますが、全件をメモリに展開せずに処理できます。

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

- 検索時に `UniversalDao.defer()` を先に呼び出すだけで使用可能
- `DeferredEntityList` は `Closeable` を実装しているため、try-with-resources でクローズが必要

**注意点**:

- 内部でサーバサイドカーソルを使用しているため、`DeferredEntityList#close` を必ず呼び出すこと（try-with-resources推奨）
- 使用するRDBMSによっては、**カーソルオープン中にトランザクション制御（コミット・ロールバック）を行うとカーソルがクローズされる**。遅延ロードによる処理中にトランザクション制御を行うとエラーになる可能性があるため注意
- 回避策として、データベースベンダーのマニュアルに沿ってカーソル挙動を調整するか、ページングで大量データを扱わないようにする

**補足（BLOB/CLOBカラムの場合）**: バイナリ型（BLOB）や大きい文字列型（CLOB）のカラムを扱う場合は、`Blob#getBinaryStream()` / `Clob#getCharacterStream()` を使い、`InputStream` / `Reader` 経由でストリーミング読み込みすることでヒープ圧迫を回避できます。

参照: `component/libraries/libraries-universal-dao.json#s9`, `component/libraries/libraries-database.json#s24`, `component/libraries/libraries-database.json#s25`