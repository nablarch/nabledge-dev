**結論**: 一覧検索でページングを実装するには、検索条件クラスで `ListSearchInfo` を継承し、アクションクラスで `DbAccessSupport` の `search` メソッドを使用し、JSPで `n:listSearchResult` タグに `searchUri` を指定します。

---

**根拠**:

## 1. 検索条件クラス（FormクラスでListSearchInfoを継承）

```java
public class W11AC01SearchForm extends ListSearchInfo {
    private String loginId;
    // ... その他検索条件フィールド

    public W11AC01SearchForm(Map<String, Object> params) {
        loginId = (String) params.get("loginId");
        // ...
        setPageNumber((Integer) params.get("pageNumber"));
        setSortId((String) params.get("sortId"));
    }

    @PropertyName("開始ページ")
    @Required
    @NumberRange(max = 10, min = 1)
    @Digits(integer = 2)
    public void setPageNumber(Integer pageNumber) {
        super.setPageNumber(pageNumber);
    }

    @PropertyName("ソートID")
    @Required
    public void setSortId(String sortId) {
        super.setSortId(sortId);
    }

    private static final String[] SEARCH_COND_PROPS =
        new String[] {"loginId", ..., "pageNumber", "sortId"};

    public String[] getSearchConditionProps() {
        return SEARCH_COND_PROPS;
    }
}
```

- `ListSearchInfo` を継承することでページングや並び替えを容易に実現できる
- `setPageNumber` をオーバーライドし `@NumberRange` で想定ページ範囲を設定する
- `getSearchConditionProps()` の返す配列に `pageNumber`（および `sortId`）を含める

## 2. アクションクラス（DbAccessSupportでsearchメソッドを使用）

```java
public class UserSearchAction extends DbAccessSupport {
    @OnError(type = ApplicationException.class, path = "/management/user/USER-001.jsp")
    public HttpResponse doUSERS00101(HttpRequest req, ExecutionContext ctx) {
        W11AC01SearchForm condition = searchConditionCtx.createObject();
        ctx.setRequestScopedVar("searchCondition", condition); // リクエストスコープに設定（必須）

        SqlResultSet searchResult;
        try {
            searchResult = search("SELECT_USER_BY_CONDITION", condition);
        } catch (TooManyResultException e) {
            throw new ApplicationException(
                MessageUtil.createMessage(MessageLevel.ERROR, "MSG00024", e.getMaxResultCount()));
        }
        ctx.setRequestScopedVar("searchResult", searchResult);
        return new HttpResponse("/path/to/list.jsp");
    }
}
```

- `search(SQL_ID, ListSearchInfo)` メソッドが件数取得・ページング位置計算・検索実行をフレームワーク側で担当する
- SQL文はSELECT文のみ指定すればよい（件数取得や開始位置指定はフレームワークが行う）
- 検索結果表示時に `ListSearchInfo` 継承クラスのオブジェクトをリクエストスコープに設定する（**必須**）

## 3. JSP（n:listSearchResultタグ）

```jsp
<n:listSearchResult listSearchInfoName="searchCondition"
                    searchUri="./USERS00101"
                    resultSetName="searchResult">
    <jsp:attribute name="headerRowFragment">
        <tr>
            <th>ログインID</th>
            <th>漢字氏名</th>
        </tr>
    </jsp:attribute>
    <jsp:attribute name="bodyRowFragment">
        <tr class="<n:write name="oddEvenCss" />">
            <td><n:write name="row.loginId" /></td>
            <td><n:write name="row.kanjiName" /></td>
        </tr>
    </jsp:attribute>
</n:listSearchResult>
```

- `usePaging`属性のデフォルトはtrue（省略可）
- `searchUri` はページングを使用する場合は**必ず指定**する
- `pagingPosition` でページングの表示位置（`top`/`bottom`/`both`/`none`）を変更可能

---

**注意点**:

- ページング時の検索条件は**前回検索時の条件**を使用する。検索条件を変更してからページングを行った場合、変更した検索条件の値は破棄される
- `getSearchConditionProps()` の返す配列に `pageNumber` を含めないと、ページングのサブミット要素（前へ・次へなど）が正しく動作しない
- ページングを**使用しない**場合は `condition.setMax(condition.getMaxResultCount())` の設定が必須（設定しないと正しく動作しない）
- JSPのボディ行で `n:write` タグでステータスにアクセスするとエラーになる。`n:set` タグを使うこと（例: `<n:set var="rowCount" value="${status.count}" />`）
- 表示件数や検索結果件数上限をデフォルト値と異なる設定にしたい場合は、アクションのメソッドで `condition.setMax(件数)` および `condition.setMaxResultCount(上限)` を設定する

---

参照: `guide/web-application/web-application-03_listSearch.json#s2`, `guide/web-application/web-application-03_listSearch.json#s3`, `component/libraries/libraries-07_FacilitateTag.json#s2`, `component/libraries/libraries-07_FacilitateTag.json#s3`, `component/libraries/libraries-07_FacilitateTag.json#s4`, `component/libraries/libraries-07_FacilitateTag.json#s8`

###