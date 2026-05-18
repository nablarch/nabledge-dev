**結論**: 入力がある項目だけ条件に含める動的SQLは、`$if` 構文を使って実現できます。

**根拠**:

`$if(プロパティ名) {SQL条件}` の形式でWHERE句に記述します。対応するBeanのプロパティが `null` または空文字列（String型の場合）のとき、その条件は自動的に除外されます。

**SQLの例**（`user_name` と `user_kbn` が可変条件）:

```sql
SELECT
  user_id,
  user_name,
  user_kbn
FROM
  user
WHERE
  $if (userName) {user_name LIKE :userName%}
  AND $if (userKbn) {user_kbn IN ('1', '2')}
  AND birthday = :birthday
```

`userName` プロパティのみに値が設定されている場合、`user_kbn` の条件は除外されます。

**Javaの実装例**:

```java
UserEntity entity = new UserEntity();
entity.setUserName("なまえ"); // userKbnはnullのまま

AppDbConnection connection = DbConnectionContext.getConnection();

ParameterizedSqlPStatement statement =
    connection.prepareParameterizedSqlStatementBySqlId(
        "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

**複数条件の実用例**（Webアプリの検索画面）:

```sql
SEARCH_PROJECT =
SELECT PROJECT_ID, PROJECT_NAME, ...
FROM PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType) {PROJECT_TYPE = :projectType}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectEndDateBegin) {PROJECT_END_DATE >= :projectEndDateBegin}
```

UniversalDAOで実行する場合:

```java
List<Project> results = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", searchCondition);
```

**注意点**:

- `$if` は **WHERE句内でのみ** 使用可能です（SELECT句・ORDER BY句では使えません）
- `$if` の中に `$if` をネストすることはできません
- IN句で `$if` と組み合わせる場合は `:プロパティ名[]` の形式でパラメータを記述します
  ```sql
  $if (userKbn) {user_kbn IN (:userKbn[])}
  ```
  配列または `java.util.Collection` 型のプロパティが `null` またはサイズ0のときに条件が除外されます
- この機能は **検索画面のように入力内容によって条件が変わる場合** に使うものです。複数のSQLを `$if` で共通化する目的には使用しないでください（保守時に予期しない不具合の原因になります）

参照: `component/libraries/libraries-database.json#s21`, `processing-pattern/web-application/web-application-getting-started-project-search.json#s1`, `component/libraries/libraries-database.json#s22`