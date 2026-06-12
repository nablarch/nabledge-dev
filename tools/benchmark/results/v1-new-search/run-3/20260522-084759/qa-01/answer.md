**結論**: Nablarchバッチで大量データを1件ずつ読み込むには、2つの観点がある。（1）DBから入力データを読む場合は標準提供の `DatabaseRecordReader` をデータリーダとして使用する。（2）`handle` メソッド内で大量データを検索する場合は `UniversalDao#defer` メソッドによる遅延ロードを使用する。

**根拠**:

#### (1) DatabaseRecordReader を使ったデータリーダパターン

Nablarchバッチは設計上、`DataReader` がデータレコードを **1件ずつ** 提供し、アクションクラスが1件ごとの業務ロジックを実行するアーキテクチャになっている。DBを入力とする場合は、標準提供の `DatabaseRecordReader` を使用することで、フレームワークが1件ずつの読み込みを管理する。

#### (2) UniversalDAO の遅延ロード（handle 内で大量データを検索する場合）

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

- 遅延ロードを使用すると、ユニバーサルDAOとしては1件ずつロードする。JDBCのフェッチサイズによってメモリの使用量が変わる（詳細はデータベースベンダー提供のマニュアルを参照）。
- 遅延ロードは内部でサーバサイドカーソルを使用しているので、`DeferredEntityList#close` メソッドを呼び出す必要がある（try-with-resources を使用すること）。

**注意点**:

1. **カーソルとトランザクション**: 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされる。遅延ロードを使用した大量データの処理中にトランザクション制御を行った場合、クローズ済みのカーソルを参照しエラーとなる可能性があるため注意すること。
2. **アンチパターン**: `handle` メソッド内で自前でSELECT文を発行してループ処理するのはアンチパターン。フレームワークのループはコミット間隔ごとにコミットされるが、自前ループではコミットが行われず、更新件数が増えるとトランザクションログを逼迫する。この場合は `handle` 内で発行しているSQLを `createReader` で行うようにすること。

参照: nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s3, libraries-universal-dao.json:s9, nablarch-patterns-Nablarchアンチパターン.json:s9, nablarch-patterns-Nablarchアンチパターン.json:s11

---