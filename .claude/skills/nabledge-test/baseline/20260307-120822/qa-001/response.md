**結論**: NablarchバッチアプリケーションはjavaコマンドからMainクラスを直接起動するスタンドアロンアプリケーションです。起動時は `-requestPath` オプションで実行するアクションクラスとリクエストIDを指定します。

**根拠**:

**1. 起動コマンドの基本形**

NablarchバッチアプリケーションはjavaコマンドからMainクラスを起動します。

```
java <起動オプション> nablarch.fw.launcher.Main \
  -diConfig <設定ファイルパス> \
  -requestPath <アクションクラス名/リクエストID> \
  -userId <ユーザID>
```

**2. `-requestPath` の指定方法**

```properties
-requestPath=com.sample.SampleBatchAction/BATCH0001
```

書式: `-requestPath=アクションのクラス名/リクエストID`

- **アクションクラス名**: 実行するバッチアクションの完全修飾クラス名
- **リクエストID**: 各バッチプロセスの識別子。同一の業務アクションクラスを実行するプロセスを複数起動する場合、このリクエストIDで識別する

**3. システムリポジトリの設定ファイル**

アプリケーション起動時にシステムリポジトリの設定ファイルパスを `-diConfig` オプションで指定します。詳細は `main-run_application` を参照。

**4. バッチタイプ別の違い**

| バッチタイプ | 説明 |
|---|---|
| 都度起動バッチ | 日次・月次など定期的にプロセスを起動して処理を実行 |
| 常駐バッチ | プロセスを起動しておき、一定間隔でバッチ処理を実行 |

> **重要**: 常駐バッチは新規開発では推奨されません。マルチスレッド実行時に処理が遅いスレッドの終了を他スレッドが待つため要求データ取り込み遅延が発生する可能性があります。新規開発では `db_messaging` の使用を推奨。

**5. 使用するアクションクラス**

| アクションクラス | 用途 |
|---|---|
| `BatchAction` | 汎用バッチアクションテンプレート |
| `FileBatchAction` | ファイル入力バッチアクションテンプレート（`data_format` 使用時） |
| `NoInputDataBatchAction` | 入力データ不要のバッチアクションテンプレート |
| `AsyncMessageSendAction` | 応答不要メッセージ送信 |

**注意点**:
- `FileBatchAction` は `data_format` を使用する場合に使用。`data_bind` を使用する場合は他のアクションクラスを選択すること
- 常駐バッチはマルチスレッド実行時に遅延の可能性があるため、新規開発では `db_messaging` を推奨
- 同一バッチアプリケーションの同時実行を防止したい場合は `duplicate_process_check_handler` を使用

参照:
- `nablarch-batch-architecture.json#nablarch-batch-application-structure`
- `nablarch-batch-architecture.json#request-path-action-request-id`
- `nablarch-batch-feature_details.json#batch-application-startup`
- `nablarch-batch-feature_details.json#system-repository-initialization`
- `nablarch-batch-architecture.json#actions`
