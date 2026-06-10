**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスを `java` コマンドで起動します。`-requestPath` には `アクションのクラス名/リクエストID` の形式で指定します。

**根拠**:

起動には以下の3つのオプションが必須です。いずれかが欠けると即座に異常終了します（終了コード = 127）。

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパス |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

**`-requestPath` の書式:**

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

**javaコマンドによる起動例:**

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**Mavenから起動する場合:**

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main ^
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"
```

**注意点**:
- リクエストIDは各バッチプロセスの識別子として使われます。同一のアクションクラスを使うプロセスを複数起動する場合は、リクエストIDで区別します。
- `-diConfig` には `classpath:` プレフィックス（クラスパス上のXML）または `file:` プレフィックス（ファイルシステム上のXML）が使えます。

参照: nablarch-batch-architecture.json:s1, nablarch-batch-architecture.json:s2, handlers-main.json:s3, blank-project-setup-NablarchBatch.json:s9