**結論**: 一覧検索でページングを実装するには、`ListSearchInfo`を継承した検索条件クラスを作成し、`DbAccessSupport`の`search()`メソッドで検索を実行し、JSPで`n:listSearchResult`タグを使用します。フレームワークがページング処理を提供するため、業務アプリケーション側でページングを作り込む必要はありません。

---

**根拠**:

## 実装手順

### 1. 検索条件クラスの実装（`ListSearchInfo`継承）

```java
public class W11AC01SearchForm extends ListSearchInfo {
    private String loginId;
    // その他の検索条件プロパティ...

    public W11AC01SearchForm(Map<String, Object> params) {
        loginId = (String) params.get("loginId");
        // その他プロパティの設定...
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

**必須実装**:
- `setPageNumber()` をオーバーライドして `@Required`、`@NumberRange`、`@Digits` アノテーションを付加する
- `getSearchConditionProps()` をオーバーライドし、`"pageNumber"` を含む検索条件プロパティ名の配列を返す

### 2. アクションの実装（`DbAccessSupport`継承）

```java
public class W11AC01Action extends DbAccessSupport {
    @OnError(type = ApplicationException.class, path = "/ss11AC/W11AC0101.jsp")
    public HttpResponse doRW11AC0102(HttpRequest req, ExecutionContext ctx) {
        ValidationContext<W11AC01SearchForm> searchConditionCtx =
            ValidationUtil.validateAndConvertRequest("11AC_W11AC01", W11AC01SearchForm.class, req, "search");
        if (!searchConditionCtx.isValid()) {
            throw new ApplicationException(searchConditionCtx.getMessages());
        }
        W11AC01SearchForm condition = searchConditionCtx.createObject();
        ctx.setRequestScopedVar("searchCondition", condition); // ListSearchInfo継承クラスをリクエストスコープに設定（必須）

        SqlResultSet searchResult;
        try {
            searchResult = search("SELECT_USER_BY_CONDITION", condition);
        } catch (TooManyResultException e) {
            throw new ApplicationException(
                MessageUtil.createMessage(MessageLevel.ERROR, "MSG00024", e.getMaxResultCount()));
        }
        ctx.setRequestScopedVar("searchResult", searchResult);
        return new HttpResponse("/ss11AC/W11AC0101.jsp");
    }
}
```

`search("SQL_ID", ListSearchInfo)` の処理:
1. SQL_IDとListSearchInfoから検索結果の件数を取得
2. 件数が上限超過 → `TooManyResultException` を送出
3. 件数が上限以内 → 検索実行し結果を返す（検索結果件数はListSearchInfoに設定される）

### 3. JSPの実装（`n:listSearchResult`タグ）

```jsp
<n:form>
  <%-- 検索条件入力フィールド --%>
  <n:submit name="search" type="submit" value="検索" uri="./USERS00101">
    <n:param paramName="pageNumber" value="1" />  <%-- 検索時は1ページ目から --%>
  </n:submit>

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
</n:form>
```

`n:listSearchResult`の必須属性:

| 属性名 | 説明 |
|---|---|
| `listSearchInfoName` | リクエストスコープに設定した`ListSearchInfo`継承クラスの変数名 |
| `searchUri` | 検索パス（検索ボタンと同じパス） |
| `resultSetName` | リクエストスコープに設定した検索結果の変数名 |
| `headerRowFragment` | ヘッダ行のJSPフラグメント |
| `bodyRowFragment` | ボディ行のJSPフラグメント |

---

**注意点**:
- ページング時の検索条件は前回検索時の条件を使用する。検索条件を変更してからページングを行った場合、変更した検索条件の値は破棄される
- `getSearchConditionProps()` の返す配列に `"pageNumber"` を含めることが必須。含めないとページング時に検索条件が正しく引き継がれない
- ボディ行で `n:write` タグでステータスにアクセスするとエラーが発生するため、`n:set` タグを使用すること（例: `<n:set var="rowCount" value="${status.count}" />`）
- ページングを使用しない場合は `condition.setMax(condition.getMaxResultCount())` の設定が必須
- 値の出力には `n:write` タグを使用すること。EL式はサニタイジング処理を行わないため直接出力しないこと

**参照**: `component/libraries/libraries-07_FacilitateTag.json#s2`, `component/libraries/libraries-07_FacilitateTag.json#s3`, `component/libraries/libraries-07_FacilitateTag.json#s4`, `guide/web-application/web-application-03_listSearch.json#s2`, `guide/web-application/web-application-03_listSearch.json#s3`, `guide/web-application/web-application-function.json#s1`

**