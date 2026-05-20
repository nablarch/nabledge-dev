**結論**: Nablarchバッチで大量データを1件ずつ読み込むには、ユニバーサルDAOの遅延ロード（`UniversalDao.defer()`）を使用します。

**根拠**:

遅延ロードを使用すると、JDBCのサーバサイドカーソルを利用して1件ずつデータを読み込むため、全件をメモリに展開せずに処理できます。

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

使用方法は、通常の検索の前に `UniversalDao.defer()` を呼び出すだけです。内部ではサーバサイドカーソルを使用するため、処理後は `DeferredEntityList#close` を必ず呼び出す必要があります（try-with-resources で自動クローズ可能）。

**注意点**:
- メモリ使用量はJDBCのフェッチサイズによって変わります。フェッチサイズの詳細はデータベースベンダーのマニュアルを参照してください。
- 使用するRDBMSによっては、**カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされます**。遅延ロード中にトランザクション制御を行うとクローズ済みカーソルを参照してエラーになる可能性があるため注意が必要です。

参照: component/libraries/libraries-universal-dao.json:s9