**結論**: UniversalDaoでページング検索を実装するには、検索前に `UniversalDao#per(1ページの件数)` と `UniversalDao#page(ページ番号)` を呼び出してから `findAllBySqlFile` 等の検索メソッドを実行する。検索結果は `EntityList` として返され、画面表示に必要な件数等の情報は `EntityList#getPagination()` で取得する `Pagination` が保持する。

**根拠**:

基本的な実装例（`UniversalDao.per().page()` の呼び出し）:

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
Pagination pagination = users.getPagination();
```

業務アクションでの実装例（ProjectAction）:

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

画面側（JSP）では `<app:listSearchResult>` タグを使うことで、検索結果件数・ページング・検索結果表をまとめて出力できる。ページング機能を使用する場合、検索フォームは `pageNumber` という名前でページ番号を受け取るように実装する:

```java
public class ProjectSearchForm {
  @Required
  @Domain("pageNumber")
  private String pageNumber;
  // getter/setter
}
```

関連する主要クラス:
- `UniversalDao` — 汎用DAO機能を提供
- `ListSearchInfo` — 一覧検索用の情報を保持する抽象クラス
- `Pagination` — `ListSearchInfo` を継承した具象クラス
- `EntityList` — ユニバーサルDAOの結果リスト保持クラス

ページング時の検索条件は、検索条件をパラメータにセットしたURIを組み立て、`<app:listSearchResult>` の `searchUri` 属性に渡すことで維持できる。

**注意点**:

- ページングでは、実際の範囲指定レコード取得処理の前に **件数取得SQL** が発行される（デフォルトは元のSQLを `SELECT COUNT(*) FROM` で包んだSQL）。`ORDER BY` を含むなど負荷が大きいSQLの場合、性能劣化が発生することがある。必要に応じて Dialect をカスタマイズし `Dialect#convertCountSql` を変更して件数取得SQLを差し替える。その際、件数取得SQLは元のSQLと同一の検索条件を持つ必要がある。
- 大量データのダウンロードやバッチ処理など、結果をメモリに展開できないケースでは、ページングではなく `UniversalDao#defer()` による遅延ロード（`DeferredEntityList` を try-with-resources でクローズ）を検討する。
- 検索条件Beanのプロパティ名は、フォームと合わせること（`BeanUtil` でコピーするため）。

参照: `component/libraries/libraries-universal-dao.json#s12`, `component/libraries/libraries-universal-dao.json#s23`, `processing-pattern/web-application/web-application-getting-started-project-search.json#s1`, `guide/biz-samples/biz-samples-03.json#s5`, `guide/biz-samples/biz-samples-03.json#s13`
