**結論**: `UniversalDao.defer()` メソッドを使用して遅延ロードを有効にする。これにより内部でサーバサイドカーソルが使われ、1件ずつ読み込むことができる。

**根拠**:

`UniversalDao.defer()` を検索の直前に呼び出すことで遅延ロードが有効になる。`DeferredEntityList` はサーバサイドカーソルを使用するため、全件をメモリに展開せずにループ処理できる。

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
- `DeferredEntityList#close()` を必ず呼び出すこと。呼び出さないとサーバサイドカーソルのリソースがリークする（try-with-resources を使うこと）
- カーソルオープン中にトランザクション制御が行われると、使用するRDBMSによってはカーソルがクローズされる場合がある。遅延ロードを使用した大量データ処理中にトランザクション制御を行うと、クローズ済みのカーソルを参照しエラーとなる可能性があるため注意すること

参照: libraries-universal-dao.json:s9