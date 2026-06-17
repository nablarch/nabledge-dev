**結論**: Nablarchバッチで大量データを1件ずつ読み込むには、ユニバーサルDAOの **遅延ロード**（`UniversalDao.defer()`）を使用します。全件をメモリに展開せず、サーバサイドカーソルで逐次読み込みます。

**根拠**:

遅延ロードは `UniversalDao.defer()` を検索の前に呼び出すだけで使用できます。内部でサーバサイドカーソルを使用するため、`DeferredEntityList#close()` を必ず呼び出してリソースを解放する必要があります。

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

なお、JDBCのフェッチサイズによってメモリ使用量が変わります。フェッチサイズの詳細はデータベースベンダー提供のマニュアルを参照してください。

**注意点**:

使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされます。遅延ロード中にトランザクション制御（コミット等）を行うと、クローズ済みカーソルを参照してエラーになる可能性があります。この場合は、データベースベンダーのマニュアルに従いカーソルの挙動を調整するか、ページングで回避してください。

参照: component/libraries/libraries-universal-dao.json:s9