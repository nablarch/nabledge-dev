**結論**: `UniversalDao#defer()` を使った遅延ロードを利用することで、検索結果を1件ずつメモリに読み込むことができます。

**根拠**:

通常の検索では全件をメモリに展開しますが、`UniversalDao.defer()` を先に呼び出すことで遅延ロードが有効になります。内部ではサーバサイドカーソルを使用し、JDBCのフェッチサイズ単位でレコードを取得します。

```java
// DeferredEntityList を try-with-resources でクローズすること
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

- `DeferredEntityList` は `AutoCloseable` なので try-with-resources で必ずクローズしてください。
- JDBCのフェッチサイズによってメモリ使用量が変わります（詳細はDBベンダーのマニュアルを参照）。

**注意点**:
- カーソルオープン中にトランザクション制御（コミット・ロールバック）を行うと、RDBMSによってはカーソルがクローズされ、エラーになる場合があります。
- 遅延ロード中のトランザクション制御は避けるか、ページングで代替することを検討してください。

なお、大きいバイナリ（BLOB）や文字列（CLOB）カラムを扱う場合も同様のメモリ問題が起きます。その際は `Blob#getBinaryStream()` や `Clob#getCharacterStream()` を使って `InputStream`/`Reader` 経由でストリーム読み込みするのが適切です。

参照: `component/libraries/libraries-universal-dao.json#s9`、`component/libraries/libraries-database.json#s24`、`component/libraries/libraries-database.json#s25`