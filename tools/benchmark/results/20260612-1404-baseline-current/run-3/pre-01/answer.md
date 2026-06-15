**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスをjavaコマンドで直接起動する。`-requestPath` には `実行するアクションのクラス名/リクエストID` の書式で指定する。

**根拠**:

起動コマンドの基本形は以下のとおり。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

`-requestPath` の書式:

```bash
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として用いられる。同一の業務アクションクラスを実行するプロセスを複数起動する場合などは、このリクエストIDが識別子となる。

**注意点**:
- `-diConfig`（システムリポジトリ設定ファイルのパス）、`-requestPath`、`-userId` の3つは必須オプション。いずれかが欠けていた場合は即座に異常終了する（終了コード = 127）。

参照: nablarch-batch-architecture.json:s2, handlers-main.json:s3