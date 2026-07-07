# qa-10 — run-1

## 質問

ユーザーの入力内容によって検索条件が変わるSQLを書きたい。入力がある項目だけ条件に含める方法はあるか？

## 回答

**結論**: SQLファイルのWHERE句に `$if(プロパティ名) {SQL条件}` という可変条件構文を記述します。対応するBeanプロパティが null / 空文字 / 空コレクションの場合、その条件が実行時に自動除外されます。

**根拠**:

#### SQLファイルの書き方（`$if` 構文）

```sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    PROJECT_TYPE,
    PROJECT_START_DATE,
    PROJECT_END_DATE
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName)           {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType)           {PROJECT_TYPE = :projectType}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectEndDateBegin)   {PROJECT_END_DATE >= :projectEndDateBegin}
```

- プロパティが **null / 空文字 / 空コレクション** の場合、その `$if` ブロックは条件から除外される
- IN句の可変条件は末尾に `[]` を付ける: `$if(projectClass) {PROJECT_CLASS IN (:projectClass[])}`

#### 除外されるタイミング

| 型 | 除外される条件 |
|----|---------------|
| String | null または空文字列 |
| その他のオブジェクト | null |
| 配列 / Collection | null またはサイズ0 |

#### 制約

- `$if` が使用できる箇所は **WHERE句のみ**
- `$if` の入れ子は不可

#### ユニバーサルDAOでの実行（推奨）

```java
// 検索条件Beanを作成（入力されていない項目はnull/空文字のまま）
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// SQLIDを指定して検索（$if が自動的に条件の組み立てを行う）
List<Project> result = UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

#### JDBCラッパーでの実行

```java
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");
// userKbn は null のまま → SQL の user_kbn 条件は除外される

AppDbConnection connection = DbConnectionContext.getConnection();
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

**注意点**:
- この機能は**検索画面のように入力内容で条件が変わる場合**に使用するものです。「条件だけが異なる複数のSQLを共通化する」目的には使用しないでください（安易な共通化は思わぬ不具合の原因になります）。
- IN句で条件数が可変の場合、`$if` と組み合わせて可変条件として定義してください。可変条件にしない場合、値が null のとき `xxxx in (null)` となり検索結果が正しく取得できない可能性があります。

参照: component/libraries/libraries-database.json:s21, processing-pattern/web-application/web-application-getting-started-project-search.json:s1, component/libraries/libraries-database.json:s22

## 参照ナレッジ

- [可変条件を持つSQLを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#可変条件を持つsqlを実行する) (s21)
- [検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-getting-started-project-search.md#検索する) (s1)
- [in句の条件数が可変となるSQLを実行する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#in句の条件数が可変となるsqlを実行する) (s22)
- [SQLをファイルで管理する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#sqlをファイルで管理する) (s12)
- [任意のSQL(SQLファイル)で検索する](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md#任意のsqlsqlファイルで検索する) (s7)
- [実行時のBeanオブジェクトの状態を元にSQL文を動的に構築できる](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/component/libraries/libraries-database.md#実行時のbeanオブジェクトの状態を元にsql文を動的に構築できる) (s6)
- [データベースアクセス](https://github.com/nablarch/nabledge-dev/blob/worktree-check-deepeval-ok-results/.claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-feature-details.md#データベースアクセス) (s3)

## DeepEval判定

| 指標 | 閾値 | スコア | DeepEval判定 | DeepEval根拠 |
|---|---|---|---|---|
| answer_correctness | 0.99 | 1.0 | OK | The Actual Output covers all key facts from the Expected Output: it describes the $if syntax for variable conditions in SQL files, explains that conditions are excluded when property values are null or empty strings (空文字), and provides detailed context. The core facts — $if syntax usage and the null/empty string exclusion behavior — are clearly present and accurately represented. The Actual Output expands significantly beyond the Expected Output but does not contradict any expected facts. |
| answer_relevancy | 0.95 | 1.0 | OK | The score is 1.00 because the response is fully relevant and directly addresses the question about writing dynamic SQL queries that conditionally include search criteria based on user input. No irrelevant statements were found! |
| faithfulness | 0.99 | 0.94 | NG | The score is 0.94 because the actual output incompletely describes the null/empty string exclusion condition. While it correctly states that non-array/Collection types are excluded when the property value is null, it omits that String objects are also excluded when they are empty strings, as specified in the retrieval context. |

## 人手照合

| 指標 | 判定 | 根拠 |
|---|---|---|
| answer_correctness | OK | 参照事実「$if構文で可変条件を記述する。プロパティ値がnullや空文字列の場合に条件が除外される」は回答の「$if(プロパティ名) {SQL条件}」構文説明および除外条件テーブル「String: null または空文字列」に含まれている |
| answer_relevancy | OK | 回答は質問「入力がある項目だけ条件に含める方法」に直接答えており、$if構文の説明・除外条件テーブル・制約・実装例はすべて質問に関連する内容で構成されている。的外れな情報は含まれていない。 |
| faithfulness | OK | DeepEvalはStringの空文字列除外条件が省略されているとしてNGと判定したが、回答の除外条件テーブルには「String: null または空文字列」と明記されており、ナレッジの「上記以外の型の場合は、プロパティ値がnullや空文字列(Stringオブジェクトの場合)」と一致している。回答内容はナレッジと矛盾しておらず、DeepEvalのNG判定は誤りである。 |

### 参照事実（expected_facts）

- $if構文で可変条件を記述する。プロパティ値がnullや空文字列の場合に条件が除外される
