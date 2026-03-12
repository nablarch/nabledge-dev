**結論**: UniversalDaoでページングを実装するには、`UniversalDao.per(件数).page(ページ番号).findAllBySqlFile(...)` の順でメソッドを呼び出します。

**根拠**:

#### 基本的な使い方

`per()` メソッドで1ページあたりの件数、`page()` メソッドでページ番号を指定してから `findAllBySqlFile()` を呼び出します。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
```

ページング表示に必要な件数情報（総件数、総ページ数など）は `Pagination` オブジェクトが保持しており、`EntityList` から取得できます。

```java
Pagination pagination = users.getPagination();
```

#### Webアプリケーションでの実装例

検索画面でのページング実装の典型的なパターンです。フォームのページ番号を使って動的に切り替えます。

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

フォームクラスは `SearchFormBase` を継承することでページ番号プロパティを利用できます。

#### ページング関連クラス構成

| クラス名 | 概要 |
|---|---|
| `UniversalDao` | `per()`, `page()` メソッドでページング指定 |
| `Pagination` | `ListSearchInfo` を継承した具象クラス。件数情報を保持 |
| `EntityList` | 検索結果リスト。`getPagination()` で `Pagination` を取得可能 |
