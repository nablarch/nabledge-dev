**結論**: ユニバーサルDAOの遅延ロード機能（`UniversalDao.defer()`）を使用することで、大量データを1件ずつ読み込めます。

**根拠**:

遅延ロードは `UniversalDao.defer()` メソッドを先に呼び出すだけで使用できます。内部でサーバサイドカーソルを使用するため、処理後に `DeferredEntityList#close` を呼び出す必要があります。

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
- 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされます。遅延ロードを使用した大量データの処理中にトランザクション制御を行った場合、クローズ済みのカーソルを参照しエラーとなる可能性があります。データベースベンダ提供のマニュアルに沿ってカーソルの挙動を調整するか、大量データを扱わないようページングなどで回避してください。
- JDBCのフェッチサイズによってメモリの使用量が変わります。フェッチサイズの詳細はデータベースベンダー提供のマニュアルを参照してください。

参照:
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  検索結果を遅延ロードする