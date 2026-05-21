**結論**: `$if(プロパティ名) {SQL条件}` 構文をSQLファイルに記述することで、Beanのプロパティ値がnullまたは空文字の場合にその条件を自動的に除外できます。

**根拠**:

`$if` 構文のルール:
- `$if(プロパティ名) {SQL文の条件}` の形式で記述する
- プロパティ値がnullや空文字（String型）の場合、条件がSQL文から除外される
- 配列・`java.util.Collection` の場合、nullまたはサイズ0の場合に除外される
- 使用できる箇所はwhere句のみ（`$if` のネストは不可）

実際の検索機能のSQLサンプル（Exampleアプリの `Project.sql`）:
```sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    ...
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(clientId)              {CLIENT_ID = :clientId}
    AND $if(projectName)           {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType)           {PROJECT_TYPE = :projectType}
    AND $if(projectClass)          {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectStartDateEnd)   {PROJECT_START_DATE <= :projectStartDateEnd}
```

Java側の実装（JDBCラッパー直接使用の場合）:
```java
// Beanを生成してプロパティに値を設定（入力があった項目のみ設定）
UserEntity entity = new UserEntity();
entity.setUserName("なまえ");
// userKbn は未入力のため設定しない → SQL条件から除外される

AppDbConnection connection = DbConnectionContext.getConnection();

// Beanオブジェクトを第2引数に渡すことで可変条件を組み立てる
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

UniversalDAO使用の場合:
```java
// フォームの値を検索条件BeanにBeanUtilでコピー
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// UniversalDaoでSQLIDを指定して検索
return UniversalDao
    .page(searchCondition.getPageNumber())
    .per(20L)
    .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
```

in句の条件を可変にしたい場合は、名前付きパラメータの末尾に `[]` を付加します:
```sql
AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
```

**注意点**:
- `$if` は「条件だけが異なる複数のSQLの共通化」目的では使わないこと。SQL変更時に意図しない不具合を埋め込む原因となるため、その場合はSQLを複数定義する。
- in句でプロパティ値がnullまたはサイズ0になる可能性がある場合は、必ず `$if` と組み合わせること（そうしないと `IN (null)` となり正しく検索できない）。

参照: `component/libraries/libraries-database.json:s21`, `component/libraries/libraries-database.json:s22`, `processing-pattern/web-application/web-application-getting-started-project-search.json:s1`

---