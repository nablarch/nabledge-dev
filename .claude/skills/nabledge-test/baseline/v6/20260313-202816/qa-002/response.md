**結論**: `UniversalDao#per()` と `UniversalDao#page()` を使用してページング検索を実装できます。検索フォームに `pageNumber` プロパティを設け、`listSearchResult` タグファイルと組み合わせることで画面表示まで実現できます。

**根拠**:

**1. UniversalDao でのページング呼び出し方法**

`UniversalDao#per()` でページサイズを、`UniversalDao#page()` でページ番号を指定してから検索メソッドを呼び出します。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

ページング情報（総件数・総ページ数など）は `EntityList` から `Pagination` として取得できます。

```java
Pagination pagination = users.getPagination();
```

（参照: `libraries-universal_dao.json#s9`）

**2. 業務アクションでの実装例**

```java
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

（参照: `web-application-getting-started-project-search.json#s1`）

**3. 検索フォームに pageNumber を追加する**

ページング機能を使用するには、検索フォームに `pageNumber` プロパティが必要です。

```java
public class ProjectSearchForm {
    @Required
    @Domain("pageNumber")
    private String pageNumber;

    public String getPageNumber() { return this.pageNumber; }
    public void setPageNumber(String pageNumber) { this.pageNumber = pageNumber; }
}
```

（参照: `biz-samples-03.json#s2`）

**4. JSP でのページング表示**

`listSearchResult` タグファイルを使用して検索結果とページングを表示します。`searchUri` には現在の検索条件を含む URI を指定します。

```jsp
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<%@ taglib prefix="app" tagdir="/WEB-INF/tags/listSearchResult" %>

<c:url value="/action/project/list" var="uri" context="/">
    <c:param name="searchForm.projectName" value="${searchForm.projectName}"/>
</c:url>

<app:listSearchResult resultSetName="searchResult" searchUri="${uri}">
    <jsp:attribute name="headerRowFragment">
        <tr><th>プロジェクトID</th><th>プロジェクト名</th></tr>
    </jsp:attribute>
    <jsp:attribute name="bodyRowFragment">
        <tr><td><n:write name="row.projectId"/></td>
            <td><n:write name="row.projectName"/></td></tr>
    </jsp:attribute>
</app:listSearchResult>
```

`listSearchResult` タグファイルは `META-INF/tags/listSearchResult` から業務アプリケーションの `/WEB-INF/tags` にコピーして使用します。

（参照: `biz-samples-03.json#s2`, `biz-samples-03.json#s3`, `biz-samples-03.json#s4`）

**注意点**:

- `searchUri` 属性はページングを表示する場合に必須です。指定しないとページング遷移時に検索条件が失われます。
- `listSearchResult` タグの `usePaging` 属性はデフォルト `true` です。ページングを非表示にする場合は `false` を指定します。
- ページング用の検索処理は内部的に件数取得 SQL が発行されます。件数取得 SQL で性能劣化が発生した場合はカスタマイズが必要です（`libraries-universal_dao.json#s9` 補足参照）。
- `varStatusName` で指定した変数に `n:write` タグでアクセスする場合はエラーが発生するため、`n:set` タグを介してアクセスすること（`biz-samples-03.json#s3` 参照）。
- ページング表示は検索結果件数が **1件以上** の場合のみ表示されます。

参照: `libraries-universal_dao.json#s9`, `web-application-getting-started-project-search.json#s1`, `biz-samples-03.json#s2`, `biz-samples-03.json#s3`, `biz-samples-03.json#s4`, `biz-samples-03.json#s5`
