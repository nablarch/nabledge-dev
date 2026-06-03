**結論**: NablarchバッチはJavaコマンドで `nablarch.fw.launcher.Main` クラスを直接起動する。`-requestPath` は `アクションのクラス名/リクエストID` の書式で指定する。

**根拠**: 起動に必要なオプションは以下の3つ（いずれか欠けると終了コード127で即座に異常終了）:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

各オプションの説明:

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパス（XMLファイル） |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

`-requestPath` の書式:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使われる。同一のアクションクラスを複数プロセスで起動する場合に識別子として機能する。

**注意点**: 3つの必須オプション（`-diConfig`、`-requestPath`、`-userId`）のいずれかが欠けた場合、終了コード127で即座に異常終了する。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3

---