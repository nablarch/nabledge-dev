**結論**: `UniversalDao#per` メソッドと `UniversalDao#page` メソッドを検索メソッドの前に呼び出すだけでページング検索を実装できます。

**根拠**:

**基本的な使い方**

`UniversalDao.per(件数).page(ページ番号)` の順でメソッドチェーンし、`findAllBySqlFile` などの検索メソッドを呼び出します。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
Pagination pagination = users.getPagination();
```

- `per(n)` — 1ページあたりの件数を指定
- `page(n)` — 取得するページ番号を指定（1始まり）
- 戻り値は `EntityList<T>`。`EntityList#getPagination()` で `Pagination` オブジェクトを取得でき、総件数・総ページ数などのページング表示情報を参照できます。

**Webアプリケーションでの実装例（プロジェクト検索）**

業務アクションでページング検索を行う実装例は以下の通りです。フォームからページ番号を受け取り、`UniversalDao.page().per()` に渡します。

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

フォームクラスには `pageNumber` プロパティを用意します（`listSearchResult` タグを使用する場合は必須）。

```java
public class ProjectSearchForm {
    @Required
    @Domain("pageNumber")
    private String pageNumber;
    public String getPageNumber(){ return this.pageNumber; }
    public void setPageNumber(String pageNumber){ this.pageNumber = pageNumber; }
}
```

**注意点**:

- ページング実行時、実際の範囲取得の前に **件数取得SQL** が自動発行されます。デフォルトでは元のSQLを `SELECT COUNT(*) FROM` で包んだSQLが使用されます。`ORDER BY` 句を含む高負荷SQLで性能劣化が発生した場合は、`Dialect#convertCountSql` をカスタマイズして件数取得SQLを変更できます。
- `listSearchResult` タグを使ってページングを表示する場合、フォームに `pageNumber` という名前でページ番号を受け取るプロパティが必要です。
- ページング全体は検索結果件数が1件以上の場合のみ表示されます。

参照: `component/libraries/libraries-universal_dao.json#s9`, `processing-pattern/web-application/web-application-getting-started-project-search.json#s1`, `guide/biz-samples/biz-samples-03.json#s3`, `guide/biz-samples/biz-samples-03.json#s1`
