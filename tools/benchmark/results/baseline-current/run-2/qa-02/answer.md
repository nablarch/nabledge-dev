**結論**: DBからデータを読み込み集計して別テーブルに書き込む定期処理は、**Nablarchバッチの都度起動バッチ（DB to DBパターン）** として実装します。Nablarch Batch と Jakarta Batch のどちらでも実装できますが、構成が異なります。

## Nablarch Batch で実装する場合

### 処理パターンの選択

「DB to DB」かつ「日次・月次などの定期実行」であれば、**都度起動バッチ** が該当します。

> 都度起動バッチ：プロセスを都度起動して処理を実行。日次や月次など定期的なバッチ処理に使用。

### ハンドラキュー構成（最小構成）

DB接続ありの都度起動バッチの最小ハンドラ構成：

| No. | ハンドラ | スレッド |
|-----|---------|---------|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | メイン |
| 2 | グローバルエラーハンドラ | メイン |
| 3 | データベース接続管理ハンドラ（初期処理/終了処理用） | メイン |
| 4 | トランザクション制御ハンドラ（初期処理/終了処理用） | メイン |
| 5 | リクエストディスパッチハンドラ | メイン |
| 6 | マルチスレッド実行制御ハンドラ | メイン |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブ |
| 8 | **トランザクションループ制御ハンドラ** | サブ |
| 9 | **データリードハンドラ** | サブ |

### データリーダ

DB読み込みには `DatabaseRecordReader` を使用します。SELECT文の結果セットを1件ずつ読み込み、アクションクラスに渡します。

### アクションクラスの責務（DB to DB）

- 入力：SELECT文の結果レコード1件
- 処理：集計ロジックを実行
- 出力：別テーブルへのINSERT/UPDATE（UniversalDao等を使用）

1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません。

### コミット間隔の設定

トランザクションループ制御ハンドラの `commitInterval` でコミット間隔を調整します：

```xml
<component class="nablarch.fw.handler.LoopHandler">
  <!-- コミット間隔に1000を指定 -->
  <property name="commitInterval" value="1000" />
</component>
```

## Jakarta Batch で実装する場合

### バッチ種類の選択

DBからレコードを読み込んで業務処理を実行するパターンは **Chunk タイプ** を使用します（Batchletは「SQL1つで処理が完結」等のタスク指向向け）。

### 実装クラス構成

| クラス | 責務 |
|--------|------|
| **ItemReader** | DBからデータを読み込み、フォームに変換して返す |
| **ItemProcessor** | 集計ロジックを実行し、出力エンティティに変換する |
| **ItemWriter** | エンティティを別テーブルにINSERT/UPDATE |
| **エンティティ** | 出力テーブルと1対1対応のクラス |

**注意点**:

1. **定期起動の仕組みは別途必要** — バッチ自体はプロセスとして実装しますが、日次・月次のスケジューリングはOSのcron・ジョブスケジューラ等で制御します（Nablarchの管轄外）。
2. **コミット間隔のチューニング** — 大量データ処理時はコミット間隔が性能に直結します。小さすぎるとコミットオーバーヘッドが増加し、大きすぎると障害時のリカバリ範囲が広がります。
3. **マルチスレッドの注意** — マルチスレッド実行制御ハンドラを使う場合、アクションクラスはスレッドセーフに実装する必要があります。
4. **Jakarta Batch の場合** — ItemReader/ItemProcessor/ItemWriter は Jakarta Batch仕様のインタフェースを実装するため、仕様書も参照してください。

参照: guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.json#s1, #s2, #s4 / processing-pattern/nablarch-batch/nablarch-batch-architecture.json#s5, #s7 / processing-pattern/jakarta-batch/jakarta-batch-architecture.json#s2 / processing-pattern/jakarta-batch/jakarta-batch-application-design.json#s2 / component/handlers/handlers-loop-handler.json#s5