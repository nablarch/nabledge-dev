**結論**: `$if(プロパティ名) {SQL条件}` 構文を使って SQLファイルに可変条件を記述することで、入力のある項目だけをWHERE句に含める動的SQLを実現できる。

**根拠**:

SQLファイルに `$if` 構文で可変条件を記述する。プロパティが null または空文字列（String型）の場合、その条件が自動的に除外される。

```sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID,
    PROJECT_NAME,
    PROJECT_TYPE,
    PROJECT_CLASS,
    PROJECT_START_DATE,
    PROJECT_END_DATE,
    VERSION
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

業務アクションでは、フォームの値を検索条件Beanにコピーし、`UniversalDao#findAllBySqlFile` に渡して実行する。

```java
@InjectForm(form = ProjectSearchForm.class, prefix = "searchForm", name = "searchForm")
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse list(HttpRequest request, ExecutionContext context) {
    ProjectSearchForm searchForm = context.getRequestScopedVar("searchForm");
    ProjectSearchDto searchCondition =
            BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);
    List<Project> searchList = searchProject(searchCondition, context);
    context.setRequestScopedVar("searchResult", searchList);
    return new HttpResponse("/WEB-INF/view/project/index.jsp");
}

private List<Project> searchProject(ProjectSearchDto searchCondition, ExecutionContext context) {
    LoginUserPrincipal userContext = SessionUtil.get(context, "userContext");
    searchCondition.setUserId(userContext.getUserId());
    return UniversalDao
            .page(searchCondition.getPageNumber())
            .per(20L)
            .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
}
```

`$if` 構文の条件除外ルール:
- `配列/Collection` 型: プロパティ値が null またはサイズ0のとき除外
- それ以外の型（String含む）: プロパティ値が null または空文字列のとき除外

制約:
- 使用できる箇所はwhere句のみ
- `$if` の入れ子は不可

**注意点**: `$if` はウェブアプリケーションの検索画面のように入力内容によって条件が変わる場合に使うもの。条件だけ異なる複数のSQLを共通化するために使ってはならない（安易な共通化は不具合の原因となる）。

参照: libraries-database.json:s21, web-application-getting-started-project-search.json:s1

---