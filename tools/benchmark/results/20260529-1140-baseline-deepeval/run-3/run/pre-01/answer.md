**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` をエントリポイントとしてjavaコマンドで起動する。`-requestPath` には `アクションのクラス名/リクエストID` の書式で実行アクションとリクエストIDを指定する。

**根拠**:

起動コマンドの例:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

`-requestPath` の書式と指定例:

```bash
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使用される。同一のアクションクラスを複数プロセスで起動する場合の識別子となる。

**注意点**:

起動に必要な3つのオプションはすべて必須で、いずれかが欠けると即座に異常終了する（終了コード = 127）。

| オプション | 内容 |
|-----------|------|
| `-diConfig` | システムリポジトリの設定ファイルパス（XMLファイル） |
| `-requestPath` | 実行するアクションのクラス名/リクエストID |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3

---