**結論**: NablarchバッチアプリケーションはJavaの`main`クラス（`nablarch.fw.launcher.Main`）を`java`コマンドで直接起動します。起動時に必須の引数として `-diConfig`、`-requestPath`、`-userId` の3つを指定する必要があります。

**根拠**: 

起動コマンドの基本形は以下のとおりです:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

各オプションの意味は次のとおりです:

| オプション | 必須 | 説明 |
|---|---|---|
| `-diConfig` | 必須 | システムリポジトリの設定ファイルのパス |
| `-requestPath` | 必須 | 実行するアクションのクラス名とリクエストID |
| `-userId` | 必須 | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

**`-requestPath` の書式**:

```bash
-requestPath=アクションのクラス名/リクエストID
```

具体例:

```bash
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

- アクションのクラス名は完全修飾クラス名（FQCN）で指定します
- リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを複数プロセスで起動する場合に区別するために使われます

**注意点**: 3つの必須オプション（`-diConfig`、`-requestPath`、`-userId`）のうちいずれかが欠けていた場合、アプリケーションは即座に異常終了します（終了コード = 127）。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3