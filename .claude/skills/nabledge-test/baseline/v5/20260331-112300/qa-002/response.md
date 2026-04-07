**結論**: `UniversalDao#per` メソッドと `UniversalDao#page` メソッドを先に呼び出してから検索メソッドを実行することでページング検索を実装できます。

**根拠**:

#### 基本的な使い方

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
Pagination pagination = users.getPagination();
```

- `per(件数)` : 1ページあたりの件数を指定
- `page(ページ番号)` : 取得するページ番号を指定（1始まり）
- `EntityList` から `getPagination()` で `Pagination` オブジェクトを取得でき、総件数・総ページ数などのページング情報を利用できます

#### Webアプリケーションでの実装例（業務アクション）

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

フォームには `pageNumber` プロパティが必要です：

```java
public class ProjectSearchForm {
  @Required
  @Domain("pageNumber")
  private String pageNumber;
  public String getPageNumber(){ return this.pageNumber; }
  public void setPageNumber(String pageNumber){ this.pageNumber = pageNumber; }
}
```

#### 関連クラス構成

| クラス名 | 概要 |
|---|---|
| `UniversalDao` | ページング検索を提供するDAOクラス。`per()`・`page()` メソッドを先に呼び出す |
| `ListSearchInfo` | 一覧検索用情報を保持する抽象クラス |
| `Pagination` | `ListSearchInfo` を継承した具象クラス。ページング情報を保持 |
| `EntityList` | 検索結果リストの保持クラス。`getPagination()` でページング情報を取得可能 |

**注意点**:

- ページング実行時は、実際の範囲指定レコード取得の前に件数取得SQLが自動で発行されます。`ORDER BY` 句を含む高負荷SQLで性能劣化が発生した場合は、`Dialect#convertCountSql` をオーバーライドして件数取得SQLをカスタマイズできます。
- 大量データを扱う場合（ダウンロード等）はページングの代わりに `UniversalDao#defer` による遅延ロードの利用も検討してください。ただし、遅延ロード中のトランザクション制御でカーソルがクローズされる場合があるため、そのような場合はページングで対処します。

参照: `libraries-universal_dao.json#s9`, `web-application-getting-started-project-search.json#s1`, `biz-samples-03.json#s3`, `libraries-universal_dao.json#s4`