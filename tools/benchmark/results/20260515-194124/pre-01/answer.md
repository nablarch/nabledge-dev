**結論**: NablarchバッチアプリケーションはJavaコマンドで `nablarch.fw.launcher.Main` クラスを起動します。`-requestPath` には `アクションのクラス名/リクエストID` の形式で指定します。

**根拠**:

起動コマンドの基本形は以下の通りです。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

起動時に必須の3つのオプション（いずれか欠けると終了コード127で即異常終了）:

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルパス（XMLファイル） |
| `-requestPath` | 実行するアクションとリクエストIDを指定 |
| `-userId` | ユーザID（セッションコンテキスト変数 `user.id` に格納） |

**`-requestPath` の書き方**:

```
-requestPath=アクションのクラス名/リクエストID
```

具体例:
```
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として使われます。同一の業務アクションクラスを複数のプロセスで実行する場合に、このリクエストIDで識別します。

**処理の流れ**:
1. `Main` クラスがハンドラキューを実行
2. DataReader が入力データを1件ずつ読み込み
3. DispatchHandler が `-requestPath` で指定されたリクエストパスを元にアクションクラスを特定
4. アクションクラスがデータレコード1件ごとに業務ロジックを実行
5. データがなくなるまで繰り返し、最後にプロセス終了コードを返す

**注意点**:
- `-requestPath` で指定した値は `Request#getRequestPath()` で取得できます
- 設定ファイルパスは `file:` プレフィックスを付けてファイルシステムパスとして指定できます
- `-requestPath` と `-diConfig` と `-userId` の3つはすべて必須です。1つでも欠けると起動直後に終了コード127で異常終了します

参照: `component/handlers/handlers-main.json#s3`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s2`, `processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s3`