**結論**: Nablarchの二重サブミット防止は、**クライアント側（JavaScript）とサーバ側（トークン）の2つを併用**して実装します。DBコミットを伴う画面では両方の対策が必要です。

---

**根拠**:

## 1. クライアント側: JavaScriptによる二重サブミット防止

`n:button` タグや `n:submitLink` タグの `allowDoubleSubmission` 属性に `false` を指定します。

```jsp
<n:button uri="..." allowDoubleSubmission="false">登録</n:button>
```

この設定でダブルクリックや連続クリックによる2回以上のリクエスト送信を防止します。

---

## 2. サーバ側: トークンによる二重サブミット防止

### JSP実装

`n:form` タグの `useToken` 属性に `true` を設定します。

```jsp
<n:form useToken="true">
  ...
</n:form>
```

### Actionクラス実装

```java
@OnDoubleSubmission(
    path = "forward://RW11AC0201"
)
public HttpResponse doRW11AC0204(HttpRequest req, ExecutionContext ctx) {
    W11AC02Form form = validate(req);
    return new HttpResponse("/ss11AC/W11AC0203.jsp");
}
```

参照: `component/libraries/libraries-07_SubmitTag.json#s3`, `guide/web-application/web-application-07_insert.json#s4`
