**結論**: Nablarchバッチで大量データをメモリに展開せず1件ずつ読み込むには、**ユニバーサルDAOの遅延ロード**（`UniversalDao#defer`）を使用する。また、Nablarchバッチのアーキテクチャ自体が `DataReader` によるレコード1件ずつの処理を標準的に提供しており、`DatabaseRecordReader` がその標準実装となる。

---

**根拠**:

**方法1: ユニバーサルDAOの遅延ロード（推奨）**

`UniversalDao#defer` メソッドを先に呼び出すことで遅延ロードが有効になる。内部でサーバサイドカーソルを使用するため、ユニバーサルDAOとしては1件ずつロードする。`DeferredEntityList#close` を必ず呼び出す必要があるため、try-with-resourcesを使用する。

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

**方法2: Nablarchバッチの標準アーキテクチャを活用する**

Nablarchバッチは、`DataReader` がデータレコードを1件ずつ提供し、`BatchAction#handle` がその1件を処理する構造になっている。DBからの入力には標準提供の `DatabaseRecordReader` を使用する。

処理の流れ：
1. `DataReader` が入力データを読み込み、データレコードを1件ずつ提供する
2. アクションクラスがデータレコード1件ごとの業務ロジックを実行する
3. 処理対象データがなくなるまで繰り返す

この構造を正しく使えば、大量データでもメモリに全件展開せずに処理できる。

---

**注意点**:

- **遅延ロードのトランザクション制約**: 使用するRDBMSによっては、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされ、エラーとなる可能性がある。データベースベンダのマニュアルに沿ってカーソルの挙動を確認すること。回避策としてページング処理の使用も検討できる。
- **アンチパターンに注意**: `handle` メソッド内で自前のSELECT+ループ処理を実装するのはアンチパターン。フレームワーク管理のループが機能せず、大量更新時にトランザクションログを逼迫する原因となる。検索はcreateReaderで行い、handleには1件分の処理のみを実装すること。
- **JDBCフェッチサイズ**: 遅延ロード使用時も、実際のメモリ使用量はJDBCのフェッチサイズによって変わる。詳細はデータベースベンダーのマニュアルを参照。

参照: `libraries-universal-dao.json:s9`, `nablarch-batch-architecture.json:s3`, `nablarch-batch-architecture.json:s7`, `nablarch-batch-feature-details.json:s4`, `nablarch-patterns-Nablarchアンチパターン.json:s9`, `nablarch-patterns-Nablarchアンチパターン.json:s11`

---