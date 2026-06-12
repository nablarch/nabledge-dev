Step 5-7: 回答を生成し、検証します。

---

**結論**: SQLファイルに `$if(プロパティ名) {条件}` 構文を使い、Beanオブジェクトで条件を渡すことで、入力がある項目だけをWHERE句に含めることができます。`UniversalDao.findAllBySqlFile()` で実行します。

**根拠**:

`$if` 構文のルール：プロパティ値が null または空文字（String の場合）のとき、その条件がSQLから除外されます。配列・Collection の場合は null またはサイズ0のとき除外されます。

**SQLファイル例（Project.sql）**:

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
    AND $if(clientId)               {CLIENT_ID = :clientId}
    AND $if(projectName)            {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectType)            {PROJECT_TYPE = :projectType}
    AND $if(projectClass)           {PROJECT_CLASS IN (:projectClass[])}
    AND $if(projectStartDateBegin)  {PROJECT_START_DATE >= :projectStartDateBegin}
    AND $if(projectStartDateEnd)    {PROJECT_START_DATE <= :projectStartDateEnd}
```

**業務アクション実装例**:

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

private List<Project> searchProject(ProjectSearchDto searchCondition,
                                    ExecutionContext context) {
    return UniversalDao
            .page(searchCondition.getPageNumber())
            .per(20L)
            .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
}
```

- フォームの値は `BeanUtil.createAndCopy()` で検索条件Bean（`ProjectSearchDto`）にコピーします。フォームのプロパティ名と検索条件BeanのプロパティをSQLの名前付きパラメータ（`:projectName` など）に合わせます。
- `UniversalDao.findAllBySqlFile()` の第2引数はSQLID（`SEARCH_PROJECT`）、第3引数に検索条件Beanを渡します。

**注意点**:
- `$if` は **WHERE句のみ** 使用可能です。
- `$if` の中に `$if` をネストすることはできません。
- この機能はユーザー入力で条件が変わる検索画面向けです。「条件が異なるだけの複数SQLを共通化する」目的には使わないでください。無理に共通化すると、SQL変更時に思わぬ不具合を埋め込む原因になります（その場合はSQLを複数定義すること）。

参照: `libraries-database.json:s21`, `web-application-getting-started-project-search.json:s1`, `libraries-universal-dao.json:s10`

---