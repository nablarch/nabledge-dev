**結論**: ユニバーサルDAOの **遅延ロード（defer）** を使用すると、検索結果を1件ずつロードしてメモリ消費を抑えることができます。

**根拠**:

`UniversalDao#defer()` メソッドを検索前に呼び出すだけで遅延ロードが有効になります。内部ではサーバサイドカーソルを使用するため、`DeferredEntityList#close()` を必ず呼び出す必要があります（try-with-resources推奨）。

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

なお、BLOBやCLOBなどの大容量カラムを扱う場合も同様の問題が起きます。その際は `byte[]` や `String` で一括取得するのではなく、`Blob#getBinaryStream()` や `Clob#getCharacterStream()` を使って `InputStream` / `Reader` 経由で逐次読み込みする方法があります。

**注意点**:

- 遅延ロード使用時のメモリ使用量はJDBCの**フェッチサイズ**に依存します。詳細はデータベースベンダーのマニュアルを参照してください。
- 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われると**カーソルがクローズ**される場合があります。遅延ロードで大量データを処理中にトランザクション制御を行うと、クローズ済みカーソル参照でエラーになることがあります。
- カーソルの挙動はDBベンダーのマニュアルで調整するか、大量データを扱わないよう**ページング**などで回避することも検討してください。

参照: `component/libraries/libraries-universal-dao.json#s9`, `component/libraries/libraries-database.json#s24`, `component/libraries/libraries-database.json#s25`