**結論**: `UniversalDao#per()` と `UniversalDao#page()` メソッドをチェーンで呼び出し、続けて `findAllBySqlFile()` を実行することでページング検索を実装できます。

**根拠**:

**基本的なページング検索の実装**:

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
Pagination pagination = users.getPagination();
```

- `per(件数)`: 1ページあたりの表示件数を指定する
- `page(ページ番号)`: 取得するページ番号を指定する
- 検索結果は `EntityList` で返り、`getPagination()` で件数情報（全件数、ページ数等）を取得できる

**実際のWebアプリケーションでの実装例**（プロジェクト検索）:

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

フォームのページ番号（`getPageNumber()`）を `page()` に渡し、1ページあたりの件数（例: 20件）を `per()` に指定します。

**フレームワーク提供クラス（ページング関連）**:

| クラス名 | 概要 |
|---|---|
| `UniversalDao` | `per()` / `page()` メソッドでページング指定を提供 |
| `ListSearchInfo` | 一覧検索用の情報を保持する抽象クラス |
| `Pagination` | `ListSearchInfo` を継承した具象クラス。件数・ページ情報を保持 |
| `EntityList` | 検索結果リスト。`getPagination()` でページング情報を取得可能 |

**注意点**:
- ページング検索では、実際のレコード取得の前に**件数取得SQL**が自動発行される。デフォルトでは元のSQLを `SELECT COUNT(*) FROM` で包んだSQLが使用される。
- `ORDER BY` 句を含む高負荷SQLで性能問題が発生した場合は、使用しているダイアレクトを継承して `Dialect#convertCountSql()` の実装を変更することで件数取得SQLをカスタマイズできる。
- 検索条件にはSQLインジェクション防止のためSQLを外部ファイルに記述し、`$if` 構文で動的条件を実現する。

参照: `libraries-universal_dao.json#s9`, `web-application-getting-started-project-search.json#s1`, `libraries-universal_dao.json#s4`, `biz-samples-03.json#s3`