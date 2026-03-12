**結論**: UniversalDaoでページングを実装するには、`UniversalDao.per(件数).page(ページ番号)` メソッドを先に呼び出してから検索メソッドを実行します。

**根拠**:

`UniversalDao#per` と `UniversalDao#page` を使ったページング実装の基本形:

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

ページング表示に必要な件数情報は `Pagination` オブジェクトが保持しており、`EntityList` から取得できます:

```java
Pagination pagination = users.getPagination();
```

Webアプリケーションでの実装例（検索画面）:

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

ページング表示に関連するフレームワーク提供クラスとタグファイルの構成:

| クラス/タグ | 概要 |
|---|---|
| `UniversalDao` | `per()`, `page()` によるページング検索を提供 |
| `ListSearchInfo` | 一覧検索用の情報を保持する抽象クラス |
| `Pagination` | `ListSearchInfo` を継承。件数情報を保持 |
| `EntityList` | 検索結果リストの保持クラス。`getPagination()` で `Pagination` を取得 |
| `listSearchResult` タグ | 検索結果の一覧表示 |
| `listSearchPaging` タグ | ページングUIの出力 |
| `listSearchSubmit` タグ | ページングのサブミット要素の出力 |

**注意点**:

- ページング処理では、範囲指定レコード取得の前に**件数取得SQL**が自動的に発行されます。デフォルトでは元のSQLを `SELECT COUNT(*) FROM` で包んだSQLが使われます。
- `ORDER BY` 句を含むSQLなど処理負荷が大きい場合は、ダイアレクトをカスタマイズして件数取得SQLを変更することで性能を改善できます（`Dialect#convertCountSql` をオーバーライド）。
- 大量データを順次処理する用途（バッチ処理、CSVダウンロードなど）にはページングではなく`UniversalDao.defer()` による**遅延ロード**が適しています。ただし遅延ロード中はトランザクション制御に注意が必要です。

参照: `libraries-universal_dao.json#paging`, `web-application-getting-started-project-search.json#search`, `about-nablarch-03.json#structure`, `libraries-universal_dao.json#customize-count-sql`
