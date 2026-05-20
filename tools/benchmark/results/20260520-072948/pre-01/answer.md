**結論**: Nablarchバッチアプリケーションは `java nablarch.fw.launcher.Main` コマンドで起動します。`-requestPath` は「アクションのクラス名/リクエストID」の形式で指定します。

**根拠**:

`-requestPath` の書式:
```
実行するアクションのクラス名/リクエストID
```

具体的な指定例:
```
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

起動時には以下の**3つのオプションが必須**です。いずれかが欠けていた場合は即座に異常終了します（終了コード = 127）。

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパス |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

実行コマンドの例:
```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

リクエストIDは各バッチプロセスの識別子として使われます。同一のアクションクラスを複数プロセスで起動する場合に、このIDで識別します。

**注意点**: `-diConfig`・`-requestPath`・`-userId` の3オプションはすべて必須です。1つでも欠けると終了コード 127 で即座に異常終了します。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3, nablarch-batch-architecture.json:s3