Step 5-7: 回答を生成し、検証します。

セクション内容から確認できた主要情報：
- `handlers-main.json:s3`：起動コマンドの完全な例、3つの必須オプション、欠落時の終了コード127
- `nablarch-batch-architecture.json:s2`：`-requestPath` の書式と指定例
- `nablarch-batch-architecture.json:s1`：Main クラスがスタンドアロン起動の起点
- `nablarch-batch-architecture.json:s3`：DispatchHandlerが `-requestPath` を使ってアクションを特定する処理フロー

**クレーム検証（Step 6）**：
- `nablarch.fw.launcher.Main` で起動 → `handlers-main.json:s3` に明示 ✅
- `-requestPath=アクションクラス名/リクエストID` の書式 → `nablarch-batch-architecture.json:s2`、`handlers-main.json:s3` に明示 ✅
- 3つの必須オプション（`-diConfig`、`-requestPath`、`-userId`） → `handlers-main.json:s3` に明示 ✅
- いずれか欠けると終了コード127で即異常終了 → `handlers-main.json:s3` に明示 ✅
- リクエストIDはバッチプロセスの識別子 → `nablarch-batch-architecture.json:s2` に明示 ✅

verify_result = PASS

---

**結論**: `java nablarch.fw.launcher.Main` コマンドで起動し、`-requestPath=アクションのクラス名/リクエストID` の書式で実行するアクションとリクエストIDを指定します。

**根拠**:

起動コマンドは以下の通りです。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

必須オプションは以下の3つで、すべて必ず指定する必要があります。

| オプション | 内容 |
|-----------|------|
| `-diConfig` | システムリポジトリの設定ファイルパス。このパスでシステムリポジトリを初期化する。 |
| `-requestPath` | 実行するアクションのクラス名とリクエストID。書式は `アクションのクラス名/リクエストID`。 |
| `-userId` | ユーザID。セッションコンテキスト変数 `user.id` に格納される。 |

`-requestPath` の書式は次のとおりです。

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使われます。同一の業務アクションクラスを複数プロセスで起動する場合に、このリクエストIDで区別します。

**注意点**:
- `-diConfig`、`-requestPath`、`-userId` のいずれかが欠けていた場合、終了コード `127` で即座に異常終了します。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3

---