Nablarchバッチアプリケーションは、`javaコマンド`からスタンドアロンのアプリケーションとして直接起動します。

## 起動方法

メインクラスとして `nablarch.fw.launcher.Main` を指定し、以下の3つのオプションを必ず指定します（いずれか欠けると終了コード127で異常終了します）。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

## -requestPath の書き方

```
-requestPath=アクションのクラス名/リクエストID
```

**指定例：**
```
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

- **アクションのクラス名**：実行するアクションクラスの完全修飾クラス名
- **リクエストID**：各バッチプロセスの識別子。同一の業務アクションクラスを複数プロセスで起動する場合などに識別子として使用します

## Mavenを使った起動例（都度起動バッチ）

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-diConfig' 'classpath:batch-boot.xml' '-requestPath' 'SampleBatch' '-userId' 'batch_user'"
```

## 起動方式の選択

Nablarchバッチには2つの起動方式があります。

| 方式 | 用途 |
|------|------|
| **都度起動バッチ** | 日次・月次など定期的にプロセスを起動して処理を実行する場合 |
| **テーブルをキューとして使ったメッセージング** | プロセスを常駐させ、DBテーブルを監視して未処理レコードを順次処理する場合（オンライン処理からの非同期バッチに適する） |