**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスをjavaコマンドで直接起動します。`-requestPath` には `実行するアクションのクラス名/リクエストID` の書式で指定します。

**根拠**:

起動コマンドの基本形は以下のとおりです。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

必須オプションは3つあります:

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパスを指定する。このパスでシステムリポジトリを初期化する。 |
| `-requestPath` | 実行するアクションとリクエストIDを指定する。 |
| `-userId` | ユーザIDを指定する。`user.id` としてセッションコンテキスト変数に格納される。 |

`-requestPath` の書式:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使われます。同一の業務アクションクラスを実行するプロセスを複数起動する場合などに、このリクエストIDが識別子となります。

**注意点**: 3つの必須オプション（`-diConfig`、`-requestPath`、`-userId`）のいずれかが欠けていた場合、バッチアプリケーションは即座に異常終了します（終了コード = 127）。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3