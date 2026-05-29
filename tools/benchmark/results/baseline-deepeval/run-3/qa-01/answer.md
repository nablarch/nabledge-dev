Step 5-8: 回答を生成し、verify します。

**結論**: Nablarchバッチで大量データを1件ずつ読み込むには、**ユニバーサルDAOの遅延ロード**（`UniversalDao.defer()`）を使用するか、フレームワーク標準の**`DatabaseRecordReader`**をデータリーダとして使用する方法があります。

**根拠**:

**方法1: ユニバーサルDAOの遅延ロード（バッチのhandle内でDBアクセスする場合）**

`UniversalDao#defer` メソッドを先に呼び出すことで遅延ロードが有効になり、検索結果をすべてメモリに展開せず1件ずつ処理できます。内部でサーバサイドカーソルを使用するため、`DeferredEntityList#close` の呼び出しが必須です。

```java
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

メモリ使用量はJDBCのフェッチサイズにも依存します（詳細はDBベンダーのマニュアルを参照）。

**方法2: DatabaseRecordReader（Nablarchバッチの正規アーキテクチャ）**

Nablarchバッチの本来のアーキテクチャは、`createReader` メソッドで `DatabaseRecordReader` を返し、フレームワークが1件ずつ読み込んでデータリードハンドラ経由でハンドラメソッドに渡す設計です。この方式ではフレームワークがループとトランザクション制御を管理するため、大量データでもメモリを逼迫しません。

**注意点**:
- 遅延ロードをバッチで使用する場合、カーソルオープン中にトランザクション制御が行われるとカーソルがクローズされる可能性があります（RDBMS依存）。その場合はDBベンダーのマニュアルを参照してカーソルの挙動を調整するか、ページングで回避してください。
- `handle` メソッド内で自前の `SELECT + ループ` を実装するのはアンチパターンです。コミットが実行されないためトランザクションログを逼迫します。SQLは `createReader` で発行し、フレームワーク管理のループを使用してください。

参照: libraries-universal-dao.json:s9, nablarch-batch-architecture.json:s7, nablarch-patterns-Nablarchアンチパターン.json:s9, nablarch-patterns-Nablarchアンチパターン.json:s11

---