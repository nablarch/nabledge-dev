**結論**: NablarchバッチアプリケーションはJavaコマンドで`nablarch.fw.launcher.Main`クラスを起動する。`-requestPath`には`アクションのクラス名/リクエストID`の書式で実行対象を指定する。

**根拠**:

起動コマンドの実行例:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

フレームワークの動作に必要な3つのオプションはすべて必須。いずれか1つでも欠けると終了コード127で即座に異常終了する。

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパスを指定 |
| `-requestPath` | 実行するアクションとリクエストIDを指定 |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納される） |

**`-requestPath`の書式**:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

- `アクションのクラス名`は完全修飾クラス名またはパッケージ相対クラス名
- `リクエストID`は各バッチプロセスの識別子。同一アクションクラスを複数プロセスで起動する場合に区別するために使用する

**注意点**: 3つの必須オプションのうち1つでも欠けている場合、終了コード127で即座に異常終了する。

参照: handlers-main.json:s3, nablarch-batch-architecture.json:s2