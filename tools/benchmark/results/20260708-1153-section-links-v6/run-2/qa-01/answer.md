**結論**: ユニバーサルDAOの遅延ロード（`UniversalDao.defer()`）を使用する。これにより、大量データをすべてメモリに展開せずにサーバサイドカーソルで1件ずつ処理できる。

**根拠**:

遅延ロードは `UniversalDao.defer()` メソッドを検索前に呼び出すだけで使用できる。内部でサーバサイドカーソルを使用しており、JDBCのフェッチサイズに応じてメモリ使用量が制御される。

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
- `DeferredEntityList#close` の呼び出しが必須。上記のように try-with-resources を使うこと。
- 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされ、エラーとなる可能性がある。大量データ処理中のトランザクション制御には注意すること。詳細はデータベースベンダー提供のマニュアルを参照。カーソルの挙動が問題になる場合は、ページング機能で回避する方法もある。

参照:
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  検索結果を遅延ロードする