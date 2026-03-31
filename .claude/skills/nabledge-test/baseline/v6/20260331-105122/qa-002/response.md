**結論**: `UniversalDao#per()` と `UniversalDao#page()` メソッドを使用してページング検索を実装します。

**根拠**:

**基本的なAPIの使い方**

`UniversalDao#per` メソッドで1ページあたりの件数、`UniversalDao#page` メソッドでページ番号を指定します。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

ページング表示に必要な件数情報は `Pagination` が保持しており、`EntityList` から取得できます。

```java
Pagination pagination = users.getPagination();
```

**Webアプリケーションでの実装例**

業務アクションでの典型的な実装パターン：

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
    LoginUserPrincipal userContext = SessionUtil.get(context, "userContext");
    searchCondition.setUserId(userContext.getUserId());
    return UniversalDao
            .page(searchCondition.getPageNumber())
            .per(20L)
            .findAllBySqlFile(Project.class, "SEARCH_PROJECT", searchCondition);
}
```

**フォームへのページ番号実装**

検索フォームに `pageNumber` プロパティを追加する必要があります：

```java
public class ProjectSearchForm {
    @Required
    @Domain("pageNumber")
    private String pageNumber;

    public String getPageNumber() { return this.pageNumber; }
    public void setPageNumber(String pageNumber) { this.pageNumber = pageNumber; }
}
```

**JSP（ページング表示）**

`listSearchResult` タグファイルを使用してページングUIを表示します。`searchUri` 属性に現在の検索条件を含むURIを渡します：

```jsp
<c:url value="/action/project/list" var="uri" context="/">
    <c:param name="searchForm.projectName" value="${searchForm.projectName}"/>
</c:url>

<app:listSearchResult resultSetName="searchResult" searchUri="${uri}">
    <jsp:attribute name="headerRowFragment">
        <tr><th>プロジェクトID</th><th>プロジェクト名</th></tr>
    </jsp:attribute>
    <jsp:attribute name="bodyRowFragment">
        <tr>
            <td><n:write name="row.projectId"/></td>
            <td><n:write name="row.projectName"/></td>
        </tr>
    </jsp:attribute>
</app:listSearchResult>
```

**ページング関連クラスの構成**

| クラス名 | 概要 |
|---|---|
| `UniversalDao` | `per()` / `page()` メソッドでページング検索を提供 |
| `ListSearchInfo` | 一覧検索用情報を保持する抽象クラス |
| `Pagination` | `ListSearchInfo` を継承した具象クラス。件数・ページ数を保持 |
| `EntityList` | DAO検索結果のリスト。`Pagination` を内包 |

**注意点**:

- `searchUri` 属性は**必須**です。ページングを表示する場合は必ず指定してください（指定しないとページング遷移が機能しません）
- ページング用の検索処理内部では、件数取得SQLが実行されます。件数取得SQLによる性能劣化が発生した場合は、カスタム件数取得SQLの設定を検討してください
- フォームの `pageNumber` プロパティはページング機能が要求するため、必ず実装してください
- ページング全体は検索結果件数が **1件以上** の場合にのみ表示されます（0件時はヘッダ行のみ表示）

参照:
- `component/libraries/libraries-universal_dao.json#s9`
- `processing-pattern/web-application/web-application-getting-started-project-search.json#s1`
- `guide/biz-samples/biz-samples-03.json#s3`
- `guide/biz-samples/biz-samples-03.json#s2`
