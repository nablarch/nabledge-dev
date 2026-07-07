# qa-10 — run-2

## 質問

ユーザーの入力内容によって検索条件が変わるSQLを書きたい。入力がある項目だけ条件に含める方法はあるか？

## 回答

**結論**: SQLファイルに `$if(プロパティ名) {SQL条件}` 構文で可変条件を定義し、条件Beanのプロパティが null または空文字の項目は実行時に自動的に条件から除外されます。

**根拠**:

SQL ファイル（可変条件の記法）

```sql
select
  user_id,
  user_name,
  user_kbn
from
  user
where
  $if (userName) {user_name like :userName%}
  and $if (userKbn) {user_kbn in ('1', '2')}
  and birthday = :birthday
```

- `$if (プロパティ名) {条件}` と記述する。
- プロパティ値が **null または空文字列（String の場合）** のとき、その条件ブロックは SQL から除外される。
- 配列・`Collection` の場合は null またはサイズ 0 のとき除外。
- `$if` が使えるのは **where 句のみ**、かつ `$if` のネストは不可。

Javaの実装例

```java
// 入力がある項目だけセットする
UserEntity entity = new UserEntity();
entity.setUserName("なまえ"); // userKbn は設定しない（nullのまま）

AppDbConnection connection = DbConnectionContext.getConnection();

// 2番目の引数に条件Beanを渡すことで可変条件が組み立てられる
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SearchAction#findUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

上記の場合、`userKbn` は null なので `user_kbn` の条件は除外され、`user_name like :userName%` と `birthday = :birthday` だけが実行される。

**注意点**:
- `$if` 内で IN 句を可変件数にしたい場合は `:param[]` 構文を組み合わせる（例: `$if (userKbn) {user_kbn in (:userKbn[])}`）。
- この機能はウェブアプリの検索画面のような「ユーザの入力によって条件が変わる」ケース専用。異なる SQL を共通化するために使うものではなく、条件が異なる SQL は必ず別々に定義すること。

参照: libraries-database.json:s21, libraries-database.json:s16, libraries-database.json:s22

## 参照ナレッジ

- [可変条件を持つSQLを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#可変条件を持つsqlを実行する) (s21)
- [Beanオブジェクトを入力としてSQLを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#beanオブジェクトを入力としてsqlを実行する) (s16)
- [in句の条件数が可変となるSQLを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#in句の条件数が可変となるsqlを実行する) (s22)
- [実行時のBeanオブジェクトの状態を元にSQL文を動的に構築できる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#実行時のbeanオブジェクトの状態を元にsql文を動的に構築できる) (s6)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output fully covers both facts from the Expected Output: (1) it explicitly describes the $if syntax for defining variable conditions in SQL files, and (2) it clearly states that properties with null or empty string values are automatically excluded from the conditions at runtime. The Actual Output goes into considerably more detail with code examples and additional notes, but all core facts from the Expected Output are present and addressed. |
| answer_relevancy | 0.95 | 0.85 | NG | The score is 0.85 because the response largely addresses the core question about dynamically filtering SQL conditions based on user input, which is relevant. However, the score cannot be higher because the response includes irrelevant content about SQL commonalization and SQL definition splitting policies, neither of which were asked about in the input. |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | — | — |
| answer_relevancy | — | — |
| faithfulness | — | — |

### 参照事実（expected_facts）

- $if構文で可変条件を記述する。プロパティ値がnullや空文字列の場合に条件が除外される
