**結論**: 二重サブミット防止は、クライアント側とサーバ側の**2つを併用**して実装する。DBコミットを伴う処理画面（登録・更新確認→完了画面など）で使用する。

---

## クライアント側の二重サブミット防止

JavaScriptを使用。1回目のサブミット時にonclick属性を書き換え、2回目以降のリクエストをサーバ側に送信しない。ボタンの場合はdisabled属性も設定される。

**JSP実装例**:

```jsp
<n:submit type="button" name="back" value="戻る" uri="./back" />
<n:submit type="button" name="register" value="登録" uri="./register"
          allowDoubleSubmission="false" />
```

`allowDoubleSubmission="false"` を指定することで特定のボタン/リンクのみ防止できる（デフォルトは `true`）。

---

## サーバ側の二重サブミット防止

サーバ側で発行した一意なトークンをサーバ側（セッション）とクライアント側（hiddenタグ）に保持し突合することで実現。トークンは**1回のチェックに限り有効**。

### JSP（n:form の useToken 属性）

確認画面の `<n:form>` に `useToken="true"` を指定する:

```jsp
<n:form useToken="true">
    <n:forConfirmationPage>
        <n:submit value="確定" uri="/action/project/update"
                allowDoubleSubmission="false" type="button" />
    </n:forConfirmationPage>
</n:form>
```

入力画面と確認画面を共通化した場合、確認画面ではデフォルトが `true`（共通化時は指定不要）。

### アクション側（@OnDoubleSubmission）

確定処理のアクションメソッドに `@OnDoubleSubmission` を付与する:

```java
@OnDoubleSubmission
public HttpResponse update(HttpRequest request, ExecutionContext context) {
    Project targetProject = SessionUtil.delete(context, "project");
    UniversalDao.update(targetProject);
    return new HttpResponse(303, "redirect://completeOfUpdate");
}
```

### JSP以外のテンプレートエンジン（Thymeleaf等）の場合

JSPを使用しない場合は `@UseToken` アノテーションを使用し、フォームへ明示的にトークンを埋め込む。

**アクションメソッドに `@UseToken` を付与**:

```java
@UseToken
public HttpResponse confirm(HttpRequest req, ExecutionContext ctx) {
    // 省略
}
```

**Thymeleafでのhidden埋め込み例**:

```xml
<form th:action="@{/path/to/action}" method="post">
  <input type="hidden" name="nablarch_token" th:value="${nablarch_request_token}" />
</form>
```

`name` 属性は `"nablarch_token"`、`value` 属性はリクエストスコープのキー `"nablarch_request_token"` から取得した値を設定する。

その後、後続アクションに `on_double_submission_interceptor` を設定してトークンをチェックする（`@OnDoubleSubmission`）。

---

**注意点**:

- クライアント側・サーバ側**どちらか一方のみ**では不十分:
  - クライアント側のみ → リクエストを重複処理する恐れがある
  - サーバ側のみ → ダブルクリックで2回リクエストが送信された場合、処理順によってはユーザに処理結果が返されない恐れがある
- サーバ側はセッションにトークンを格納するため、**同一ユーザが複数ウィンドウ/タブで並行して確認画面に遷移することができない**（後に遷移した画面のみ処理継続可能）
- スケールアウト環境では、デフォルトのHTTPセッション保管方式ではスティッキーセッションやセッションレプリケーションが必要。トークンをDBに保管する方式（`db_double_submit`）を使用すれば特別な設定なしに複数サーバ間でトークン共有が可能だが、CSRF対策には使用できないため `csrf_token_verification_handler` と併用すること

参照:
- `component/handlers/handlers-use_token.json#s1`
- `component/handlers/handlers-use_token.json#s3`
- `component/libraries/libraries-tag.json#s1`
- `component/libraries/libraries-tag_reference.json#s4`
- `processing-pattern/web-application/web-application-getting-started-project-update.json#s2`
- `component/libraries/libraries-db_double_submit.json#s1`
