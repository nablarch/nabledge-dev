**結論**: Nablarchバッチアプリケーションは、`java`コマンドから直接起動するスタンドアロンアプリケーションです。起動には`Main`クラスをエントリポイントとして使用し、コマンドライン引数`-requestPath`でアクションクラスとリクエストIDを指定します。

**根拠**:

Nablarchバッチアプリケーションの基本的な起動方法は以下の通りです。

**1. アプリケーション構成**

Nablarchバッチアプリケーションは`java`コマンドから直接起動するスタンドアロンアプリケーションです。起点となるメインクラス(`Main`)がシステムリポジトリとログを初期化後、ハンドラキューを実行します。

**2. 起動コマンドの形式**

コマンドライン引数に`-requestPath`を指定してアクションクラスとリクエストIDを指定します。

```
java -cp <classpath> nablarch.fw.launcher.Main \
  -requestPath=com.sample.SampleBatchAction/BATCH0001 \
  <その他のオプション>
```

`-requestPath`の書式:
```
-requestPath=アクションのクラス名/リクエストID
```

リクエストIDは各バッチプロセスの識別子です。同一の業務アクションクラスを実行するプロセスを複数起動する場合、このリクエストIDで識別します。

**3. 起動後の処理フロー**

1. 共通起動ランチャ(`Main`)がハンドラキューを実行
2. データリーダ(`DataReader`)が入力データを読み込み、データレコードを1件ずつ提供
3. ディスパッチハンドラ(`DispatchHandler`)がコマンドライン引数(`-requestPath`)のリクエストパスから処理すべきアクションクラスを特定し、ハンドラキューの末尾に追加
4. アクションクラスがデータレコード1件ごとの業務ロジックを実行
5. 処理対象データがなくなるまで繰り返す
6. ステータスコード→プロセス終了コード変換ハンドラ(`StatusCodeConvertHandler`)がプロセス終了コードを返却

**4. バッチタイプ**

| タイプ | 説明 |
|---|---|
| 都度起動バッチ | 日次や月次など、定期的にプロセスを起動してバッチ処理を実行 |
| 常駐バッチ | プロセスを起動しておき、一定間隔でバッチ処理を実行。ただし新規開発では`db_messaging`を推奨 |

**注意点**:
- 常駐バッチはマルチスレッド実行時、処理が遅いスレッドの終了を他スレッドが待つため、要求データ取り込み遅延が発生する可能性があります。新規開発では常駐バッチではなく`db_messaging`の使用を推奨します。
- 起動時のシステムリポジトリ設定ファイルパスも指定が必要です（詳細は`main-run_application`参照）。

参照: `nablarch-batch-architecture.json#nablarch-batch-application-structure`, `nablarch-batch-architecture.json#request-path-action-request-id`, `nablarch-batch-architecture.json#nablarch-batch-process-flow`, `nablarch-batch-feature_details.json#batch-application-startup`, `nablarch-batch-feature_details.json#system-repository-initialization`
