**結論**: `UniversalDao#per()` と `UniversalDao#page()` をチェーンして呼び出した後に検索メソッドを実行することでページング検索を実装できます。

**根拠**:

**1. 基本的なAPIの使い方**

`UniversalDao#per(件数)` で1ページあたりの表示件数を、`UniversalDao#page(ページ番号)` で取得するページ番号を指定します。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

ページング表示に必要な件数情報は `Pagination` が保持しており、`EntityList` から取得できます：

```java
Pagination pagination = users.getPagination();
```

**2. 実装例（Webアプリケーション）**

フォームには `pageNumber` プロパティを定義します：

```java
public class ProjectSearchForm extends SearchFormBase implements Serializable {
    @Required
    @Domain("pageNumber")
    private String pageNumber;

    public String getPageNumber() { return this.pageNumber; }
    public void setPageNumber(String pageNumber) { this.pageNumber = pageNumber; }
    // その他の検索条件プロパティ...
}
```

業務アクションでは `searchCondition.getPageNumber()` を使用してページ番号を渡します：

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

**3. JSP（検索結果とページングの表示）**

`listSearchResult` タグファイルを使用することでページング付きの一覧表示を実現できます。`searchUri` 属性には検索条件をパラメータにセットしたURIを渡します：