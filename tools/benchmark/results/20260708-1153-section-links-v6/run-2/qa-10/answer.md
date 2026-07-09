**結論**: SQLファイル内の `$if(プロパティ名) {SQL条件}` 構文を使うと、対応するBeanのプロパティ値がnullまたは空文字の場合に、その条件を自動的に除外できる。

**根拠**:

**`$if` 構文のルール**

```sql
-- Project.sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    PROJECT_TYPE
FROM
    PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType) {PROJECT_TYPE = :projectType}
    AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
```

- `$if(プロパティ名)` に対応するBeanのプロパティが **null** または **空文字列** → その条件を除外
- 配列・`Collection` 型の場合は **null** または **サイズ0** → 除外
- `$if` 内に `$if` はネスト不可、where句のみで使用可

**ユニバーサルDAOを使った実装例**

```java
// 検索条件Beanを作成（未入力項目はnullまたは空文字のまま）
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);
searchCondition.setUserId(userContext.getUserId());

// SQLIDを指定してBeanを条件として検索
List<Project> result = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", searchCondition);
```

**JDBCラッパーを直接使う場合**

```java
UserEntity entity = new UserEntity();
entity.setUserName("なまえ"); // userKbnはnullのままにすると条件から除外される

AppDbConnection connection = DbConnectionContext.getConnection();
ParameterizedSqlPStatement statement = connection.prepareParameterizedSqlStatementBySqlId(
    "jp.co.tis.sample.action.SampleAction#searchUser", entity);

SqlResultSet result = statement.retrieve(entity);
```

**注意点**:
- `$if` は「ユーザー入力によって条件が変わる検索」向けの機能。条件が異なる複数のSQLを共通化する目的で使うのは誤用で、安易な共通化はSQL変更時に不具合の原因になる
- in句で条件が可変になる場合は `$if` と `:propertyName[]` を組み合わせる（`$if(userKbn) {USER_KBN IN (:userKbn[])}`）
- 検索条件BeanのプロパティはBeanUtil経由でMapに変換されるため、BeanUtilが対応していない型は使用できない

参照:
- データベースアクセス(JDBCラッパー)
  .claude/skills/nabledge-6/docs/component/libraries/libraries-database.md
  実行時のBeanオブジェクトの状態を元にSQL文を動的に構築できる
  可変条件を持つSQLを実行する
  in句の条件数が可変となるSQLを実行する
  Beanオブジェクトを入力としてSQLを実行する
- 検索機能の作成
  .claude/skills/nabledge-6/docs/processing-pattern/web-application/web-application-getting-started-project-search.md
  検索する
- ユニバーサルDAO
  .claude/skills/nabledge-6/docs/component/libraries/libraries-universal-dao.md
  条件を指定して検索する
  任意のSQL(SQLファイル)で検索する