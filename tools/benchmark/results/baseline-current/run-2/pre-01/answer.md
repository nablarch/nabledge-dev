**結論**: Nablarchバッチアプリケーションは `java` コマンドで `nablarch.fw.launcher.Main` を起点に起動します。`-requestPath` には「アクションクラス名/リクエストID」という書式で実行対象を指定します。

**根拠**:

起動コマンドの基本形は以下のとおりです。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

必須オプションは3つあり、いずれか1つでも欠けると終了コード127で即座に異常終了します。

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパスを指定する |
| `-requestPath` | 実行するアクションとリクエストIDを指定する |
| `-userId` | ユーザIDを設定する（`user.id` としてセッションコンテキスト変数に格納される） |

**`-requestPath` の書式**:

```properties
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使われます。同一の業務アクションクラスを複数プロセスで起動する場合、このリクエストIDで区別します。

**起動後の処理の流れ**:
1. `Main`（共通起動ランチャ）がハンドラキューを実行する
2. DataReaderが入力データを1件ずつ読み込む
3. DispatchHandlerが `-requestPath` で指定されたリクエストパスを元にアクションクラスを特定し、ハンドラキューに追加する
4. アクションクラスがデータ1件ごとに業務ロジックを実行し、Resultを返す
5. すべてのデータ処理完了後、StatusCodeConvertHandlerがプロセス終了コードに変換して返す

**注意点**:
- `-diConfig`、`-requestPath`、`-userId` の3オプションはすべて必須です。欠けると終了コード127で即座に異常終了します。
- Nablarchバッチはスタンドアロンアプリケーションとして動作するため、Webアプリケーションとは起動方式が異なります。

参照: `component/handlers/handlers-main.json#s3`、`processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s1`、`processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s2`、`processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s3`