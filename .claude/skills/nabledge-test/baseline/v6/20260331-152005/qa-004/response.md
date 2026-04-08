**結論**: 二重サブミット防止は、**クライアント側**とサーバ側の**2つを併用**して実装します。DBコミットを伴う処理画面では両方の対応が必要です。

**根拠**:

## クライアント側の二重サブミット防止

JavaScriptを使用して、1回目のサブミット時にonclick属性を書き換え、2回目以降のリクエストをサーバ側に送信しない方式です。

対応するカスタムタグ（`n:submit`, `n:button`, `n:submitLink`）で `allowDoubleSubmission="false"` を指定します（デフォルトは `true`）。

```jsp
<n:submit type="button" name="back" value="戻る" uri="./back" />
<n:submit type="button" name="register" value="登録" uri="./register"
          allowDoubleSubmission="false" />
```

確認画面での実装例（`n:forConfirmationPage` タグと組み合わせ）:

```jsp
<n:forConfirmationPage>
    <n:button uri="/action/client/back"
              cssClass="btn btn-lg btn-light">入力へ戻る</n:button>
    <n:button uri="/action/client/create"
              allowDoubleSubmission="false"
              cssClass="btn btn-lg btn-success">確定</n:button>
</n:forConfirmationPage>
```

---

## サーバ側の二重サブミット防止

サーバ側で発行した一意なトークンをセッション（サーバ側）とhiddenタグ（クライアント側）に保持して突合します。トークンは**1回のチェックに限り有効**です。

### 手順1: トークンの設定（JSP使用時）

`n:form` タグの `useToken` 属性を `true` に設定します（入力・確認画面共通化時は確認画面でデフォルト `true`）。

```jsp
<n:form useToken="true">
```

### 手順2: トークンのチェック（アクションメソッド）

業務アクションメソッドに `@OnDoubleSubmission` アノテーションを付与します。`path` 属性に二重サブミット判定時の遷移先を指定します。

```java
@OnDoubleSubmission(path = "/WEB-INF/view/error/userError.jsp")
public HttpResponse register(HttpRequest req, ExecutionContext ctx) {
    // 省略
}
```

### アプリケーション全体のデフォルト設定

`BasicDoubleSubmissionHandler` をコンポーネント定義に追加することで、`@OnDoubleSubmission` のデフォルト値（遷移先パス・メッセージID・ステータスコード）を一括設定できます。

```xml
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
  <property name="path" value="/WEB-INF/view/error/userError.jsp" />
  <property name="messageId" value="DOUBLE_SUBMISSION_ERROR" />
  <property name="statusCode" value="200" />
</component>
```

---

## JSP以外のテンプレートエンジン使用時（Thymeleafなど）

`@UseToken` アノテーションをアクションメソッドに付与し、テンプレートに明示的にトークンを埋め込みます。

```java
@UseToken
public HttpResponse confirm(HttpRequest req, ExecutionContext ctx) {
    // 省略
}
```

```xml
<form th:action="@{/path/to/action}" method="post">
  <input type="hidden" name="nablarch_token" th:value="${nablarch_request_token}" />
```