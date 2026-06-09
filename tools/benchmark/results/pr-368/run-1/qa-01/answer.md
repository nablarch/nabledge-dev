**結論**: Nablarchバッチで大量データをメモリに乗せず1件ずつ処理するには、`UniversalDao.defer()` による遅延ロードを使用する。内部でサーバサイドカーソルを使用するため、全件をヒープに展開せず処理できる。

**根拠**:

`UniversalDao.defer()` を検索前に呼び出すだけで遅延ロードが有効になる。`DeferredEntityList` は `Closeable` を実装しているため、`try-with-resources` でクローズする必要がある。

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

遅延ロードを使用すると、ユニバーサルDAOとしては1件ずつロードするが、JDBCのフェッチサイズによってメモリの使用量が変わる。フェッチサイズの詳細はデータベースベンダー提供のマニュアルを参照すること。

なお、`DataReader` を使った標準バッチ構成でデータベースから1レコードずつ読み込む場合は、`DatabaseRecordReader`（`DataReader<SqlRow>` 実装）も利用できる。`setStatement()` でSQLステートメントを設定し、フレームワークが `read()` を呼び出すたびにレコードを1行ずつ返却する。

**注意点**:
- 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされる場合がある。遅延ロードを使用した大量データの処理中にトランザクション制御を行った場合、クローズ済みのカーソルを参照しエラーになる可能性があるため注意すること。回避策として、データベースベンダーのマニュアルに沿ってカーソルの挙動を調整するか、ページングで分割処理することが考えられる。
- `DeferredEntityList#close()` を呼び出さないとリソースリークになる。必ず `try-with-resources` を使用すること。

参照: `component/libraries/libraries-universal-dao.json:s9`, `javadoc/javadoc-nablarch-fw-reader-DatabaseRecordReader.json`