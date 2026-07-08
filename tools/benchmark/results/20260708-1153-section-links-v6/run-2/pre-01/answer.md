**結論**: Nablarchバッチアプリケーションは、`nablarch.fw.launcher.Main` クラスをjavaコマンドで直接起動します。`-requestPath` には「アクションのクラス名/リクエストID」の書式で指定します。

**根拠**:

起動には以下の3つのオプションが必須です（いずれかが欠けると終了コード127で即座に異常終了します）。

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパスを指定する |
| `-requestPath` | 実行するアクションとリクエストIDを指定する |
| `-userId` | ユーザIDを設定する |

**-requestPath の書式**:

```bash
実行するアクションのクラス名/リクエストID
```

**起動コマンドの例**:

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

リクエストIDは各バッチプロセスの識別子として使用されます。同一の業務アクションクラスを実行するプロセスを複数起動する場合など、このリクエストIDが識別子となります。

なお、アーキテクチャ上では `-requestPath` で指定されたリクエストパスをもとに、ハンドラキュー内のリクエストディスパッチハンドラが呼び出すアクションクラスを決定します。

**注意点**: `-requestPath` で指定した値は `Request#getRequestPath` が返すようになります。アクションクラス内で参照する場合はこのAPIを使用してください。

参照:
- 共通起動ランチャ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-main.md
  アプリケーションを起動する
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md
  リクエストパスによるアクションとリクエストIDの指定