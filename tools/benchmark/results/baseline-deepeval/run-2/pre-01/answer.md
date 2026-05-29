Step 5: 回答を生成します。

---

**結論**: NablarchバッチアプリケーションはMainクラス (`nablarch.fw.launcher.Main`) を `java` コマンドで直接起動し、`-requestPath` に「アクションのクラス名/リクエストID」の形式で指定します。

**根拠**:

Nablarchバッチはスタンドアロンアプリケーションとして動作し、`nablarch.fw.launcher.Main` がエントリポイントです。起動には以下3つのオプションが**必須**で、いずれか1つでも欠けると終了コード127で即座に異常終了します。

| オプション | 役割 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパス |
| `-requestPath` | 実行するアクションのクラス名とリクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

**`-requestPath` の書式**:

```bash
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

**java コマンドによる起動例**:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**Maven (mvn exec:java) による起動例**（ブランクプロジェクトの場合）:

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main ^
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"
```

リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを実行するプロセスを複数起動する場合などに、このリクエストIDが識別子となります。

**注意点**:
- `-diConfig`・`-requestPath`・`-userId` の3オプションはすべて必須です。1つでも欠けると終了コード127で異常終了します。
- 起動の流れとして、Mainクラスがハンドラキューを実行し、ディスパッチハンドラが `-requestPath` で指定されたリクエストパスを元に処理すべきアクションクラスを特定します。

参照: `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s1`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s2`, `component/handlers/handlers-main.json:s3`, `setup/blank-project/blank-project-setup-NablarchBatch.json:s9`

---