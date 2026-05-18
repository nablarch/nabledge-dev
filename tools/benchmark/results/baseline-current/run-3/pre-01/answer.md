**結論**: NablarchバッチアプリケーションはJavaコマンドで `nablarch.fw.launcher.Main` クラスを起動します。`-requestPath` には「アクションクラス名/リクエストID」の形式で指定します。

**根拠**:

### 起動コマンドの基本形

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

以下の3つのオプションは**必須**です。いずれかが欠けると即座に異常終了します（終了コード = 127）。

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパス |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納される） |

### -requestPath の書き方

```
-requestPath=アクションのクラス名/リクエストID
```

**例:**
```bash
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

- **アクションのクラス名**: 実行するActionクラスの完全修飾名（または単純名）
- **リクエストID**: バッチプロセスの識別子。同一のアクションクラスを複数起動する場合に区別に使われる

### Mavenプロジェクトからの起動例（ブランクプロジェクト）

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"
```

### 処理の流れ

1. `Main` クラスがハンドラキューを実行
2. `-requestPath` で指定されたリクエストパスをもとに `DispatchHandler` がアクションクラスを特定
3. アクションクラスがデータレコード1件ごとに業務ロジックを実行

**注意点**:
- `-requestPath` の区切り文字はスラッシュ `/` です
- リクエストIDは省略可能な場合もありますが（例: `-requestPath SampleBatch`）、複数のバッチプロセスを同一アクションで動かす場合は必ずリクエストIDで区別してください
- テストケース（リクエスト単体テスト）でも `requestPath` カラムに同じ書式（`アクションのクラス名/リクエストID`）で指定します

参照: `component/handlers/handlers-main.json#s3`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s2`, `setup/blank-project/blank-project-setup-NablarchBatch.json#s9`