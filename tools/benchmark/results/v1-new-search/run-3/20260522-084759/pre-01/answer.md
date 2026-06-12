**結論**: NablarchバッチアプリケーションはJavaコマンドで `nablarch.fw.launcher.Main` クラスを起動します。`-requestPath` は `アクションのクラス名/リクエストID` の形式で指定します。

**根拠**:

起動コマンドは以下のとおりです。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

フレームワークの動作に必要な以下の3つのオプションは必ず指定してください。いずれかが欠けていると即座に異常終了します（終了コード = 127）。

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパス |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納される） |

`-requestPath` の書式は次のとおりです。

```
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使用されます。同一の業務アクションクラスを実行するプロセスを複数起動する場合などは、このリクエストIDで区別します。

**処理の流れ**: 起動後、`-requestPath` で指定されたリクエストパスをもとにディスパッチハンドラが処理すべきアクションクラスを特定し、ハンドラキューの末尾に追加します。

**注意点**: 3つの必須オプション（`-diConfig`、`-requestPath`、`-userId`）のうち1つでも欠けると終了コード 127 で異常終了します。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3

---