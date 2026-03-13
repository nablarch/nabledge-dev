**結論**: `UniversalDao#per` メソッドと `UniversalDao#page` メソッドを組み合わせて呼び出すことでページング検索を実装できる。

**根拠**:

## 基本的な使い方

`UniversalDao.per()` で1ページあたりの件数、`UniversalDao.page()` でページ番号を指定し、その後に検索メソッドを呼び出す。

```java
EntityList<User> users = UniversalDao.per(3).page(1)
                            .findAllBySqlFile(User.class, "FIND_ALL_USERS");
Pagination pagination = users.getPagination();
```

ページング情報（総件数、総ページ数など）は `EntityList#getPagination()` で取得できる `Pagination` オブジェクトに格納される。

## 実装例（プロジェクト検索）

業務アクション内での実装例：

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

ページ番号はフォームから受け取る（`pageNumber` という名前のプロパティで受け取る実装が必要）。

## 画面表示（JSPタグ）

ページングUIはフレームワーク提供のクラスとサンプル提供のタグファイルで実現できる。

**フレームワーク提供クラス**:
- `UniversalDao` - DAO機能
- `Pagination` - ページング情報保持クラス
- `EntityList` - 検索結果リスト（Paginationを内包）

**タグファイル（nablarch-biz-sample-all）**:
- `listSearchResult` - 検索結果一覧表示タグ
- `listSearchPaging` - ページングUI出力タグ
- `listSearchSubmit` - ページングのサブミット要素出力タグ

JSPでの使用例：

```jsp
<c:url value="/action/project/list" var="uri" context="/">
  <c:param name="searchForm.projectName" value="${searchForm.projectName}"/>
</c:url>
<app:listSearchResult resultSetName="searchResult" searchFormName="searchForm" searchUri="${uri}">
  <jsp:attribute name="headerRowFragment">
    <tr><th>プロジェクト名</th></tr>
  </jsp:attribute>
  <jsp:attribute name="bodyRowFragment">
    <tr><td><n:write name="row.projectName" /></td></tr>
  </jsp:attribute>
</app:listSearchResult>
```

**ページング使用時の必須実装**: `searchFormName` で指定するフォームが `pageNumber` という名前でページ番号を受け取る実装が必要。

```java
public class ProjectSearchForm {
    @Required
    @Domain("pageNumber")
    private String pageNumber;
    // getter/setter...
}
```

## 件数取得SQLのカスタマイズ

ページング時は自動的に件数取得SQLが発行される（元SQLを `SELECT COUNT(*) FROM` で包んだSQL）。`ORDER BY` 句を含む高負荷SQLで性能劣化が発生した場合は、使用しているDialectを継承して `Dialect#convertCountSql` の実装を変更することでカスタマイズできる。

**注意点**:
- ページング使用時は、件数取得SQLが自動発行される。検索SQLに `ORDER BY` 句がある場合は性能に注意すること。
- フォームには `pageNumber` プロパティの実装が必須。
- 画面表示に `listSearchResult` タグを使用する場合は nablarch-biz-sample-all の依存関係が必要。
- 大量データ処理（Webダウンロード、バッチなど）でページングが適さない場合は `UniversalDao#defer`（遅延ロード）も検討できる。

参照: `component/libraries/libraries-universal_dao.json#s9`, `processing-pattern/web-application/web-application-getting-started-project-search.json#s1`, `guide/biz-samples/biz-samples-03.json#s3`
