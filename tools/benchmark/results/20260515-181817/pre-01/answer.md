**結論**: NablarchバッチアプリケーションはJavaコマンドで `nablarch.fw.launcher.Main` クラスを指定して起動します。`-requestPath` には「アクションのクラス名/リクエストID」の書式で指定します。

**根拠**:

### 起動コマンドの基本形

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

### 必須オプション（3つすべて必須）

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパス（XMLファイル）を指定 |
| `-requestPath` | 実行するアクションのクラス名とリクエストIDを指定 |
| `-userId` | ユーザIDを指定（セッションコンテキスト変数 `user.id` に格納） |

いずれかが欠けた場合、即座に異常終了します（終了コード = 127）。

### `-requestPath` の書式

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

- **アクションのクラス名**: 実行したい業務アクションの完全修飾クラス名（またはシンプルなクラス名）
- **リクエストID**: バッチプロセスの識別子。同一アクションを複数起動する場合の識別に使用される

### Mavenからの起動例（ブランクプロジェクト）

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main ^
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"
```

**注意点**:

- `-requestPath` で指定したリクエストパスは、`DispatchHandler` がアクションクラスを特定するために使用します。正しいクラス名でないとディスパッチが失敗します
- リクエストIDは業務的な識別子として機能し、ログにも `req_id` として出力されます
- 常駐バッチと都度起動バッチでは `-diConfig` で指定するXMLファイルと `-requestPath` の値が異なります

参照: `component/handlers/handlers-main.json#s3`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s2`, `setup/blank-project/blank-project-setup-NablarchBatch.json#s9`