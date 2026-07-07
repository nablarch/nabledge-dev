# qa-02 — run-3

## 質問

DBからデータを読み込んで集計し、結果を別テーブルに書き込む定期処理を作りたい。どういう構成で実装すればいい？

## 回答

**結論**: 「DBからデータを読み込んで集計し、別テーブルへ書き込む定期処理」は Nablarch バッチの **DB to DB パターン（都度起動バッチ）** で実装します。`DatabaseRecordReader` でデータを1件ずつ読み込み、`BatchAction` を継承したアクションクラスの `handle` メソッドで集計・書き込み処理を行います。

---

**根拠**

### 全体構成（DB to DB パターン）

| 要素 | 内容 |
|---|---|
| データリーダ | `DatabaseRecordReader`（DB からレコードを1件ずつ読み込む） |
| アクションクラス | `BatchAction` を継承して `handle` メソッドに業務ロジックを実装 |
| 起動方式 | 都度起動バッチ（日次・月次の定期処理に適する） |

DB to DB パターンの特徴：入力はSELECT文の結果セット、1レコードの処理中に行われる更新は同一トランザクション下で実行されるため、障害発生時でも不整合が発生しません。

---

### ハンドラ構成（都度起動バッチ DB接続有り 最小構成）

| No. | ハンドラ | スレッド | 役割 |
|---|---|---|---|
| 1 | ステータスコード→プロセス終了コード変換ハンドラ | メイン | 終了コード変換 |
| 2 | グローバルエラーハンドラ | メイン | 実行時例外のログ出力 |
| 3 | データベース接続管理ハンドラ（初期処理用） | メイン | DB接続の取得・解放 |
| 4 | トランザクション制御ハンドラ（初期処理用） | メイン | トランザクション管理 |
| 5 | リクエストディスパッチハンドラ | メイン | アクションクラスの決定 |
| 6 | マルチスレッド実行制御ハンドラ | メイン | 並列処理制御 |
| 7 | データベース接続管理ハンドラ（業務処理用） | サブ | DB接続の取得・解放 |
| 8 | トランザクションループ制御ハンドラ | サブ | ループとコミット間隔の制御 |
| 9 | データリードハンドラ | サブ | 1件ずつレコードを読み込む |

---

### アクションクラスの実装

`BatchAction` を継承し、`handle` メソッドに集計と書き込み処理を実装します。`createReader` メソッドで `DatabaseRecordReader` を返します。

```java
public class AggregationBatchAction extends BatchAction<InputEntity> {

    @Override
    public Result handle(InputEntity inputData, ExecutionContext ctx) {
        // 集計処理（入力レコードをもとに集計結果を計算）
        ResultEntity result = aggregate(inputData);
        // 結果テーブルへの書き込み
        UniversalDao.insert(result);
        return new Result.Success();
    }

    @Override
    public DataReader<InputEntity> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader はコンポーネント定義で SQLを設定して使用
        return new DatabaseRecordReader();
    }
}
```

---

### 起動方法

バッチはコマンドラインから起動し、`-requestPath` でアクションクラスとリクエストIDを指定します。

```bash
mvn exec:java -Dexec.mainClass=nablarch.fw.launcher.Main \
    -Dexec.args="'-requestPath' 'com.example.AggregationBatchAction/AGGR0001' \
                 '-diConfig' 'classpath:aggregation-batch.xml' \
                 '-userId' 'batch'"
```

---

**注意点**

- **大量データの読み込み**: `handle` 内でさらに大量データをSELECTする場合は `UniversalDao.defer()` を使った遅延ロードを活用してください。ただし、遅延ロード中にトランザクション制御を行うとカーソルがクローズされる場合があるため注意が必要です。
  ```java
  try (DeferredEntityList<InputData> list
          = (DeferredEntityList<InputData>) UniversalDao.defer()
                                              .findAllBySqlFile(InputData.class, "FIND_ALL")) {
      for (InputData data : list) { /* 処理 */ }
  }
  ```
- **集計処理の設計**: 1レコードに対して集計・更新の処理が完結するよう設計するとトランザクション管理がシンプルになります。SQLの GROUP BY を活用してDB側で集計することも検討してください。
- **コミット間隔**: トランザクションループ制御ハンドラの `commitInterval` を適切に設定することで、処理件数に応じたコミットが行われます。

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-batch-feature-details.json:s4, nablarch-batch-getting-started-nablarch-batch.json:s3, nablarch-patterns-Nablarchバッチ処理パターン.json:s1, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, libraries-universal-dao.json:s6, libraries-universal-dao.json:s9, libraries-universal-dao.json:s14

## 参照ナレッジ

- [Nablarchバッチアプリケーションの処理の流れ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションの処理の流れ) (s3)
- [都度起動バッチの最小ハンドラ構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#都度起動バッチの最小ハンドラ構成) (s5)
- [Nablarchバッチアプリケーションで使用するデータリーダ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションで使用するデータリーダ) (s7)
- [Nablarchバッチアプリケーションで使用するアクション](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションで使用するアクション) (s8)
- [データベースアクセス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-feature-details.md#データベースアクセス) (s4)
- [業務ロジックを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md#業務ロジックを実行する) (s3)
- [DB to DB](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.md#db-to-db) (s4)
- [起動方法による分類](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.md#起動方法による分類) (s1)
- [入出力による分類](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.md#入出力による分類) (s2)
- [検索結果を遅延ロードする](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#検索結果を遅延ロードする) (s9)
- [バッチ実行(一括登録、更新、削除)を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#バッチ実行一括登録更新削除を行う) (s14)
- [ユニバーサルDAOを使うための設定を行う](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#ユニバーサルdaoを使うための設定を行う) (s6)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The actual output explicitly covers both expected facts. It mentions `DatabaseRecordReader` for reading data from the database, and it clearly states that `BatchAction` should be inherited to implement the action class. Both facts are prominently featured in the conclusion, the table, and the code example. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is fully relevant, directly addressing the question about implementing a scheduled batch process that reads data from a DB, aggregates it, and writes results to another table. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- DatabaseRecordReaderでデータベースからデータを読み込む
- BatchActionを継承したアクションクラスを実装する
