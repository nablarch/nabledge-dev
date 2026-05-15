**結論**: `$if(プロパティ名) {SQL条件}` 構文を使うことで、入力された項目だけをWHERE句に含める動的SQLを記述できます。

**根拠**:

Nablarchのデータベースアクセス機能（`ParameterizedSqlPStatement` または UniversalDAO）では、SQLファイルに `$if` 構文を使って可変条件を定義できます。

**基本ルール**
- `$if(プロパティ名) {SQL条件}` の形式で記述
- 対応するBeanプロパティが **null・空文字列（String）・サイズ0（配列/Collection）** の場合、その条件はSQLから除外される
- 使用できる箇所は **WHERE句のみ**（`$if` のネストも不可）

**SQLの例**（検索画面）:
```sql
SEARCH_PROJECT =
SELECT PROJECT_ID, PROJECT_NAME, PROJECT_TYPE
FROM PROJECT
WHERE
    USER_ID = :userId
    AND $if(projectName)  {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType)  {PROJECT_TYPE = :projectType}
    AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

`projectName` だけ入力されていた場合、`projectType` などの条件は自動的に除外されます。

**Javaの実装例**（UniversalDAO使用）:
```java
// 検索条件Beanに入力値をセット
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// SQLIDを指定して検索（条件Beanの状態でSQLが動的に組み立てられる）
List<Project> results = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", searchCondition);
```

**IN句を可変にする場合**: 末尾に `[]` を付け、`$if` と組み合わせる。
```sql
AND $if(projectClass) {PROJECT_CLASS IN (:projectClass[])}
```
プロパティの型は配列または `java.util.Collection` にする必要があります。

**注意点**:
- `$if` はWHERE句のみで使用可能
- この機能は「ユーザー入力で条件が変わる検索画面」向けの機能であり、「条件が異なる複数のSQLを1つに共通化する」目的で使うべきではない（安易な共通化は不具合の原因になる）
- IN句のプロパティがnullになりうる場合は必ず `$if` と組み合わせること（`$if` なしでnullを渡すと `IN (null)` になり正しく検索できない）
- 検索条件BeanのプロパティはBeanUtilでMapに変換されるため、BeanUtilがサポートしていない型は使用不可

参照: `component/libraries/libraries-database.json#s21`, `component/libraries/libraries-database.json#s22`, `processing-pattern/web-application/web-application-getting-started-project-search.json#s1`