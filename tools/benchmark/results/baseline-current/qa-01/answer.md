**結論**: UniversalDAOの遅延ロード（`UniversalDao.defer()`）を使用することで、大量データを1件ずつ読み込むことができます。また、Nablarchバッチのアーキテクチャ自体も、DataReaderがデータを1件ずつアクションクラスに渡す設計になっています。

**根拠**:

大量データをすべてメモリに展開する通常の検索ではなく、遅延ロードを使うことでメモリ使用量を抑えられます。内部でサーバサイドカーソルを使用し、JDBCのフェッチサイズに応じてメモリ使用量が制御されます。

```java
// try-with-resourcesを使ったclose呼び出し
// DeferredEntityListはダウンキャストして取得する
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理（1件ずつ）
    }
}
```

`defer()` を検索前に呼び出すだけで遅延ロードが有効になります。

なお、Nablarchバッチのアーキテクチャでは、`DatabaseRecordReader` がDBからデータを読み込み、DataReaderが1件ずつアクションクラスに渡す処理の流れになっています。バッチ処理の中でUniversalDAOの遅延ロードを使う場合も、この1件ずつの処理と組み合わせることができます。

**注意点**:
- `DeferredEntityList` は使用後に必ず `close()` する必要があります（`try-with-resources` を使用してください）
- RDBMSによっては、**カーソルオープン中にトランザクション制御を行うとカーソルがクローズされ、エラーになる**場合があります。大量データ処理中のトランザクション制御には注意してください
- フェッチサイズの調整はデータベースベンダーのマニュアルを参照してください

参照: `component/libraries/libraries-universal-dao.json#s9`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s7`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s3`