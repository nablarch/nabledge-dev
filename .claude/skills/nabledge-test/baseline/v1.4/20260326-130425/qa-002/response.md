**結論**: 一覧検索でページングを実装するには、`ListSearchInfo`を継承した検索条件Formクラス、`DbAccessSupport`の`search`メソッドを使用したActionクラス、`nbs:listSearchResult`カスタムタグを使用したJSPの3つを実装する。

---

**根拠**:

## 1. 検索条件FormクラスでListSearchInfoを継承する

```java
public class W11AC01SearchForm extends ListSearchInfo {
    public W11AC01SearchForm(Map<String, Object> params) {
        setPageNumber((Integer) params.get("pageNumber"));
    }

    @PropertyName("開始ページ")
    @Required
    @NumberRange(max = 10, min = 1)
    @Digits(integer = 2)
    public void setPageNumber(Integer pageNumber) {
        super.setPageNumber(pageNumber);
    }

    private static final String[] SEARCH_COND_PROPS = new String[] { ..., "pageNumber" };

    public String[] getSearchConditionProps() {
        return SEARCH_COND_PROPS;
    }
}
```

実装のポイント:
- `pageNumber` と `sortId` のセッターをオーバーライドしてバリデーションアノテーションを設定する
- `SEARCH_COND_PROPS` に `pageNumber` を含める
- `getSearchConditionProps()` メソッドを追加して `SEARCH_COND_PROPS` を返す

## 2. ActionクラスでDbAccessSupportを継承し、searchメソッドを呼び出す

```java
public class W11AC01Action extends DbAccessSupport {

    @OnError(type = ApplicationException.class, path = "/ss11AC/W11AC0101.jsp")
    public HttpResponse doRW11AC0102(HttpRequest req, ExecutionContext ctx) {
        W11AC01Form form = W11AC01Form.validate(req, "search");

        W11AC01SearchForm condition = searchConditionCtx.createObject();
        ctx.setRequestScopedVar("11AC_W11AC01", condition);

        SqlResultSet searchResult;
        try {
            searchResult = search("SELECT_USER_BY_CONDITION", condition);
        } catch (TooManyResultException e) {
            throw new ApplicationException(
                MessageUtil.createMessage(MessageLevel.ERROR, "MSG00035", e.getMaxResultCount()));
        }

        ctx.setRequestScopedVar("searchResult", searchResult);
        ctx.setRequestScopedVar("resultCount", condition.getResultCount());
        return new HttpResponse("/ss11AC/W11AC0101.jsp");
    }
}
```

## 3. JSPでnbs:listSearchResultタグを使用する

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

主要属性:
- `listSearchInfoName`: `ListSearchInfo`継承クラスをリクエストスコープに設定した変数名
- `searchUri`: 検索を行うパス（ページング時の再検索先）
- `resultSetName`: 検索結果をリクエストスコープに設定した変数名

## 4. 主要クラス・タグの概要

| クラス/タグ | 概要 |
|---|---|
| `DbAccessSupport` | 一覧検索用の `search` メソッドを提供するサポートクラス |
| `ListSearchInfo` | 一覧検索用の情報（ページ番号、表示件数など）を保持するクラス |
| `TooManyResultException` | 検索結果件数が最大件数を超えた場合の例外 |
| `listSearchResult` タグ | 検索結果の一覧表示・ページングを出力するタグファイル |

## 5. 表示件数・上限件数の設定

デフォルト値（`nablarch.listSearch.max` = 20件、`nablarch.listSearch.maxResultCount` = 200件）と異なる設定をする場合、Actionクラスで設定する:

```java
private static final int MAX_ROWS = 10;
private static final int MAX_RESULT_COUNT = 50;

condition.setMax(MAX_ROWS);              // 1ページの表示件数
condition.setMaxResultCount(MAX_RESULT_COUNT); // 検索結果件数の上限
```

---

**注意点**:
- `TooManyResultException` は必ずキャッチし、`ApplicationException` に変換してスローすること
- ページング時の検索条件維持はウィンドウスコープで実現する。検索条件フォームと検索結果一覧フォームを分けて実装する必要がある
- JSP内で検索ボタンを実装する場合、`<n:param paramName="xxx.pageNumber" value="1" />` を指定し、検索ボタン押下時は1ページ目から表示させること
- ページングなしで全件表示する場合は、`usePaging="false"` を指定し、Actionで `condition.setMax(condition.getMaxResultCount())` を必ず設定すること
- `getParameterizedSqlStatement` の第2引数と `retrieve` の引数には必ず**同じインスタンス**を渡すこと
- `n:write` タグでステータス（`status`）にアクセスするとエラーが発生するため、`n:set` タグを使用すること

参照: `guide/web-application/web-application-03_listSearch.json#s2`, `guide/web-application/web-application-03_listSearch.json#s1`, `guide/web-application/web-application-03_listSearch.json#s3`, `guide/biz-samples/biz-samples-03_ListSearchResult.json#s2`, `guide/biz-samples/biz-samples-03_ListSearchResult.json#s3`
