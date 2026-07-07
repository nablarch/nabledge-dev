# qa-02 — run-2

## 質問

DBからデータを読み込んで集計し、結果を別テーブルに書き込む定期処理を作りたい。どういう構成で実装すればいい？

## 回答

**結論**: DB to DB パターンの**都度起動バッチ**として実装します。`DatabaseRecordReader` で入力テーブルを1レコードずつ読み込み、`BatchAction` を継承した業務アクションで集計処理を行い、`UniversalDao` で結果テーブルに書き込む構成です。

---

**根拠**

#### 全体構成（役割分担）

| 役割 | クラス/ハンドラ |
|------|---------------|
| 起動 | `nablarch.fw.launcher.Main`（`-requestPath`引数で指定） |
| DB読み込み | `DatabaseRecordReader`（データリーダ） |
| 業務処理・DB書き込み | `BatchAction` を継承した業務アクション |
| トランザクション制御 | `トランザクションループ制御ハンドラ` |

#### ハンドラ構成（都度起動バッチ DB接続有り）

```
メインスレッド:
  1. ステータスコード→プロセス終了コード変換ハンドラ
  2. グローバルエラーハンドラ
  3. データベース接続管理ハンドラ（初期処理/終了処理用）
  4. トランザクション制御ハンドラ（初期処理/終了処理用）
  5. リクエストディスパッチハンドラ
  6. マルチスレッド実行制御ハンドラ

サブスレッド:
  7. データベース接続管理ハンドラ（業務処理用）
  8. トランザクションループ制御ハンドラ   ← コミット間隔ごとにコミット
  9. データリードハンドラ               ← 1レコードずつ読み込み
```

#### 業務アクションの実装例

```java
public class AggregationBatchAction extends BatchAction<SqlRow> {

    @Override
    public Result handle(SqlRow inputData, ExecutionContext ctx) {
        // 1. 入力レコードから集計処理
        AggregationResult result = aggregate(inputData);

        // 2. 結果テーブルへ書き込み
        UniversalDao.insert(result);

        return new Result.Success();
    }

    @Override
    public DataReader<SqlRow> createReader(ExecutionContext ctx) {
        // DatabaseRecordReader で入力テーブルを読み込む
        DatabaseRecordReader reader = new DatabaseRecordReader();
        // ... SQL設定
        return reader;
    }
}
```

#### DB to DB パターンの特徴

- 入力はSELECT文の結果セットの各レコード
- 1レコードの処理中に行われる更新は全て同一トランザクション下で実行されるため、障害発生時でも不整合が発生しない

#### 起動方法

```bash
java nablarch.fw.launcher.Main \
  -requestPath=com.example.AggregationBatchAction/BATCH0001 \
  -diConfig classpath:aggregation-batch.xml \
  -userId batch-user
```

---

**注意点**:
- `トランザクションループ制御ハンドラ` の `commitInterval` でコミット間隔を設定することで、大量データ処理時のメモリ使用量を制御できる。
- `DatabaseRecordReader` でデータを読み込む場合は、`DataReader` インタフェースを実装するか、`BatchAction.createReader` でリーダを返す。

参照: nablarch-batch-architecture.json:s3, nablarch-batch-architecture.json:s5, nablarch-batch-architecture.json:s7, nablarch-batch-architecture.json:s8, nablarch-patterns-Nablarchバッチ処理パターン.json:s2, nablarch-patterns-Nablarchバッチ処理パターン.json:s4, nablarch-batch-getting-started-nablarch-batch.json:s3

## 参照ナレッジ

- [Nablarchバッチアプリケーションの処理の流れ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションの処理の流れ) (s3)
- [都度起動バッチの最小ハンドラ構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#都度起動バッチの最小ハンドラ構成) (s5)
- [Nablarchバッチアプリケーションで使用するデータリーダ](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションで使用するデータリーダ) (s7)
- [Nablarchバッチアプリケーションで使用するアクション](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションで使用するアクション) (s8)
- [DB to DB](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.md#db-to-db) (s4)
- [入出力による分類](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.md#入出力による分類) (s2)
- [業務ロジックを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-getting-started-nablarch-batch.md#業務ロジックを実行する) (s3)
- [データベースアクセス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-feature-details.md#データベースアクセス) (s4)
- [Nablarchバッチアプリケーションの構成](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#nablarchバッチアプリケーションの構成) (s1)
- [リクエストパスによるアクションとリクエストIDの指定](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/nablarch-batch/nablarch-batch-architecture.md#リクエストパスによるアクションとリクエストidの指定) (s2)
- [起動方法による分類](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/guide/nablarch-patterns/nablarch-patterns-Nablarchバッチ処理パターン.md#起動方法による分類) (s1)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output explicitly covers both facts from the Expected Output checklist. It mentions `DatabaseRecordReader` for reading data from the database (in the table, code example, and explanatory text), and it mentions `BatchAction` inheritance for implementing the action class (in the table, code example showing `AggregationBatchAction extends BatchAction<SqlRow>`, and explanatory text). Both expected facts are clearly and explicitly addressed. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is perfectly relevant, directly addressing the question about how to implement a batch process that reads data from a DB, aggregates it, and writes the results to another table. No irrelevant statements were found! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「DatabaseRecordReaderでデータベースからデータを読み込む」は回答の全体構成表・コード例（`createReader`メソッド）・注意点に含まれている。参照事実「BatchActionを継承したアクションクラスを実装する」は回答の全体構成表・コード例（`AggregationBatchAction extends BatchAction<SqlRow>`）に含まれている。 |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- DatabaseRecordReaderでデータベースからデータを読み込む
- BatchActionを継承したアクションクラスを実装する
