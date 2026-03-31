**結論**: 一覧検索でページングを実装するには、`ListSearchInfo`クラスを継承した検索条件クラスを作成し、`listSearchResult`タグを使用したJSPと、`DbAccessSupport`の`search`メソッドを使用するActionクラスの3点を実装する。

---

**根拠**:

## 1. 検索条件クラスの実装（`ListSearchInfo`継承）

```java
public abstract class W11AC01FormBase extends ListSearchInfo {
    // 検索条件フィールド (loginId, kanjiName等)

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
}

public class W11AC01Form extends W11AC01FormBase {
    private static final String[] SEARCH_CONDITION_PROPS = {
        "loginId", "kanjiName", ..., "pageNumber", "sortId"
    };

    public String[] getSearchConditionProps() {
        return SEARCH_CONDITION_PROPS;
    }
    // バリデーションメソッド省略
}
```

**実装要点**:
- `pageNumber`のセッターをオーバーライドしてバリデーションアノテーションを付加する
- `getSearchConditionProps()`をオーバーライドし、`SEARCH_COND_PROPS`に`"pageNumber"`を含める

## 2. Actionクラスの実装

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
        return new HttpResponse("/ss11AC/W11AC0101.jsp");
    }
}
```

**実装要点**:
- `DbAccessSupport`の`search()`メソッドで検索（ページング処理は自動）
- `TooManyResultException`をキャッチして`ApplicationException`に変換すること
- `ListSearchInfo`継承クラスをリクエストスコープに設定する（`listSearchResult`タグが使用）

## 3. JSPの実装

```jsp
<%-- 検索条件フォームと検索結果フォームを分離すること --%>
<nbs:listSearchResult listSearchInfoName="11AC_W11AC01"
                      searchUri="/action/ss11AC/W11AC01Action/RW11AC0102"
                      resultSetName="searchResult">
    <jsp:attribute name="headerRowFragment">
        <tr><th>ログインID</th><th>漢字氏名</th></tr>
    </jsp:attribute>
    <jsp:attribute name="bodyRowFragment">
        <tr>
            <td><n:write name="row.LOGIN_ID" /></td>
            <td><n:write name="row.KANJI_NAME" /></td>
        </tr>
    </jsp:attribute>
</nbs:listSearchResult>
```

**実装要点**:
- ページング時の検索条件維持のため、ウィンドウスコープを使用し、**検索条件フォームと検索結果フォームを分離する**
- 検索ボタンには`<n:param paramName="xxx.pageNumber" value="1" />`で取得開始ページを指定する（検索時は常に1ページ目から）

## ページング設定（リポジトリ設定）

| プロパティ名 | 説明 | デフォルト値 |
|---|---|---|
| `nablarch.listSearch.maxResultCount` | 検索結果の最大件数（上限） | 200 |
| `nablarch.listSearch.max` | 1ページの表示件数 | 20 |

個別に変更する場合はActionクラスで直接設定：
```java
condition.setMax(MAX_ROWS);            // 1ページの表示件数
condition.setMaxResultCount(MAX_RESULT_COUNT);  // 検索結果の最大件数
```

---

**注意点**:
- `TooManyResultException`は必ずキャッチして`ApplicationException`に変換すること（未キャッチだとシステムエラーになる）
- 検索条件フォームと検索結果フォームを同一画面に配置する場合は必ず分離して実装すること（ページング時の検索条件維持のため）
- `getSearchConditionProps()`で返す配列に`pageNumber`を含めること（含めないとページング時に検索条件が失われる）
- ページングなしで全件表示する場合は`condition.setMax(condition.getMaxResultCount())`を必ず設定し、JSPで`usePaging="false"`を指定する

---

参照: `guide/web-application/web-application-function.json#s1`, `guide/web-application/web-application-03_listSearch.json#s2`, `guide/web-application/web-application-03_listSearch.json#s3`, `guide/biz-samples/biz-samples-03_ListSearchResult.json#s2`
