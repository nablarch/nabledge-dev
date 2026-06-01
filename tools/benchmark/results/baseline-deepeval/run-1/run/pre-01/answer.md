**結論**: Nablarchバッチアプリケーションはjavaコマンドで `nablarch.fw.launcher.Main` クラスを直接起動します。`-requestPath` オプションには `アクションのクラス名/リクエストID` の形式で実行するアクションを指定します。

**根拠**:

起動コマンドの例:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

`-requestPath` の書式:

```
-requestPath=アクションのクラス名/リクエストID
```

具体的な指定例:

```
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

起動に必須の3つのオプション:

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパス |
| `-requestPath` | 実行するアクションのクラス名とリクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納される） |

リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを実行するプロセスを複数起動する場合などに、このリクエストIDが識別子となります。

**注意点**: `-diConfig`、`-requestPath`、`-userId` のいずれかが欠けていた場合は、即座に異常終了します（終了コード = 127）。

参照: handlers-main.json:s3, nablarch-batch-architecture.json:s2, nablarch-batch-architecture.json:s1

---