**結論**: Nablarchバッチアプリケーションは `java nablarch.fw.launcher.Main` コマンドで起動し、`-requestPath` には `アクションのクラス名/リクエストID` の書式で指定します。

**根拠**:

起動に必要な3つのオプションを必ず指定します。いずれかが欠けると即座に異常終了（終了コード=127）します。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

各オプションの意味：

- **`-diConfig`**: システムリポジトリの設定ファイルのパスを指定します。このパスでシステムリポジトリを初期化します。
- **`-requestPath`**: 実行するアクションとリクエストIDを指定します。書式は以下のとおりです。

```bash
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

- **`-userId`**: ユーザIDを設定します。セッションコンテキスト変数に `user.id` という名前で格納されます。

**注意点**: リクエストIDは各バッチプロセスの識別子として使用されます。同一のアクションクラスを複数プロセスで起動する場合に、このリクエストIDが識別子となります。

参照: component/handlers/handlers-main.json:s3, processing-pattern/nablarch-batch/nablarch-batch-architecture.json:s2