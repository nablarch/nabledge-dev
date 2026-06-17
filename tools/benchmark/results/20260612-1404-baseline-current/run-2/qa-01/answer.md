**結論**: ユニバーサルDAOの遅延ロード（`UniversalDao.defer()`）を使用する。これにより内部でサーバサイドカーソルを使って1件ずつロードするため、全件をメモリに展開せずに処理できる。

**根拠**:

遅延ロードは、検索メソッドの前に `UniversalDao.defer()` を呼び出すだけで使用できる。

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

- `UniversalDao.defer()` を先に呼び出した後、通常の検索メソッド（`findAllBySqlFile` など）を呼ぶ
- 内部でサーバサイドカーソルを使用するため、JDBCのフェッチサイズに基づいてメモリ使用量が制御される
- 戻り値は `DeferredEntityList` にダウンキャストして受け取る
- `DeferredEntityList` は `Closeable` を実装しているため、try-with-resources で確実に `close()` を呼ぶ必要がある

**注意点**:

- 使用するRDBMSによっては、カーソルオープン中にトランザクション制御（コミット・ロールバック）が行われるとカーソルがクローズされる。これにより遅延ロード処理中にエラーとなる可能性があるため、カーソルの挙動をデータベースベンダーのマニュアルで確認すること。
- 回避策として、コミット間隔を調整するか、[ページング](component/libraries/libraries-universal-dao.json:s12)で大量データを分割して処理する方法もある。

参照: `component/libraries/libraries-universal-dao.json:s9`