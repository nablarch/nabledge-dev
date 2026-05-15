**結論**: Nablarch 6 で「DB読込→集計→別テーブルへ書込」の定期処理を実装する場合、**Nablarchバッチアプリケーション（都度起動バッチ）**を使用し、DataReader + アクションクラスの構成で実装するのが推奨です。

**根拠**:

### 推奨フレームワーク: Nablarchバッチアプリケーション

Nablarchは2種類のバッチフレームワークを提供しています。

| フレームワーク | 特徴 |
|---|---|
| **Nablarchバッチアプリケーション** | Nablarch独自。情報が豊富で有識者のアサインがしやすい。**新規開発で推奨** |
| Jakarta Batchに準拠したバッチ | 標準仕様準拠だが有識者が少なく学習コストが高い |

### 基本構成

```
都度起動バッチ（日次・月次など定期的に起動）
│
├── DataReader  ← DBから処理対象データを読み込む
│
└── アクションクラス (Action) ← 1レコードずつ受け取って業務ロジックを実行
      ├── 集計処理
      └── UniversalDao.insert() / update() で結果テーブルに書き込み
```

アクションクラスの責務:
1. DataReader を生成する
2. DataReaderが読み込んだデータレコードを元に業務ロジックを実行し、Resultを返す

入力データがDBなど安全な場合は、フォームクラスを使用せず、データレコードからエンティティクラスを作成して業務ロジックを実行すればよい。

### ハンドラ構成

- **データリードハンドラ** (`DataReadHandler`): DataReaderを使って入力データを1件ずつ読み込み、後続ハンドラに委譲
- **トランザクションループ制御ハンドラ** (`LoopHandler`): データが存在する間、後続ハンドラを繰り返し実行し、一定件数ごとにコミット
- **データベース接続管理ハンドラ**: DB接続を管理

### バッチ起動

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-requestPath' 'YourAggregateAction/BATCH01' \
                 '-diConfig' 'classpath:batch-config.xml' \
                 '-userId' 'batch_user'"
```

**注意点**:

- **常駐バッチは非推奨**: 定期処理には都度起動バッチを使用すること
- **コミット間隔**: `LoopHandler` の `commitInterval` を適切に設定すること
- **大量データの遅延ロード**: 入力データが大量の場合、`UniversalDao.defer().findAllBySqlFile()` で遅延ロードを使用しヒープ圧迫を避けること
- **定期起動**: Nablarchバッチ自体はスケジューラ機能を持たない。cronやジョブスケジューラから都度起動する設計となる

参照:
- `processing-pattern/nablarch-batch/nablarch-batch-architecture.json`
- `processing-pattern/nablarch-batch/nablarch-batch-application-design.json`
- `processing-pattern/nablarch-batch/nablarch-batch-batch.json`
- `component/handlers/handlers-data-read-handler.json`
- `component/handlers/handlers-loop-handler.json`
- `processing-pattern/jakarta-batch/jakarta-batch-database-reader.json`