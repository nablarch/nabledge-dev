**結論**: Nablarchバッチで大量データを1件ずつ読み込むには、`UniversalDao.defer()` による遅延ロードを使用する。これにより、全件をメモリに展開せずにサーバサイドカーソルで1件ずつ処理できる。

**根拠**:

遅延ロードは `UniversalDao.defer()` を検索前に呼び出すだけで使用できる。内部でサーバサイドカーソルを使用するため、`DeferredEntityList#close` の呼び出しが必要。`try-with-resources` を使うのが推奨パターン。

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

なお、Nablarchバッチの標準データリーダとして `DatabaseRecordReader` も提供されており、こちらも「データベースの参照結果を1レコードづつ読み込む」用途に使える。`BatchAction` と組み合わせてフレームワークのデータリーダ機構として使用する場合はこちらを利用する。

**注意点**:
- 遅延ロードはJDBCのフェッチサイズによってメモリ使用量が変わる。フェッチサイズはDBベンダー提供のマニュアルを参照。
- 使用するRDBMSによっては、**カーソルオープン中にトランザクション制御（コミット等）を行うとカーソルがクローズされる**可能性がある。大量データ処理中にトランザクション制御が必要な場合は、DBベンダーのマニュアルでカーソルの挙動を確認するか、ページングで回避すること。

参照: libraries-universal-dao.json:s9, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s7, javadoc/javadoc-nablarch-fw-reader-DatabaseRecordReader.json