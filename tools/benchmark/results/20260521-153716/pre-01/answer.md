Step 5〜7: 回答を生成し検証します。

---

**結論**: NablarchバッチアプリケーションはMainクラス（`nablarch.fw.launcher.Main`）をjavaコマンドで直接起動するスタンドアロンアプリです。`-requestPath`には「アクションのクラス名/リクエストID」の形式で指定します。

**根拠**:

`-requestPath`の書式:
```
-requestPath=アクションのクラス名/リクエストID
```

例:
```
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

起動時に必須となるオプションは以下の3つです。いずれかが欠けている場合は即座に異常終了します（終了コード = 127）。

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパス |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザID（`user.id`としてセッションコンテキストに格納される） |

**javaコマンドによる起動例**:
```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**Mavenプロジェクトからの起動例**（都度起動バッチ）:
```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main ^
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"
```

**注意点**: リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを実行するプロセスを複数起動する場合、このリクエストIDが識別子となります。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3, blank-project-setup-NablarchBatch.json:s9

---