**結論**: Nablarchバッチアプリケーションは `nablarch.fw.launcher.Main` クラスを `java` コマンドで直接起動し、`-requestPath` に「アクションのクラス名/リクエストID」の形式で実行対象を指定します。

**根拠**:

起動に必要な3つのオプションがあり、いずれか1つでも欠けると即座に異常終了します（終了コード = 127）。

| オプション | 内容 |
|---|---|
| `-diConfig` | システムリポジトリの設定ファイルのパス |
| `-requestPath` | 実行するアクションとリクエストID |
| `-userId` | ユーザID |

**-requestPath の書式:**

```bash
-requestPath=アクションのクラス名/リクエストID
```

**指定例:**

```bash
# アーキテクチャ概要の記載例
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

**実際の起動コマンド例:**

```bash
java nablarch.fw.launcher.Main \
  -diConfig file:./batch-config.xml \
  -requestPath admin.DataUnloadBatchAction/BC0012 \
  -userId testUser
```

リクエストIDは各バッチプロセスの識別子として用いられます。同一の業務アクションクラスを実行するプロセスを複数起動する場合などに、このリクエストIDが識別子となります。

**注意点**:
- `-requestPath` で指定されたリクエストパスを `Request#getRequestPath` が返すようになり、ハンドラキューの `RequestPathJavaPackageMapping`（リクエストディスパッチハンドラ）がこれを解析して呼び出すアクションを決定します。
- `RequestPathJavaPackageMapping` には `basePackage` と `basePath` を設定するため、`-requestPath` にはベースパス以降のクラス名のみを指定する形になります（プロジェクト設定に依存）。

参照:
- アーキテクチャ概要
  .claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md
  リクエストパスによるアクションとリクエストIDの指定
  Nablarchバッチアプリケーションの構成
- 共通起動ランチャ
  .claude/skills/nabledge-6/docs/component/handlers/handlers-main.md
  アプリケーションを起動する