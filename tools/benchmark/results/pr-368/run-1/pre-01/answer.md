**結論**: NablarchバッチアプリケーションはJavaコマンドで`nablarch.fw.launcher.Main`クラスを指定して起動します。`-requestPath`には「実行するアクションのクラス名/リクエストID」の書式で指定します。

**根拠**: 起動に必要な3つのオプションは必須です。いずれかが欠けると即座に異常終了します（終了コード = 127）。

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパスを指定する |
| `-requestPath` | 実行するアクションとリクエストIDを指定する |
| `-userId` | ユーザIDを指定する（`user.id`としてセッションコンテキスト変数に格納される） |

`-requestPath`の書式:

```bash
実行するアクションのクラス名/リクエストID
```

起動コマンドの例:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

アーキテクチャドキュメントでは以下の書式例も示されています:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

**注意点**:
- リクエストIDは各バッチプロセスの識別子として使われます。同一の業務アクションクラスを複数プロセスで起動する場合、このリクエストIDで識別します。
- 任意のオプションを追加で渡すこともでき、アクション内で`ExecutionContext#getSessionScopedVar("オプション名称")`で取得できます。

参照: handlers-main.json:s3, handlers-main.json:s4, nablarch-batch-architecture.json:s2