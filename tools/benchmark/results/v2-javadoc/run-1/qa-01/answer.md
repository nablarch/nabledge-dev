十分なセクション情報が揃いました。回答を生成します。

---

**結論**: `UniversalDao.defer()` を使って遅延ロードを行うことで、大量データをメモリに全展開せずに処理できます。内部でサーバサイドカーソルを使用し、JDBCのフェッチサイズ単位でDBからデータを取得します。

**根拠**:

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

ポイントは2つです:
1. **`UniversalDao.defer()`** を検索前に呼び出す — これだけで遅延ロードが有効になります
2. **`DeferredEntityList#close()`** を必ず呼び出す — 内部でサーバサイドカーソルを使っているためリソース解放が必要です（`try-with-resources` を使うのが確実）

**注意点**:
- 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルが自動クローズされる場合があります。遅延ロード中にコミット/ロールバックが発生すると、クローズ済みカーソルへのアクセスエラーになる可能性があります。
- メモリ使用量はJDBCのフェッチサイズの設定によって変わります。詳細はDBベンダーのマニュアルを参照してください。

参照: libraries-universal-dao.json:s9, javadoc-nablarch-common-dao-UniversalDao.json:s27

---