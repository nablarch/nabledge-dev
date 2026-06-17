**結論**: `UniversalDao.findAllBySqlFile()` メソッドにSQLファイルのSQL IDを指定して検索します。条件指定・ページング・大量データの遅延ロードと3つのパターンがあります。

**根拠**:

**1. 基本的な条件指定検索**

SQLファイル（例: `Project.sql`）にSQL IDを定義し、検索条件Beanを渡します。

```sql
-- Project.sql
SEARCH_PROJECT =
SELECT
    PROJECT_ID, PROJECT_NAME, PROJECT_START_DATE
FROM
    PROJECT
WHERE
    $if(projectName) {PROJECT_NAME LIKE :%projectName%}
    AND $if(projectStartDateBegin) {PROJECT_START_DATE >= :projectStartDateBegin}
```

```java
// 検索条件Beanを用意（カラム型に合わせた型で定義）
ProjectSearchDto condition = BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

// findAllBySqlFile の第2引数にSQL IDを指定
List<Project> projects = UniversalDao.findAllBySqlFile(
    Project.class, "SEARCH_PROJECT", condition);
```

**2. ページング付き検索**

```java
EntityList<Project> projects = UniversalDao
        .page(searchCondition.getPageNumber())
        .per(20L)
        .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);

// ページネーション情報の取得
Pagination pagination = projects.getPagination();
```

**3. 大量データの遅延ロード**

```java
// defer() を先に呼び出し、try-with-resources で close する
try (DeferredEntityList<User> users
        = (DeferredEntityList<User>) UniversalDao.defer()
                                        .findAllBySqlFile(User.class, "FIND_BY_NAME")) {
    for (User user : users) {
        // 1件ずつ処理
    }
}
```

**4. 業務アクションでの実装例（ウェブアプリケーション）**

```java
@InjectForm(form = ProjectSearchForm.class, prefix = "searchForm", name = "searchForm")
@OnError(type = ApplicationException.class, path = "/WEB-INF/view/project/index.jsp")
public HttpResponse list(HttpRequest request, ExecutionContext context) {
    ProjectSearchForm searchForm = context.getRequestScopedVar("searchForm");
    ProjectSearchDto searchCondition =
            BeanUtil.createAndCopy(ProjectSearchDto.class, searchForm);

    EntityList<Project> searchList = UniversalDao
            .page(searchCondition.getPageNumber())
            .per(20L)
            .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);

    context.setRequestScopedVar("searchResult", searchList);
    return new HttpResponse("/WEB-INF/view/project/index.jsp");
}
```

**注意点**:
- 検索条件BeanのプロパティはSQLのカラム型と互換性のある型（`java.sql.Date` 等）で定義すること
- 遅延ロード（`defer()`）使用時は必ず `DeferredEntityList#close` を呼び出すこと（try-with-resources 推奨）
- `batchUpdate` では楽観的ロックは使用できない

参照: libraries-universal-dao.json:s7, libraries-universal-dao.json:s10, libraries-universal-dao.json:s12, libraries-universal-dao.json:s9, web-application-getting-started-project-search.json:s1