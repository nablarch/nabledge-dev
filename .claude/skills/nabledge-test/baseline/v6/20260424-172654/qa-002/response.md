**結論**: UniversalDaoでページング検索を実装するには、検索時に `UniversalDao#per(件数)` メソッドと `UniversalDao#page(ページ番号)` メソッドを先に呼び出してから `findAllBySqlFile` を実行します。ページング表示に必要な検索結果件数などの情報は、返却された `EntityList` から `getPagination()` で取得できる `Pagination` が保持しています。

**根拠**:

基本的な使い方（`universal-dao.json#s12`）：

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");

// ページング情報（総件数など）を取得
Pagination pagination = users.getPagination();
```

業務アクションでの実装例（`web-application-getting-started-project-search.json#s1`）：

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

関連するフレームワーククラス（`biz-samples-03.json#s5`）：
- `UniversalDao`：汎用的なDAO機能を提供
- `ListSearchInfo`：一覧検索用の情報を保持する抽象クラス
- `Pagination`：`ListSearchInfo` を継承した具象クラス（検索結果件数等を保持）
- `EntityList`：UniversalDaoから返される結果リストの保持クラス

JSPでは `listSearchResult` / `listSearchPaging` / `listSearchSubmit` タグを使って検索結果とページングを表示します。

**注意点**:
- ページングでは、実際の範囲指定レコードの取得処理の前に、件数取得SQLが発行されます（元のSQLを `SELECT COUNT(*) FROM` で包んだSQL）。`ORDER BY` 句などで性能劣化が発生する場合は、ダイアレクトをカスタマイズし `Dialect#convertCountSql` を変更することで件数取得SQLを変更できます（`universal-dao.json#s23`）。
- 件数取得SQLは元のSQLと同一の検索条件を持つ必要があります。差分が発生しないよう注意してください。
- ページング用の検索処理は、内部的にデータベースアクセス（JDBCラッパー）の範囲指定検索機能を使用します。
- 大量データを扱う場合（ダウンロード処理など）はページングではなく、`UniversalDao#defer` による遅延ロード（`DeferredEntityList`）を使用します（`universal-dao.json#s9`）。

参照:
- `component/libraries/libraries-universal-dao.json#s12`（ページング基本API）
- `component/libraries/libraries-universal-dao.json#s23`（件数取得SQLのカスタマイズ）
- `processing-pattern/web-application/web-application-getting-started-project-search.json#s1`（業務アクションでの実装例）
- `guide/biz-samples/biz-samples-03.json#s5, s6`（関連クラス・タグファイル）
