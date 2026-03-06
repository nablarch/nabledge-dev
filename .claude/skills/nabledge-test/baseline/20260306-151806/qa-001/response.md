**結論**: NablarchバッチアプリケーションはJavaのスタンドアロンアプリケーションとして、`java`コマンドから直接起動します。起動時にコマンドライン引数 `-requestPath` でアクションクラスとリクエストIDを指定します。

**根拠**:

Nablarchバッチアプリケーションは `java` コマンドから直接起動するスタンドアロンアプリケーションです。起動の起点となるのは **Main クラス** で、システムリポジトリとログを初期化後にハンドラキューを実行します。

**起動コマンドの基本形式:**

```bash
java -cp <クラスパス> nablarch.fw.launcher.Main \
  -diConfig <設定ファイルパス> \
  -requestPath <アクションクラス名>/<リクエストID> \
  -userId <ユーザID>
```

**`-requestPath` の指定方法:**

```properties
-requestPath=アクションのクラス名/リクエストID
```

**例:**

```properties
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

リクエストIDは各バッチプロセスの識別子です。同一の業務アクションクラスを複数プロセスで起動する場合、リクエストIDで識別します。

**バッチタイプ:**

- **都度起動バッチ**: 日次・月次など定期的にプロセスを起動してバッチ処理を実行
- **常駐バッチ**: プロセスを起動しておき、一定間隔でバッチ処理を実行

> **重要**: 新規開発では常駐バッチではなく `:ref:db_messaging` を推奨。常駐バッチはマルチスレッド実行時に処理が遅いスレッドの終了を他スレッドが待つため、要求データ取り込み遅延が発生する可能性があります。

**起動時のシステムリポジトリ設定:**

アプリケーション起動時にシステムリポジトリの設定ファイルパスを `-diConfig` 引数で指定します。詳細は知識ファイルの参照先（`main-run_application`）に記載されていますが、該当する知識ファイルは現時点では未作成です。

**注意点**:
- 都度起動バッチと常駐バッチの実装方法は同一で、相違点はハンドラ構成のみ
- 常駐バッチの新規開発では `db_messaging` への移行を検討すること
- 同時実行防止が必要な場合は `duplicate_process_check_handler` を使用する

参照: `nablarch-batch-architecture.json#nablarch-batch-application-structure`, `nablarch-batch-architecture.json#request-path-action-request-id`, `nablarch-batch-feature_details.json#batch-application-startup`, `nablarch-batch-feature_details.json#system-repository-initialization`
