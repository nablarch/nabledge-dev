**結論**: SQLファイル内で `$if(プロパティ名) {SQL文の条件}` 構文を使うことで、Beanのプロパティが null や空文字の場合にその条件を自動的に除外できます。

**根拠**:

#### 1. SQLファイルに `$if` 構文で可変条件を記述する

```sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    PROJECT_START_DATE
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName)           {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType)           {PROJECT_TYPE = :projectType}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectStartDateEnd)   {PROJECT_START_DATE <= :projectStartDateEnd}
```

除外される条件:
- 通常型（String等）: プロパティ値が `null` または空文字列の場合
- 配列・`Collection` 型: プロパティ値が `null` またはサイズ0の場合

#### 2. 検索条件 Bean を作成する

```java
public class ProjectSearchDto implements Serializable {
    private String projectName;
    private java.sql.Date projectStartDateBegin;
    private java.sql.Date projectStartDateEnd;
    // ゲッタ・セッタは省略
}
```

#### 3-A. UniversalDAO を使う場合（推奨）

```java
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

List<Project> result = UniversalDao
    .page(searchCondition.getPageNumber())
    .per(20L)
    .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

#### 3-B. JDBCラッパー（`DbConnectionContext`）を使う場合

```java
AppDbConnection connection = DbConnectionContext.getConnection();

// 第2引数に条件 Bean を渡すことで $if の判定が行われる
ParameterizedSqlPStatement statement =
    connection.prepareParameterizedSqlStatementBySqlId(
        "jp.co.example.ProjectAction#SEARCH_PROJECT", searchCondition);

SqlResultSet result = statement.retrieve(searchCondition);
```

> **重要**: `prepareParameterizedSqlStatementBySqlId` の **第2引数** に条件 Bean を渡すことで、その Bean の状態を元に `$if` の条件が組み立てられます。

**注意点**:
- `$if` はwhere句のみで使用可能です。`$if` の中に `$if` はネストできません。
- この機能は「ユーザの入力によって検索条件が変わる」用途向けです。条件だけ異なる複数のSQLを共通化するために使用するものではなく、機能ごとにSQLを定義してください。
- in句を可変にしたい場合は `$if(userKbn) {user_kbn in (:userKbn[])}` のように `[]` を末尾に付けます。

参照: libraries-database.json:s21, web-application-getting-started-project-search.json:s1, libraries-database.json:s16, libraries-universal-dao.json:s10