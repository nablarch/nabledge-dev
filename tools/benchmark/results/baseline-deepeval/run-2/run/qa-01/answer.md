**結論**: Nablarchバッチで大量データを1件ずつ読み込むには、ユニバーサルDAOの**遅延ロード**（`UniversalDao.defer()`）を使用します。

**根拠**:

ユニバーサルDAOの遅延ロードは、検索時に `UniversalDao#defer` メソッドを先に呼び出すだけで使用できます。遅延ロードを使用すると、ユニバーサルDAOとしては1件ずつロードします（メモリ使用量はJDBCのフェッチサイズによって変わります）。

内部でサーバサイドカーソルを使用しているため、`DeferredEntityList#close` の呼び出しが必要です。try-with-resources で確実にクローズしてください。

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

- **トランザクション制御との競合**: 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされます。これにより、遅延ロードを使用した大量データの処理中にトランザクション制御を行った場合、クローズ済みのカーソルを参照してエラーとなる可能性があります。データベースベンダ提供のマニュアルに沿ってカーソルの挙動を調整するか、ページングなどで回避してください。
- **アンチパターンの回避**: `handle` メソッド内で自前のSELECT＋ループを実装するのはアンチパターンです。自前ループではフレームワークのコミット間隔制御が働かず、トランザクションログを逼迫させる恐れがあります。入力データの取得は `createReader` で `DatabaseRecordReader` を使うか、遅延ロードを使用してください。

参照: `libraries-universal-dao.json:s9`, `nablarch-batch-architecture.json:s7`, `nablarch-patterns-Nablarchアンチパターン.json:s9`