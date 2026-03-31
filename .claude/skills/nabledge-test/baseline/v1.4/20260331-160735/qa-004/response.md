**結論**: 二重サブミット防止はサーバサイドの「トークンチェック」とJavaScriptによる「クライアントサイドの制御」の2つの方法で実装できます。Nablarch ウェブアプリケーションでは、これらを組み合わせて使用するのが基本です。

---

**根拠**:

## 1. サーバサイドのトークンチェック

サーバ側で発行した一意なトークンをセッション（サーバ側）とhiddenタグ（クライアント側）に保持し、サーバ側で突合することで二重サブミットを検知します。

### JSPの実装

`n:form` タグの `useToken` 属性に `true` を設定します。

```jsp
<n:form useToken="true">
```

| 条件 | useToken属性 |
|---|---|
| 入力画面と確認画面を共通化している | 設定不要（自動的にトークンが設定される） |
| 共通化していない | `true` を設定する |

### Actionクラスの実装

トークンをチェックしたいメソッドに `@OnDoubleSubmission` アノテーションを付与します。

```java
@OnError(type = ApplicationException.class, path = "forward://RW11AC0201")
@OnDoubleSubmission(
    path = "forward://RW11AC0201"
)
public HttpResponse doRW11AC0204(HttpRequest req, ExecutionContext ctx) {
    W11AC02Form form = validate(req);
    // ...
    return new HttpResponse("/ss11AC/W11AC0203.jsp");
}
```

`@OnDoubleSubmission` の属性:

| 属性 | 説明 |
|---|---|
| `path` | 二重サブミットと判定した場合の遷移先リソースパス（**必須: 未指定はシステムエラー**） |
| `messageId` | 遷移先画面に表示するエラーメッセージのメッセージID |
| `statusCode` | レスポンスステータス（デフォルト: 400） |

### コンポーネント設定（BasicDoubleSubmissionHandler）

`BasicDoubleSubmissionHandler` をリポジトリに登録することで、アノテーションで個別指定しない場合のデフォルト値を設定できます。

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
    <property name="messageId" value="MSG00022" />
    <property name="statusCode" value="200" />
</component>
```

### インターセプタの実行順設定

`interceptorsOrder` に `OnDoubleSubmission` を定義する必要があります（未定義の場合は実行時例外）。

```xml
<list name="interceptorsOrder">
  <value>nablarch.common.web.token.OnDoubleSubmission</value>
  <value>nablarch.fw.web.interceptor.OnErrors</value>
  <value>nablarch.fw.web.interceptor.OnError</value>
</list>
```

---

## 2. JavaScriptによるクライアントサイド制御

ユーザのダブルクリックやボタン連打を防ぐ方法です。サンプル提供の `button` タグの `allowDoubleSubmission` 属性に `false` を指定します。

```jsp
<n:submit ... allowDoubleSubmission="false" />
```

---

**注意点**:
- `@OnDoubleSubmission` の `path` 属性は、アノテーションと `BasicDoubleSubmissionHandler` のいずれかに必ず指定すること。両方未指定の場合、二重サブミット判定時にシステムエラーとなる。
- 同一業務を複数ウィンドウで並行操作した場合、後に確認画面に遷移したウィンドウのみ処理継続可能。先に遷移したウィンドウのトークンは古くなり、処理実行すると二重サブミットと判定される。
- Firefox の古いバージョン（3.x系含む）では `n:submitLink` のダブルクリックで2回リクエストが送信される問題があるが、サーバサイドのトークンチェックと併用することで業務処理が2重実行されることはない（Firefox 9.01以降で解消）。
- リクエスト単体テストで二重サブミット防止を施しているURIをテストする際は、テスト実行前に `setValidToken(request, context)` または `setToken(request, context, true)` でトークンをセッションに設定する必要がある。

参照: `component/libraries/libraries-07_SubmitTag.json#s2`, `guide/web-application/web-application-07_insert.json#s6`, `guide/web-application/web-application-07_insert.json#s5`, `component/handlers/handlers-HttpMethodBinding.json#s6`, `development-tools/testing-framework/testing-framework-02_RequestUnitTest-06_TestFWGuide.json#s5`