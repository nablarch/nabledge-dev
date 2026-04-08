**結論**: 一覧検索でページングを実装するには、`ListSearchInfo`を継承した検索条件Formクラスを作成し、`DbAccessSupport`の`search`メソッドで検索を行い、JSPで`nbs:listSearchResult`タグを使用します。

**根拠**:

#### 1. 検索条件Formクラス (`ListSearchInfo`継承)

`ListSearchInfo`を継承したクラスを作成し、`pageNumber`プロパティを入力精査に含める必要があります。

```java
public class W11AC01SearchForm extends ListSearchInfo {
    public W11AC01SearchForm(Map<String, Object> params) {
        setPageNumber((Integer) params.get("pageNumber"));
    }

    @PropertyName("ページ番号")
    @Required
    @NumberRange(max = 10, min = 1)
    @Digits(integer = 2)
    public void setPageNumber(Integer pageNumber) {
        super.setPageNumber(pageNumber);
    }

    private static final String[] SEARCH_COND_PROPS = new String[] { ..., "pageNumber"};

    public String[] getSearchConditionProps() {
        return SEARCH_COND_PROPS;
    }
}
```

#### 2. Actionクラス (`DbAccessSupport`継承)

`DbAccessSupport.search()`メソッドに SQL_ID と `ListSearchInfo` を渡すことでページング検索が実行されます。COUNT処理・ページング（開始位置・取得件数）はフレームワークが自動で処理します。

```java
public class W11AC01Action extends DbAccessSupport {
    @OnError(type = ApplicationException.class, path = "/ss11AC/W11AC0101.jsp")
    public HttpResponse doRW11AC0102(HttpRequest req, ExecutionContext ctx) {
        ValidationContext<W11AC01SearchForm> searchConditionCtx =
            ValidationUtil.validateAndConvertRequest("11AC_W11AC01", W11AC01SearchForm.class, req, "search");
        searchConditionCtx.abortIfInvalid();

        W11AC01SearchForm condition = searchConditionCtx.createObject();
        ctx.setRequestScopedVar("11AC_W11AC01", condition);  // ページング用にリクエストスコープへ設定

        SqlResultSet searchResult = null;
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

#### 3. JSP (`nbs:listSearchResult`タグ)

`listSearchInfoName`属性にリクエストスコープのキー名を指定し、`searchUri`属性にページング用のURIを指定します。

```jsp
<nbs:listSearchResult listSearchInfoName="11AC_W11AC01"
                      searchUri="/action/ss11AC/W11AC01Action/RW11AC0102"
                      resultSetName="searchResult">
    <jsp:attribute name="headerRowFragment">
        <tr>
            <th>ログインID</th>
            <th>漢字氏名</th>
        </tr>
    </jsp:attribute>
    <jsp:attribute name="bodyRowFragment">
        <tr class="<n:write name='oddEvenCss' />">
            <td><n:write name="row.loginId" /></td>
            <td><n:write name="row.kanjiName" /></td>
        </tr>
    </jsp:attribute>
</nbs:listSearchResult>
```

#### 4. ページング件数設定

デフォルト値（最大件数200件・1ページ20件）を変更する場合は、Actionクラスで設定します。

```java
condition.setMax(10);              // 1ページの表示件数
condition.setMaxResultCount(50);   // 検索結果の最大件数（上限）
```

**注意点**:
- `pageNumber`プロパティは入力精査に必ず含める（ページング動作に必要）
- `ListSearchInfo`を継承したオブジェクトをリクエストスコープに設定することが必須（`nbs:listSearchResult`タグが参照するため）
- ページング時は前回の検索条件が使用される。検索条件とページングのフォームは分けて実装すること

参照: `guide/biz-samples/biz-samples-03_ListSearchResult.json#s3`, `#s4`, `#s5`, `#s1`, `#s6`
