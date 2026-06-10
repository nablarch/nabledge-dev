**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスを `java` コマンドで直接起動します。`-requestPath` は `実行するアクションのクラス名/リクエストID` の形式で指定します。

**根拠**:

起動コマンドの基本形式：

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

必須オプション（いずれかが欠けると即座に終了コード127で異常終了）：

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパス。このパスでシステムリポジトリを初期化する。 |
| `-requestPath` | 実行するアクションとリクエストIDを指定する。 |
| `-userId` | ユーザIDを設定する。セッションコンテキスト変数に `user.id` として格納される。 |

`-requestPath` の書式：

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを複数プロセスで起動する場合に、プロセスの区別に使用されます。

**注意点**: `-diConfig`・`-requestPath`・`-userId` の3オプションはすべて必須です。1つでも欠けると終了コード127で即時異常終了します。

参照: component/handlers/handlers-main.json:s3, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s2