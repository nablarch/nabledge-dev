### Answer

Nablarchバッチアプリケーションは、`javaコマンド`から直接起動するスタンドアロンアプリケーションとして実行します。

## 起動方法

`nablarch.fw.launcher.Main`クラスをメインクラスとして指定し、以下の3つのオプションを**必ず**指定します（いずれか欠けると終了コード127で即時異常終了）。

| オプション | 説明 |
|-----------|------|
| `-diConfig` | システムリポジトリの設定ファイルのパス |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

## -requestPath の書き方

```
-requestPath=アクションのクラス名/リクエストID
```

**例：**
```bash
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使われます。同一の業務アクションクラスを複数プロセスで起動する場合に、このリクエストIDで識別します。

## 起動コマンド例

**都度起動バッチの場合：**
```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**Mavenを使う場合（都度起動バッチ）：**
```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"
```

**Mavenを使う場合（テーブルをキューとして使ったメッセージング）：**
```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-diConfig' 'classpath:resident-batch-boot.xml' '-requestPath' 'SampleResiBatch' '-userId' 'batch_user'"
```

## 起動方式の選択

Nablarchバッチには主に2つの起動方式があります。

- **都度起動バッチ**：プロセスを都度起動して処理を実行。日次・月次などの定期バッチに使用。
- **テーブルをキューとして使ったメッセージング**：プロセスを常駐させ、DBテーブルを監視して未処理レコードを順次処理。オンライン処理の非同期バッチに使用。