**結論**: 一覧検索でページングを実装するには、`ListSearchInfo`を継承した検索条件クラスを作成し、`DbAccessSupport`の`search`メソッドで検索を実行し、JSPで`nbs:listSearchResult`タグを使用します。

```java
public class W11AC01Action extends DbAccessSupport {
    public HttpResponse doRW11AC0102(HttpRequest req, ExecutionContext ctx) {
        W11AC01SearchForm condition = ...;
        ctx.setRequestScopedVar("11AC_W11AC01", condition);
        SqlResultSet searchResult = search("SELECT_USER_BY_CONDITION", condition);
        ctx.setRequestScopedVar("searchResult", searchResult);
        return new HttpResponse("/ss11AC/W11AC0101.jsp");
    }
}
```

参照: `guide/biz-samples/biz-samples-03_ListSearchResult.json#s3`
