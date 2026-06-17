**結論**: `UniversalDao.defer().findAllBySqlFile(...)` を使って検索結果を `DeferredEntityList` として受け取ることで、サーバサイドカーソルによる1件ずつの遅延ロードが実現できます。

**根拠**:

遅延ロードは、検索時に `UniversalDao#defer` メソッドを先に呼び出すだけで使用できます。

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

遅延ロードを使用すると、ユニバーサルDAOとしては1件ずつロードします。内部でサーバサイドカーソルを使用しているため、`DeferredEntityList#close` メソッドを呼び出してリソースを解放する必要があります（try-with-resources を使うことで確実に解放できます）。

なお、メモリ使用量はJDBCのフェッチサイズによっても変わります。詳細はデータベースベンダー提供のマニュアルを参照してください。

**注意点**:
- 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされます。大量データの処理中にトランザクション制御（コミット等）を行った場合、クローズ済みのカーソルを参照してエラーになる可能性があります。データベースベンダーのマニュアルに従ってカーソルの挙動を調整するか、ページングで回避してください。

参照: libraries-universal-dao.json:s9, javadoc/javadoc-nablarch-common-dao-UniversalDao.json:s27