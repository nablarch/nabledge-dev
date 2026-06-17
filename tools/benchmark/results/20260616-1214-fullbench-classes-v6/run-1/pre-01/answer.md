**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスを `java` コマンドで直接起動します。`-requestPath` には「実行するアクションのクラス名/リクエストID」という書式で指定します。

**根拠**:

起動コマンドは以下の形式です。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

必須オプションは以下の3つで、いずれか1つでも欠けると即座に異常終了します（終了コード = 127）。

| オプション | 内容 |
|-----------|------|
| `-diConfig` | システムリポジトリの設定ファイルのパスを指定する |
| `-requestPath` | 実行するアクションとリクエストIDを指定する |
| `-userId` | ユーザIDを設定する（`user.id` としてセッションコンテキスト変数に格納）|

`-requestPath` の書式は以下のとおりです。

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

起動後の処理の流れ:
1. `Main` クラスがハンドラキューを実行する
2. データリーダ（DataReader）が入力データを1件ずつ読み込む
3. ディスパッチハンドラ（DispatchHandler）が `-requestPath` で指定されたリクエストパスをもとに処理すべきアクションクラスを特定する
4. アクションクラスがデータレコード1件ごとの業務ロジックを実行する
5. 処理対象データがなくなるまで繰り返し、最終的にステータスコードをプロセス終了コードに変換して終了する

**注意点**:
- リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを実行するプロセスを複数起動する場合、このリクエストIDが識別子となります。

参照: nablarch-batch-architecture.json:s2, component/handlers/handlers-main.json:s3