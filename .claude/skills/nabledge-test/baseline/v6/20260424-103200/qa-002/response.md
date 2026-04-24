**結論**: UniversalDaoでページング検索を実装するには、検索時に `UniversalDao#per(件数)` と `UniversalDao#page(ページ番号)` を呼び出してから `findAllBySqlFile` 等の検索メソッドを実行します。検索結果は `EntityList` として返り、そこから `getPagination()` で `Pagination`（検索結果件数、ページ数など）を取得できます。

**根拠**:

1. 基本形（`component/libraries/libraries-universal-dao.json#s12`）:

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

ページング情報は `Pagination` が保持し、`EntityList` から取得できます。

```java
Pagination pagination = users.getPagination();
```

2. 業務アクションでの実装例（`processing-pattern/web-application/web-application-getting-started-project-search.json#s1`）:

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

- `per(件数)`: 1ページあたりの件数
- `page(番号)`: 取得するページ番号（画面から受け取る）
- SQLは外部ファイル（例: `SEARCH_PROJECT`）にSQLIDとして定義

3. 関連クラス（`guide/biz-samples/biz-samples-03.json#s5, s8, s9`）:

| クラス | 役割 |
|---|---|
| `UniversalDao` | 汎用的なDAO機能を提供 |
| `ListSearchInfo` | 一覧検索用の情報を保持する抽象クラス |
| `Pagination` | `ListSearchInfo` を継承した具象クラス。ページネーション情報（`resultCount`、`pageNumber`、`pageCount` など）を保持 |
| `EntityList` | `UniversalDao` から返される結果リスト。`java.util.ArrayList` を継承し `Pagination` をフィールドに持つ |

4. JSPでのページング表示（`guide/biz-samples/biz-samples-03.json#s17`）:
   `<app:listSearchResult>` タグを使用することで、検索結果件数・ページング（前へ/次へ/ページ番号）・検索結果テーブルをまとめて出力できます。`resultSetName` 属性で `EntityList` をリクエストスコープから取り出し、`searchUri` 属性にページングサブミット用URIを指定します。

5. 内部動作（`component/libraries/libraries-database.json#s2`）:
   ページング検索は、`Dialect#convertPaginationSql`（範囲指定SQLへの変換）と `convertCountSql`（件数取得SQLへの変換）により、使用するデータベース製品の方言に応じて実現されています。

**注意点**:

- ページングでは、実際の範囲指定レコード取得の前に **件数取得SQLが別途発行** されます。件数取得SQLに起因して性能劣化が発生した場合、必要に応じて「ページング処理の件数取得用SQLを変更する」の手順で件数取得SQLを個別に差し替えてください（`libraries-universal-dao.json#s12`）。
- ページング用の検索処理は、内部的に「データベースアクセス(JDBCラッパー)の範囲指定検索機能」を使用して行われます（`libraries-universal-dao.json#s12`）。
- 大量データをすべて扱いたい場合（ダウンロードや大量バッチ処理）は、ページングではなく `UniversalDao#defer` による遅延ロードの使用が推奨されます（`libraries-universal-dao.json#s9`）。

参照:
- `component/libraries/libraries-universal-dao.json#s12` (ページングの基本API)
- `processing-pattern/web-application/web-application-getting-started-project-search.json#s1` (業務アクション実装例)
- `guide/biz-samples/biz-samples-03.json#s5, s6, s8, s9, s17` (関連クラス/タグ)
- `component/libraries/libraries-database.json#s2` (Dialectによる範囲指定SQL変換)
