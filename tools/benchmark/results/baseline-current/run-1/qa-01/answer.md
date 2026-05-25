**結論**: 大量データを1件ずつ読み込むには、UniversalDao の**遅延ロード**（`defer()`）を使用します。

**根拠**:

UniversalDAO の遅延ロードは、`UniversalDao#defer()` メソッドを検索前に呼び出すだけで使用できます。内部でサーバサイドカーソルを使用し、JDBCのフェッチサイズ単位でデータを取得するため、全件をメモリに展開せずに処理できます。

```java
// try-with-resources を使ったclose呼び出し。
// DeferredEntityList はダウンキャストして取得する。
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // user を使った処理
    }
}
```

- `UniversalDao.defer()` を先に呼び出してから検索メソッドを呼ぶ
- 結果は `DeferredEntityList<T>` にダウンキャストして取得する
- サーバサイドカーソルを使用するため、**`DeferredEntityList#close()`** の呼び出しが必要（try-with-resources で自動クローズ）
- メモリ使用量はJDBCのフェッチサイズによって変わる（詳細はDBベンダーのマニュアルを参照）

**注意点**:

- 使用するRDBMSによっては、**カーソルオープン中にトランザクション制御を行うとカーソルがクローズされる**場合がある。遅延ロードによる大量データ処理中にトランザクション制御（コミット・ロールバック等）を行うと、クローズ済みカーソルを参照してエラーになる可能性があるため注意が必要。
- トランザクション制御が必要な場合は、DBベンダーのマニュアルに従ってカーソルの挙動を調整するか、ページングで大量データを扱わないよう回避する。

参照: `component/libraries/libraries-universal-dao.json#s9`