**結論**: `$if(プロパティ名) {SQL条件}` という特殊構文を使ってSQLファイルに可変条件を記述することで、入力がある項目だけをWHERE句に含めることができます。この機能はNablarchのデータベースアクセス(JDBCラッパー)が提供しています。

**根拠**:

**SQLファイルでの記述方法**

```sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType) {PROJECT_TYPE = :projectType}
    AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

- `$if(プロパティ名) { ... }` で囲んだ条件は、対応するBeanプロパティが **null または空文字** の場合に除外されます
- `in (:プロパティ名[])` の形式を使うと、配列/Collectionのサイズに応じて条件数が可変になります
- `$if` は **WHERE句内でのみ** 使用可能です（ネストは不可）

**Javaの実装例 (UniversalDAOを使う場合)**

```java
// フォームから検索条件Beanにコピー
ProjectSearchDto searchCondition =
        BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// SQL IDを指定して検索（$ifによる可変条件が適用される）
List<Project> result = UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

**JDBCラッパーを直接使う場合の実装例**

```java
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");  // userKbnはnullのまま → 条件から除外される

AppDbConnection connection = DbConnectionContext.getConnection();
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

**注意点**:
- この機能は検索画面のように「ユーザ入力によって条件が変わる」ケース専用です。「条件だけ異なる複数のSQLを共通化する」目的には使わないでください。安易な共通化は思わぬ不具合の原因になります
- `$if` 内のプロパティが配列や`Collection`でnull/サイズ0の場合も条件が除外されます

参照: `component/libraries/libraries-database.json:s21`, `component/libraries/libraries-database.json:s22`, `processing-pattern/web-application/web-application-getting-started-project-search.json:s1`