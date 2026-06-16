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