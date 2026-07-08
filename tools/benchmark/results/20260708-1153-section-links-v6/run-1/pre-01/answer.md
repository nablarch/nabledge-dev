**結論**: NablarchバッチアプリケーションはJavaコマンドで`nablarch.fw.launcher.Main`クラスを指定して起動します。`-requestPath`オプションに「アクションクラス名/リクエストID」の書式で実行するアクションとリクエストIDを指定します。

**根拠**:

起動には以下の3つのオプションが必須です。いずれかが欠けると終了コード127で即座に異常終了します。

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

**各オプションの意味**:

| オプション | 説明 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパスを指定する |
| `-requestPath` | 実行するアクションとリクエストIDを指定する |
| `-userId` | ユーザIDを指定する（`user.id`としてセッションコンテキスト変数に格納） |

**`-requestPath`の書式**:

```bash
# 書式
-requestPath=アクションのクラス名/リクエストID

# 指定例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを複数プロセスで実行する場合などに、このリクエストIDが識別子となります。

**処理の流れ**:

1. `Main`クラスがハンドラキューを実行する
2. `DataReader`が入力データを読み込みレコードを1件ずつ提供する
3. `DispatchHandler`が`-requestPath`で指定したリクエストパスを元にアクションクラスを特定する
4. アクションクラスがデータレコード1件ごとの業務ロジックを実行する
5. 処理対象データがなくなるまで2〜4を繰り返す

**注意点**: `-diConfig`, `-requestPath`, `-userId`のいずれかが欠けていると終了コード127で即座に異常終了します。

参照:
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md
  Nablarchバッチアプリケーションの構成
  リクエストパスによるアクションとリクエストIDの指定
  Nablarchバッチアプリケーションの処理の流れ
- 共通起動ランチャ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-main.md
  アプリケーションを起動する