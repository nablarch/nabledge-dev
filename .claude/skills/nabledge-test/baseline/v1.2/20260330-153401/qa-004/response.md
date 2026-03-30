**結論**: 二重サブミット防止には、**JavaScript方式**（クライアント側）と**トークン方式**（サーバ側）の2種類があります。DBの登録・更新処理では、トークン方式による確実な防止が必要です。

---

**根拠**:

## 1. JavaScript方式（クライアント側）

`n:submit` タグの `allowDoubleSubmission` 属性を `false` に設定することで、ボタン連打によるリクエストの2重送信を防止します。

## 2. トークン方式（サーバ側）

### JSP側: `n:form` の `useToken` 属性を `true` に設定

```jsp
<n:form useToken="true">
    ...
</n:form>
```

### Action側: `@OnDoubleSubmission` アノテーションを付与

```java
@OnDoubleSubmission(
    path = "forward://RW11AC0201"
)
public HttpResponse doRW11AC0204(HttpRequest req, ExecutionContext ctx) {
    // ...
}
```

### アプリケーション全体のデフォルト設定

`BasicDoubleSubmissionHandler` をリポジトリに登録することで全体デフォルトを設定できます。

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
    <property name="messageId" value="MSG00022" />
    <property name="statusCode" value="200" />
</component>
```

インターセプタ実行順に `OnDoubleSubmission` を登録する必要があります。

**注意点**:
- トークンは**1回のチェックに限り有効**です。
- `@OnDoubleSubmission` と `@OnError` を**両方付与する場合**、インターセプタ実行順に注意してください。

参照:
- `guide/web-application/web-application-07_insert.json#s5`
- `component/libraries/libraries-07_SubmitTag.json#s2`
