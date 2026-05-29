Step 5: 回答を生成します。

---

**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスをjavaコマンドで起動します。`-requestPath` には「アクションのクラス名/リクエストID」の形式で指定します。

**根拠**:

起動に必要な3つのオプションを必ず指定する必要があります（いずれか欠けると終了コード127で即座に異常終了します）。

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパス |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザーID（セッションコンテキスト変数 `user.id` に格納） |

**`-requestPath` の書式**:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

**javaコマンドでの起動例**:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**Mavenでの起動例（都度起動バッチ）**:

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main ^
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"
```

**Mavenでの起動例（常駐バッチ）**:

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main ^
    -Dexec.args="'-diConfig' 'classpath:resident-batch-boot.xml' '-requestPath' 'SampleResiBatch' '-userId' 'batch_user'"
```

**注意点**:
- リクエストIDは各バッチプロセスの識別子として使われます。同一アクションクラスを複数プロセスで起動する場合はリクエストIDで区別します。
- 常駐バッチを終了する正しい方法は `BATCH_REQUEST` テーブルの `PROCESS_HALT_FLG` に `1` を設定することです（Ctrl+Cでの強制終了は開発・テスト用途のみ）。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3, blank-project-setup-NablarchBatch.json:s9, blank-project-setup-NablarchBatch.json:s13

---