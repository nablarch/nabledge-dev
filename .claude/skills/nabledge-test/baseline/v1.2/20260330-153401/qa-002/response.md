**結論**: 一覧検索でページングを実装するには、`ListSearchInfo` を継承した検索条件クラス、`DbAccessSupport` を継承したアクションクラス、および `n:listSearchResult` タグを使用した JSP の3つを実装します。

---

**根拠**:

## 1. 検索条件クラスの実装

`ListSearchInfo` を継承したFormクラスを作成します。

- コンストラクタで `params.get("pageNumber")` を `setPageNumber()` に渡す
- `setPageNumber()` をオーバーライドしてバリデーションアノテーション（`@Required`、`@NumberRange`、`@Digits`）を付加する
- `getSearchConditionProps()` をオーバーライドし、`"pageNumber"` を含む検索条件プロパティ名の配列を返す

```java
public class W11AC01SearchForm extends ListSearchInfo {
    private String loginId;
    // ...

    public W11AC01SearchForm(Map<String, Object> params) {
        loginId = (String) params.get("loginId");
        setPageNumber((Integer) params.get("pageNumber"));
        setSortId((String) params.get("sortId"));
    }
    // ...
}
```

## 2. アクションの実装

`DbAccessSupport` を継承したアクションクラスを実装します。`search("SQL_ID", condition)` で検索実行します。

## 3. JSPの実装

`n:listSearchResult` タグに `listSearchInfoName`、`searchUri`、`resultSetName` 属性を設定してページングを実現します。

**注意点**:
- **ページング時の検索条件**: ページング時は前回検索時の条件を使用する。
- `getSearchConditionProps()` の実装: `pageNumber` および `sortId` をプロパティ名配列に含めること。

参照: `component/libraries/libraries-07_FacilitateTag.json#s2`, `guide/web-application/web-application-03_listSearch.json#s2`
