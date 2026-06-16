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