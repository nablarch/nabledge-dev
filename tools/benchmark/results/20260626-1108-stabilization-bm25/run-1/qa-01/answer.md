**結論**: `UniversalDao.defer()` を先に呼び出して遅延ロードを使用することで、大量データを1件ずつ読み込めます。内部ではサーバサイドカーソルを使用しており、メモリに検索結果を全展開せずに処理できます。

**根拠**:

検索時に `UniversalDao.defer()` を先に呼び出すだけで遅延ロードが有効になります。

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

遅延ロードでは「ユニバーサルDAOとしては1件ずつロード」されますが、実際のメモリ使用量はJDBCのフェッチサイズに依存します。フェッチサイズの詳細はデータベースベンダー提供のマニュアルを参照してください。

**注意点**:

- **必ずcloseする**: 内部でサーバサイドカーソルを使用しているため、`DeferredEntityList#close` の呼び出しが必要です。try-with-resources を使って確実にクローズしてください。
- **トランザクション制御に注意**: 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされ、エラーになる可能性があります。回避策として、ページング（`UniversalDao.per().page()`）を使う方法もあります。

参照: `libraries-universal-dao.json:s9`