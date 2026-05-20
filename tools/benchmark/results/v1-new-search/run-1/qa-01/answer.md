**結論**: Nablarchバッチで大量データを1件ずつ読み込むには、標準提供の `DatabaseRecordReader` をデータリーダとして使用するか、アクション内でユニバーサルDAOの `UniversalDao.defer()` を使って遅延ロードする。

**根拠**:

**① DatabaseRecordReader（推奨: バッチの標準構成）**

Nablarchバッチのアーキテクチャは、`DataReader` がDBからデータレコードを **1件ずつ** 業務アクションに提供する設計になっている。標準提供の `DatabaseRecordReader` を使うことで、全件をメモリに展開せずに処理できる。

```
処理の流れ:
1. DataReader (DatabaseRecordReader) が1件読み込む
2. アクションクラスが1件分の業務ロジックを実行
3. 処理対象データがなくなるまで繰り返す
```

**② UniversalDao.defer()（アクション内で遅延ロードが必要な場合）**

アクション内で大量の検索結果を扱う必要がある場合は `UniversalDao.defer()` を使用する。内部でサーバサイドカーソルを使用し、JDBCのフェッチサイズ単位でメモリ使用量を制御する。`DeferredEntityList#close` の呼び出しが必須。

```java
// try-with-resourcesを使ったclose呼び出し
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

**注意点**:
- `UniversalDao.defer()` 使用中は、カーソルオープン中にトランザクション制御を行うとカーソルがクローズされ、エラーになる場合がある（使用するRDBMSによる）。バッチ処理中にコミット間隔を設けている場合は特に注意。
- `DeferredEntityList#close` を呼び忘れるとリソースリークが発生する。

参照: `component/libraries/libraries-universal-dao.json:s9`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s3`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s7`