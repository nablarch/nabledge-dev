Step 5で回答を生成します。

**結論**: NablarchバッチアプリケーションはJavaのメインクラス `nablarch.fw.launcher.Main` を `java` コマンドで直接起動します。起動時に必須の `-diConfig`・`-requestPath`・`-userId` の3つのオプションを指定します。`-requestPath` には `アクションのクラス名/リクエストID` の書式で記述します。

**根拠**:

起動コマンドの基本形は以下のとおりです。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**必須オプション**（いずれか欠けると終了コード127で即異常終了）:

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパス（例: `file:./batch-config.xml`） |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納される） |

**`-requestPath` の書式**:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子であり、同一の業務アクションクラスを複数プロセス起動する場合などにプロセスを区別するために使われます。

**注意点**: 3つの必須オプションのうち1つでも欠けていると終了コード127で即座に異常終了します。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3

---