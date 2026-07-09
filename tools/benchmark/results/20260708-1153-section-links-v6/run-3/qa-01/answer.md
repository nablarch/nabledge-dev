**結論**: NablarchバッチでDBから大量データを1件ずつ読み込むには、`UniversalDao.defer()` による遅延ロード、または標準の `DatabaseRecordReader` を使う2つの方法があります。

**根拠**:

**方法1: ユニバーサルDAOの遅延ロード（推奨）**

`UniversalDao.defer()` を先に呼び出すだけで遅延ロードが有効になります。内部でサーバサイドカーソルを使用するため、必ず `DeferredEntityList#close` を呼び出す必要があります。

```java
// try-with-resourcesでcloseを保証する
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // userを使った処理
    }
}
```

メモリ使用量はJDBCのフェッチサイズによって変わります（詳細はDBベンダーマニュアルを参照）。

**方法2: DatabaseRecordReader（Nablarchバッチの標準データリーダ）**

Nablarchバッチでは `DatabaseRecordReader` が標準のデータリーダとして提供されており、DBからレコードを1件ずつ読み込んでハンドラキューに渡します。ハンドラ構成で `DataReadHandler` と組み合わせて使用します。

**注意点**:
- 遅延ロード（`defer()`）使用中にトランザクションをコミットすると、カーソルがクローズされてエラーになるDBMSがあります。バッチで中間コミットを行う場合は特に注意が必要です。
- `DeferredEntityList` の `close` を忘れると、サーバサイドカーソルが解放されずリソースリークになります。

参照:
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  検索結果を遅延ロードする
- 機能詳細
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-feature-details.md
  データベースアクセス
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md
  Nablarchバッチアプリケーションで使用するデータリーダ