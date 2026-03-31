**結論**: 一覧検索でページングを実装するには、`ListSearchInfo` クラスを継承した検索条件クラスを作成し、`DbAccessSupport.search()` メソッドで検索を実行し、JSPで `listSearchResult` タグファイルを使用します。

---

**根拠**:

## 実装手順

### 1. 検索条件クラスの作成（`ListSearchInfo` 継承）

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

**ポイント**:
- コンストラクタで `setPageNumber((Integer) params.get("pageNumber"))` を呼び出す
- `setPageNumber()` にバリデーションアノテーションを付加する
- `getSearchConditionProps()` に `"pageNumber"` を含める

### 2. Actionクラスの実装（`DbAccessSupport` 継承）

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

**`search(SQL_ID, ListSearchInfo)` の動作**:
1. SQL_IDとListSearchInfoから検索結果件数を取得
2. 件数が上限超過の場合は `TooManyResultException` を送出
3. 上限以下の場合は検索を実行し結果を返す（件数はListSearchInfoに設定）

> **注意**: SQL_IDには通常の検索SELECT文を指定する。件数取得・開始位置・取得件数の指定はフレームワークが処理する。

### 3. JSPの実装（`listSearchResult` タグファイル使用）

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

**主要属性**:
- `listSearchInfoName`: `ListSearchInfo` 継承クラスをリクエストスコープに設定した変数名
- `searchUri`: 検索を行うパス（検索ボタンと同じパス）
- `resultSetName`: 検索結果をリクエストスコープに設定した変数名
- `usePaging`: ページングを使用するか否か（デフォルト: true）

ページングには検索条件フォームと検索結果フォームを分離して実装する必要がある（ウィンドウスコープで検索条件を維持するため）。

### 4. 設定値（リポジトリ設定）

| プロパティ名 | 説明 | デフォルト値 |
|---|---|---|
| `nablarch.listSearch.maxResultCount` | 検索結果の最大件数（上限） | 200 |
| `nablarch.listSearch.max` | 1ページの表示件数 | 20 |

個別機能で変更する場合:
```java
condition.setMax(MAX_ROWS);              // 1ページの表示件数
condition.setMaxResultCount(MAX_RESULT_COUNT); // 検索結果の最大件数
```

---

**注意点**:

- `TooManyResultException` は必ずキャッチし `ApplicationException` に変換すること
- `listSearchResult` タグファイルを業務アプリケーションの `/WEB-INF/tags` ディレクトリに配置し、タグファイル内のプレフィックスを修正する必要がある
- ページング時の検索条件はウィンドウスコープで維持されるため、検索条件フォームと検索結果フォームを分離して実装すること
- 検索ボタンには `<n:param paramName="xxx.pageNumber" value="1" />` で取得開始ページを1に指定すること（検索ボタン押下時は1ページ目から表示するため）
- `n:write` タグでステータスにアクセスする際は `n:set` タグを経由すること（直接アクセスするとエラーになる）
- ページングなしで全件表示する場合は `usePaging="false"` を指定し、Actionクラスで `condition.setMax(condition.getMaxResultCount())` を設定すること（必須）

---

参照: `guide/biz-samples/biz-samples-03_ListSearchResult.json#s3`, `guide/biz-samples/biz-samples-03_ListSearchResult.json#s4`, `guide/biz-samples/biz-samples-03_ListSearchResult.json#s2`, `guide/web-application/web-application-03_listSearch.json#s1`, `guide/web-application/web-application-03_listSearch.json#s2`, `guide/web-application/web-application-function.json#s1`