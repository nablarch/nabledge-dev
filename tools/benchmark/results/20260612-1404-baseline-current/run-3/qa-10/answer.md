**結論**: SQLファイルで `$if(プロパティ名) {SQL条件}` 構文を使い、Beanのプロパティがnullまたは空文字列のときに該当条件を自動的に除外する。実行は `UniversalDao.findAllBySqlFile` に条件Beanを渡す。

**根拠**:

SQLファイルに以下のように `$if` 構文で可変条件を記述する。

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
    AND $if(clientId)               {CLIENT_ID = :clientId}
    AND $if(projectName)            {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType)            {PROJECT_TYPE = :projectType}
    AND $if(projectClass)           {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin)  {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectStartDateEnd)    {PROJECT_START_DATE <= :projectStartDateEnd}
```

各 `$if` に対応するBeanプロパティが null または空文字列（String型の場合）のとき、その条件はWHERE句から除外される。配列・`Collection`型の場合はnullかサイズ0のときに除外される。

業務アクションでは、条件BeanをUniversalDaoに渡すだけでよい。

```java
private List<Project> searchProject(ProjectSearchDto searchCondition, ExecutionContext context) {
    LoginUserPrincipal userContext = SessionUtil.get(context, "userContext");
    searchCondition.setUserId(userContext.getUserId());

    return UniversalDao
            .page(searchCondition.getPageNumber())
            .per(20L)
            .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
}
```

フォームから条件BeanへはBeanUtilでコピーする。

```java
ProjectSearchForm searchForm = context.getRequestScopedVar("searchForm");
ProjectSearchDto searchCondition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);
```

**注意点**:
- `$if` はwhere句のみ使用可能。`$if` の中に `$if` はネストできない
- in句に可変条件を使う場合は `:projectClass[]` のようにパラメータ末尾に `[]` を付け、対応するプロパティを配列または`Collection`型にする。プロパティ値がnullまたはサイズ0のときに条件が除外されるよう、必ず `$if` と組み合わせること（`$if` なしでnullを渡すと `IN (null)` になり正しく検索できない）
- この機能は検索画面のような「ユーザー入力によって条件が変わる」ケースに使うもの。条件だけ異なる複数のSQLを無理に共通化するために使ってはならない

参照: component/libraries/libraries-database.json:s21, processing-pattern/web-application/web-application-getting-started-project-search.json:s1, component/libraries/libraries-universal-dao.json:s10, component/libraries/libraries-database.json:s22