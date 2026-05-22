必要な情報がすべて揃いました。回答を生成します。

---

**結論**: NablarchバッチアプリケーションはMainクラスをjavaコマンドで直接起動します。`-requestPath` には `アクションのクラス名/リクエストID` の形式で実行するアクションとリクエストIDを指定します。

**根拠**:

起動コマンドの基本構造は以下の通りです。3つのオプション（`-diConfig`、`-requestPath`、`-userId`）はすべて必須で、いずれかが欠けると即座に異常終了（終了コード = 127）します。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**`-requestPath` の書き方**:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

各オプションの意味:

| オプション | 必須 | 説明 |
|---|---|---|
| `-diConfig` | 必須 | システムリポジトリの設定ファイルのパス（例: `file:./batch-config.xml`） |
| `-requestPath` | 必須 | 実行するアクションクラス名とリクエストIDを `/` で区切って指定 |
| `-userId` | 必須 | ユーザID（セッションコンテキスト変数の `user.id` に格納される） |

**注意点**:
- リクエストIDは各バッチプロセスの識別子として用いられます。同一のアクションクラスを複数プロセスで起動する場合、このリクエストIDで区別します。
- このオプションで指定されたリクエストパスは `Request#getRequestPath` が返すようになります。

参照: handlers-main.json:s3, nablarch-batch-architecture.json:s2

---