**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスをエントリポイントとして起動し、`-requestPath` オプションで実行するアクションクラス名とリクエストIDを指定します。

**根拠**:

`-requestPath` の書式は以下の通りです。

```bash
実行するアクションのクラス名/リクエストID
```

起動に必要なオプションは3つあり、すべて必須です（欠けると終了コード127で即座に異常終了します）。

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリ設定ファイルのパス |
| `-requestPath` | 実行するアクションクラス名/リクエストID |
| `-userId` | ユーザID |

**javaコマンドでの起動例**:
```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**Mavenでの起動例（都度起動バッチ）**:
```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"
```

**Mavenでの起動例（常駐バッチ）**:
```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-diConfig' 'classpath:resident-batch-boot.xml' '-requestPath' 'SampleResiBatch' '-userId' 'batch_user'"
```

`-requestPath` の完全修飾クラス名を含む指定例:
```properties
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使われ、同一のアクションクラスを複数プロセスで起動する場合の識別に利用されます。

**注意点**:
- `-requestPath` は `アクションクラス名/リクエストID` の形式。クラス名のみ（リクエストIDなし）での指定も可能（例: `'SampleBatch'`）
- 常駐バッチと都度起動バッチで `-diConfig` に指定するXMLファイルが異なる
- 常駐バッチの停止は、`BATCH_REQUEST` テーブルの `PROCESS_HALT_FLG` に1をセットするのが正式な方法（`ctrl+c` は開発時のみ）
- 内部的には、DispatchHandlerが `-requestPath` で指定されたリクエストパスを元にアクションクラスを特定する

参照: `component/handlers/handlers-main.json#s3`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s2`, `setup/blank-project/blank-project-setup-NablarchBatch.json#s9`, `setup/blank-project/blank-project-setup-NablarchBatch.json#s13`