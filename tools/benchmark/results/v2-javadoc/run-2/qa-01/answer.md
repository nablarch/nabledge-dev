セクション情報が揃いました。回答を生成します。

---

**結論**: ユニバーサルDAOの `UniversalDao.defer()` メソッドを使用すれば、サーバサイドカーソルにより検索結果を1件ずつ読み込めます。全件をメモリに展開しないため、大量データ処理でもメモリ不足を回避できます。

**根拠**:

`UniversalDao.defer()` を検索の前に呼び出すだけで遅延ロードが有効になります。内部でサーバサイドカーソルを使用するため、`DeferredEntityList` を必ず `close()` する必要があります。try-with-resources を使うのが推奨です。

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

メモリ使用量はJDBCのフェッチサイズによって変わります。フェッチサイズの設定はデータベースベンダーのマニュアルを参照してください。

**注意点**:

- **トランザクション制御との干渉**: 使用するRDBMSによっては、カーソルオープン中にトランザクション制御（コミット等）が行われるとカーソルがクローズされます。これにより「クローズ済みのカーソルを参照した」エラーが発生する可能性があります。データベースベンダーのマニュアルでカーソルの挙動を確認してください。
- **アンチパターンに注意**: `handleメソッド`内で自前のSELECT＋ループをするのは誤った実装です。フレームワーク制御外のループではコミットが行われず、トランザクションログが逼迫します。データリーダ（`createReader`）でデータ取得し、フレームワークのループ制御に任せるのが正しい設計です。

参照: libraries-universal-dao.json:s9, javadoc-nablarch-common-dao-UniversalDao.json:s27

---