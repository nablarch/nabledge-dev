**結論**: `UniversalDao.defer()` メソッドを使った遅延ロードを使用することで、大量検索結果を全てメモリに展開せず1件ずつ処理できます。

**根拠**:

遅延ロードは `UniversalDao.defer()` を検索前に呼び出すだけで使用できます。内部ではサーバサイドカーソルを使用するため、**`DeferredEntityList#close` を必ず呼び出す**必要があります。`try-with-resources` を使うのが確実です。

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

なお、実際のメモリ使用量はJDBCのフェッチサイズによって変わります。詳細はデータベースベンダー提供のマニュアルを参照してください。

**注意点**:

- **カーソルとトランザクション制御の競合**: 使用するRDBMSによっては、カーソルオープン中にトランザクション制御（コミット等）が行われるとカーソルがクローズされ、エラーとなる可能性があります。データベースベンダーのマニュアルに沿って挙動を確認するか、ページングで回避することを検討してください。
- **アンチパターン回避**: `handle` メソッド内で自前の `SELECT` + ループを実装するのはアンチパターンです（トランザクションログの逼迫を招く）。大量データのループ処理は `createReader` でデータリーダに委ねるのが正しいアプローチです。

参照: libraries-universal-dao.json:s9, nablarch-batch-architecture.json:s7, nablarch-patterns-Nablarchアンチパターン.json:s9, nablarch-patterns-Nablarchアンチパターン.json:s11

---