必要な情報が揃いました。Step 5: 回答生成に進みます。

`read_sections` = `["processing-pattern/nablarch-batch/nablarch-batch-feature-details.json:s1", "processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1", "processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s2", "component/handlers/handlers-main.json:s3", "component/handlers/handlers-main.json:s4"]`

回答を生成します。

---

**結論**: NablarchバッチはJavaコマンドで `nablarch.fw.launcher.Main` を起動し、必須オプションとして `-diConfig`（設定ファイルパス）、`-requestPath`（アクションクラス名/リクエストID）、`-userId`（ユーザID）の3つを指定します。

**根拠**:

`-requestPath` の書式は以下のとおりです：

```
アクションのクラス名/リクエストID
```

**起動コマンドの例**：

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

各オプションの説明：

| オプション | 用途 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパス |
| `-requestPath` | 実行するアクションのクラス名/リクエストID |
| `-userId` | ユーザID（`user.id` としてセッションに格納） |

`-requestPath` の具体的な書き方（`nablarch-batch-architecture.json:s2` より）：

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使われ、同一アクションクラスを複数プロセスで起動する場合の識別に利用されます。

**注意点**: 3つの必須オプション（`-diConfig`、`-requestPath`、`-userId`）のいずれかが欠けていた場合、アプリケーションは即座に異常終了します（終了コード = 127）。

参照: nablarch-batch-architecture.json:s1, nablarch-batch-architecture.json:s2, handlers-main.json:s3

---