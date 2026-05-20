**結論**: NablarchバッチでDBから大量データを1件ずつ読み込むには、`UniversalDao.defer()` メソッドを使った遅延ロードを使用します。これにより全件をメモリに展開せず、サーバサイドカーソルで1件ずつ処理できます。

**根拠**:

遅延ロードは `UniversalDao#defer()` を先に呼び出すだけで使用できます。`DeferredEntityList` はサーバサイドカーソルを内部で使用するため、処理後は必ず `close()` を呼ぶ必要があります。

```java
// try-with-resourcesを使ったclose呼び出し。
// DeferredEntityListはダウンキャストして取得する。
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理（10万件でも1件ずつ処理）
    }
}
```

JDBCのフェッチサイズによってメモリ使用量が変わります。フェッチサイズはデータベースベンダー提供のマニュアルを参照してください。

**注意点**:
- 使用するRDBMSによっては、カーソルオープン中にトランザクション制御（コミット等）を行うとカーソルがクローズされ、エラーになる場合があります。データベースベンダーのマニュアルに沿ってカーソルの挙動を確認してください。
- `DeferredEntityList#close()` を呼ばないとリソースリークが発生します。`try-with-resources` を使うことで確実にクローズできます。

参照: `component/libraries/libraries-universal-dao.json:s9`