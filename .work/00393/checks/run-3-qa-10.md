# qa-10 — run-3

## 質問

ユーザーの入力内容によって検索条件が変わるSQLを書きたい。入力がある項目だけ条件に含める方法はあるか？

## 回答

**結論**: SQLファイルで `$if(プロパティ名) {条件}` 構文を使うことで、Beanプロパティに値がある項目だけをwhere条件に含めるSQLを実装できる。JDBCラッパー（`ParameterizedSqlPStatement`）とユニバーサルDAO（`UniversalDao#findAllBySqlFile`）の両方で使用できる。

**根拠**:

**`$if` 構文のルール**

```sql
-- プロパティがnull・空文字の場合はその条件が除外される
SELECT ...
FROM user
WHERE
  $if (userName) {user_name LIKE :userName%}
  AND $if (userKbn) {user_kbn IN ('1', '2')}
  AND birthday = :birthday
```

- `String` 型の場合: null または空文字列で除外
- 配列・`Collection` 型の場合: null またはサイズ0で除外
- 使用できる箇所はwhere句のみ（`$if` のネスト不可）

**実装例（ウェブアプリケーションの検索画面での典型的なパターン）**

SQLファイル:
```sql
SEARCH_PROJECT =
SELECT PROJECT_ID, PROJECT_NAME, ...
FROM PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType) {PROJECT_TYPE = :projectType}
    AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

業務アクション（`UniversalDao` 使用）:
```java
return UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

JDBCラッパー（`ParameterizedSqlPStatement`）を直接使う場合:
```java
// 第2引数にBeanを渡すと、そのBeanの状態でSQL可変条件が組み立てられる
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", condition);

SqlResultSet result = statement.retrieve(condition);
```

**in句を可変にする場合**（`$if` と `[]` 記法を組み合わせる）:
```sql
$if (userKbn) {user_kbn IN (:userKbn[])}
```
対応するBeanプロパティは `List` や配列で定義する。

**注意点**:
- この機能はウェブアプリケーションの検索画面など、ユーザー入力によって条件が変わる場合に使うもの。条件だけが異なる複数のSQLを一本化するために使うものではない（安易に共通化すると不具合の原因になる）
- フォームの値は `BeanUtil.createAndCopy` で検索条件Bean（各プロパティをDBカラム型と互換の型で定義）に移送してから渡すのが標準的なパターン

参照: libraries-database.json:s21, libraries-database.json:s22, web-application-getting-started-project-search.json:s1

## 参照ナレッジ

- [可変条件を持つSQLを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#可変条件を持つsqlを実行する) (s21)
- [in句の条件数が可変となるSQLを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#in句の条件数が可変となるsqlを実行する) (s22)
- [検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-getting-started-project-search.md#検索する) (s1)
- [実行時のBeanオブジェクトの状態を元にSQL文を動的に構築できる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#実行時のbeanオブジェクトの状態を元にsql文を動的に構築できる) (s6)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output clearly covers all facts in the Expected Output. It explains the $if syntax for variable conditions, specifies that String properties with null or empty string values are excluded, and that array/Collection types with null or size 0 are excluded. The Expected Output's key facts — $if syntax usage and the null/empty string exclusion behavior — are both explicitly addressed in the Actual Output with detailed explanations and examples. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is fully relevant to the question about writing dynamic SQL that changes search conditions based on user input, with no irrelevant statements detected. Great job staying on topic! |
| faithfulness | 0.99 | 1.0 | OK | The score is 1.00 because the actual output is perfectly faithful to the retrieval context with no contradictions found! |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「$if構文で可変条件を記述する。プロパティ値がnullや空文字列の場合に条件が除外される」は回答の「`$if(プロパティ名) {条件}` 構文を使うことで…」および「`String` 型の場合: null または空文字列で除外」に含まれている |
| answer_relevancy | — | —
| faithfulness | — | —

### 参照事実（expected_facts）

- $if構文で可変条件を記述する。プロパティ値がnullや空文字列の場合に条件が除外される
