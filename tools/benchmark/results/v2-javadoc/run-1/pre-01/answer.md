**Step 3の選択結果を整理してStep 4に進みます。**

**Selected pages:**
- `processing-pattern/nablarch-batch/nablarch-batch-architecture.json` — `-requestPath`の書式を直接説明するs2を含む（Nablarchバッチ処理方式）
- `processing-pattern/nablarch-batch/nablarch-batch-feature-details.json` — 起動方法へのリンクを含むが実体は handlers-main に委譲
- `component/handlers/handlers-main.json` — 実際の起動コマンド例と必須オプションを含む（実装優先カテゴリ）
- `javadoc/javadoc-nablarch-fw-launcher-Main.json` — handlers-main.json:s3から参照されるJavadoc

**Excluded pages:** Nablarchバッチ以外の処理方式（web, REST, Jakarta Batch, messaging）はすべてスキップ。

**Selected sections:**
- `nablarch-batch-architecture.json:s2` (high) — `-requestPath`の書式とリクエストIDの役割を直接説明
- `nablarch-batch-architecture.json:s1` (high) — Mainクラスが起点であることを説明
- `handlers-main.json:s3` (high) — 具体的な起動コマンド例と3つの必須オプションを説明
- `javadoc-nablarch-fw-launcher-Main.json` content (partial) — Mainクラスの起動コマンド詳細例を補足

Step 4: read-sections.sh に渡すセクション:

```
processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s2
processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1
component/handlers/handlers-main.json:s3
```

(javadoc-nablarch-fw-launcher-Main.json は content 部分を読み取り済み)

Step 5〜7: 回答生成・検証を実施します。

---

**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスを javaコマンドで直接起動し、`-requestPath` に `アクションのクラス名/リクエストID` の形式で実行するアクションを指定します。

**根拠**:

起動コマンドの書式は以下のとおりです。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

必須オプションは3つあり、いずれかが欠けると即座に異常終了します（終了コード = 127）。

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイル（コンポーネント設定XMLファイル）のパスを指定 |
| `-requestPath` | 実行するアクションのクラス名とリクエストIDを指定（書式: `アクションのクラス名/リクエストID`） |
| `-userId` | プロセスの実行権限ユーザID（セッション変数に `user.id` として格納） |

`-requestPath` の書式詳細:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを複数プロセスで起動する場合に、このリクエストIDが識別子となります。

**注意点**:
- `-diConfig`・`-requestPath`・`-userId` の3つは全て必須です。1つでも欠けると終了コード127で異常終了します。
- 任意のオプションパラメータ（名前付きパラメータ）を追加することも可能で、アクション内から `ExecutionContext#getSessionScopedVar("オプション名")` で取得できます。

参照: `nablarch-batch-architecture.json:s2`, `handlers-main.json:s3`

---