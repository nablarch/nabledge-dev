**結論**: `$if(プロパティ名) {SQL条件}` 構文をSQLファイルに記述し、Beanオブジェクトのプロパティ値が null または空文字の場合にその条件を自動で除外できます。ウェブアプリの検索画面のような可変条件SQLに対応する専用機能です。

**根拠**:

SQLファイルに `$if` 構文で可変条件を記述します:

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
    AND $if(clientId)              {CLIENT_ID = :clientId}
    AND $if(projectName)           {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType)           {PROJECT_TYPE = :projectType}
    AND $if(projectClass)          {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectEndDateEnd)     {PROJECT_END_DATE <= :projectEndDateEnd}
```

除外条件は以下の通りです:
- `String` 型: `null` または空文字列の場合に除外
- `Collection` / 配列型: `null` またはサイズ0の場合に除外

業務アクションでは、フォームの値を検索条件Beanにコピーして `UniversalDao.findAllBySqlFile` に渡します:

```java
@InjectForm(form = ProjectSearchForm.class, prefix = "searchForm", name = "searchForm")
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse list(HttpRequest request, ExecutionContext context) {

    ProjectSearchForm searchForm = context.getRequestScopedVar("searchForm");
    // フォームの値を検索条件Beanにコピー
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
- `$if` が使えるのは `WHERE` 句のみ。ネスト（`$if` 内に `$if`）は不可。
- IN句のプロパティがnullやサイズ0になり得る場合は、`$if` と `[]` を併用すること。例: `$if(userKbn) {user_kbn IN (:userKbn[])}`
- この構文は「ユーザー入力によって条件が変わる検索画面」向けのものです。複数SQLの共通化を目的に使用すると、変更時に思わぬ不具合を招く可能性があります。

参照: `component/libraries/libraries-database.json:s21`, `component/libraries/libraries-database.json:s22`, `processing-pattern/web-application/web-application-getting-started-project-search.json:s1`, `component/libraries/libraries-universal-dao.json:s10`