**結論**: 二重サブミット防止は、**クライアント側**（JavaScript）と**サーバ側**（トークンチェック）の両方を組み合わせて実装します。データベースコミットを伴う処理では必ず両方を使用してください。

---

**根拠**:

## 1. クライアント側の実装

JavaScriptで実現します。1回目のサブミット時にonclick属性を書き換え、2回目以降のサブミットをサーバに送信しません。

`n:submit` / `n:button` / `n:submitLink` タグの `allowDoubleSubmission` 属性に `false` を指定します（デフォルト: `true`）。

```jsp
<!-- 「戻る」は二重サブミット防止不要、「登録」のみ指定 -->
<n:submit type="button" name="back" value="戻る" uri="./back" />
<n:submit type="button" name="register" value="登録" uri="./register"
          allowDoubleSubmission="false" />
```

確認画面では `<n:forConfirmationPage>` タグと組み合わせて実装します：

```jsp
<n:forConfirmationPage>
    <n:button uri="/action/client/back" cssClass="btn btn-default">入力へ戻る</n:button>
    <n:button uri="/action/client/create"
              allowDoubleSubmission="false"
              cssClass="btn btn-success">確定</n:button>
</n:forConfirmationPage>
```

## 2. サーバ側の実装

### 2-1. トークン設定（JSP）

`<n:form>` タグの `useToken` 属性を `true` に指定します。入力画面と確認画面を共通化した場合、確認画面ではデフォルトが `true` になるため指定不要です。

```jsp
<n:form useToken="true">
    ...
</n:form>
```

### 2-2. トークン設定（JSP以外のテンプレートエンジン）

`UseToken` インターセプタを使用します。テンプレートエンジン側でトークンをhiddenに明示的に埋め込む必要があります。

```java
// UseToken インターセプタ (nablarch.common.web.token.UseToken) をアクションに設定
```

### 2-3. 二重サブミットチェック（アクション）

業務アクションメソッドに `@OnDoubleSubmission` アノテーションを付与します。`path` 属性に二重サブミット判定時の遷移先を指定します。

```java
@OnDoubleSubmission(path = "/WEB-INF/view/error/userError.jsp")
public HttpResponse register(HttpRequest req, ExecutionContext ctx) {
    // 登録処理
}
```

`path` を省略して、アプリケーション全体のデフォルト遷移先を `BasicDoubleSubmissionHandler` で設定する方法もあります：

```xml
<!-- component定義 -->
<component name="doubleSubmissionHandler"
           class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
  <property name="path" value="/WEB-INF/view/error/userError.jsp" />
  <property name="messageId" value="DOUBLE_SUBMISSION_ERROR" />
  <property name="statusCode" value="200" />
</component>
```

> **重要**: `@OnDoubleSubmission` と `BasicDoubleSubmissionHandler` のどちらも `path` が未指定の場合、システムエラーになります。必ずどちらかで `path` を指定してください。

## 3. 実装例（更新処理の全体像）

**JSP（確認画面）**:
```jsp
<n:form useToken="true">
    <n:forConfirmationPage>
        <n:submit value="確定" uri="/action/project/update" id="bottomSubmitButton"
                allowDoubleSubmission="false" type="button" />
    </n:forConfirmationPage>
</n:form>
```

**アクション**:
```java
@OnDoubleSubmission
public HttpResponse update(HttpRequest request, ExecutionContext context) {
    Project targetProject = SessionUtil.delete(context, "project");
    UniversalDao.update(targetProject);
    return new HttpResponse(303, "redirect://completeOfUpdate");
}
```

---

**注意点**:

- **両方を使う理由**: クライアント側のみの場合はリクエストの多重処理が起きる恐れがあります。サーバ側のみの場合はダブルクリックで2リクエスト送信時、処理順によっては正常ユーザにエラーが返される恐れがあります。
- **複数ウィンドウの制限**: トークンはセッションに格納されるため、同一ユーザが複数ウィンドウ/タブで同時に確認画面へ遷移すると、後から確認画面に遷移した側のみ処理継続できます（先に遷移した側はトークン不一致でエラーになります）。
- **`@OnDoubleSubmission` の `path` 必須**: アノテーションと `BasicDoubleSubmissionHandler` のどちらにも `path` が設定されていない場合はシステムエラーとなります。

参照: `handlers-on_double_submission.json#s1`, `handlers-on_double_submission.json#s3`, `handlers-on_double_submission.json#s4`, `handlers-use_token.json#s1`, `libraries-tag.json#s1`, `web-application-client_create4.json#s1`, `web-application-getting-started-project-update.json#s2`