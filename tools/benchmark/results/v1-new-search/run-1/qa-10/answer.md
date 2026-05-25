**結論**: SQLファイルに `$if(プロパティ名) {SQL文の条件}` 構文を使用することで、Beanのプロパティ値がnullまたは空文字の場合にその条件を自動除外できる。

**根拠**:

SQLファイルに以下のように可変条件を記述する（Exampleアプリケーションの検索SQL例）:

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
    AND $if(clientId)             {CLIENT_ID = :clientId}
    AND $if(projectName)          {PROJECT_NAME LIKE  :%projectName%}
    AND $if(projectType)          {PROJECT_TYPE = :projectType}
    AND $if(projectClass)         {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin){PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectStartDateEnd)  {PROJECT_START_DATE <= :projectStartDateEnd}
```

除外される条件:
- 配列や `java.util.Collection` の場合: プロパティ値がnullまたはサイズ0
- その他の型の場合: プロパティ値がnullまたは空文字列（Stringの場合）

業務アクションでの実装例:

```java
@InjectForm(form = ProjectSearchForm.class, prefix = "searchForm", name = "searchForm")
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse list(HttpRequest request, ExecutionContext context) {

    ProjectSearchForm searchForm = context.getRequestScopedVar("searchForm");
    ProjectSearchDto searchCondition =
            BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

    List<Project> searchList = UniversalDao
            .page(searchCondition.getPageNumber())
            .per(20L)
            .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
    context.setRequestScopedVar("searchResult", searchList);

    return new HttpResponse("/WEB-INF/view/project/index.jsp");
}
```

**注意点**:
- `$if` が使用できるのは `where句のみ`。`$if` の中に `$if` を記述することはできない。
- 条件だけが異なる複数のSQLを共通化する目的では使用しないこと。安易に共通化すると、SQL変更時に意図しない不具合を埋め込む原因になる。

参照: libraries-database.json:s21, web-application-getting-started-project-search.json:s1

---