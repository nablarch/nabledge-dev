**結論**: Nablarch 6 で二重サブミット防止を実装するには、**クライアント側**と**サーバ側**の 2 つの方法を併用する。クライアント側はカスタムタグ（`<n:submit>`/`<n:button>` 等）の `allowDoubleSubmission="false"` 属性で JavaScript による再サブミット抑止を行う。サーバ側はトークンを発行・突合する方式で、トークンの設定（JSP は `<n:form useToken="true">`／JSP 以外は `@UseToken` インターセプタ）と、チェック（`@OnDoubleSubmission` インターセプタ）を組み合わせて実装する。

**根拠**:

1. クライアント側の二重サブミット防止（`libraries-tag.json#s21`）
   - 登録等コミットを伴うボタンのみ対象にする。
   ```jsp
   <n:submit type="button" name="register" value="登録" uri="./register"
             allowDoubleSubmission="false" />
   ```
   対応タグ: `submit` / `button` / `submitLink` / `downloadSubmit` / `downloadButton` / `downloadLink`。

2. サーバ側の二重サブミット防止 — トークン設定（`libraries-tag.json#s21`）
   - JSP 利用時は `form` タグの `useToken` 属性を指定。
   ```jsp
   <n:form useToken="true">
   ```
   入力画面と確認画面を共通化した場合、確認画面ではデフォルト `true` になる。

3. サーバ側の二重サブミット防止 — JSP 以外（Thymeleaf 等）での設定（`handlers-use-token.json#s3`）
   - アクションメソッドに `@UseToken` を付与し、フォームに hidden でトークンを明示的に埋め込む。
   ```java
   @UseToken
   public HttpResponse confirm(HttpRequest req, ExecutionContext ctx) { ... }
   ```
   ```xml
   <form th:action="@{/path/to/action}" method="post">
     <input type="hidden" name="nablarch_token" th:value="${nablarch_request_token}" />
   ```
   name 属性は `nablarch_token`、値はリクエストスコープの `nablarch_request_token` を参照。

4. サーバ側の二重サブミット防止 — トークンチェック（`web-application-getting-started-project-update.json#s2`、`libraries-tag.json#s21`）
   - 更新処理を行うアクションメソッドに `@OnDoubleSubmission` を付与。
   ```java
   @OnDoubleSubmission
   public HttpResponse update(HttpRequest request, ExecutionContext context) {
       Project targetProject = SessionUtil.delete(context, "project");
       UniversalDao.update(targetProject);
       return new HttpResponse(303, "redirect://completeOfUpdate");
   }
   ```

5. `BasicDoubleSubmissionHandler` によるデフォルト値設定（`handlers-on-double-submission.json#s4`）
   - `@OnDoubleSubmission` のデフォルト動作を共通化する場合、コンポーネントを登録する。
   ```xml
   <component name="doubleSubmissionHandler"
              class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
     <property name="path" value="/WEB-INF/view/error/userError.jsp" />
     <property name="messageId" value="DOUBLE_SUBMISSION_ERROR" />
     <property name="statusCode" value="200" />
   </component>
   ```

6. キー名等のカスタマイズ（`libraries-tag.json#s21`）
   - セッションスコープのキー: `webConfig` の `doubleSubmissionTokenSessionAttributeName`
   - リクエストスコープのキー: `doubleSubmissionTokenRequestAttributeName`
   - hidden の name 属性値: `doubleSubmissionTokenParameterName`
   - トークン生成ロジック: `TokenGenerator` を実装し `tokenGenerator` として登録（`libraries-tag.json#s45`）。デフォルトは `UUIDV4TokenGenerator`（36 文字ランダム）。

7. DB ベースのトークン保管（`libraries-tag.json#s22`）
   - デフォルトはセッション保管のため、スケールアウト時はスティッキーセッション／レプリケーションが必要。データベース保管の実装を使うと AP サーバ設定不要でトークンを共有できる。

8. テスト（`testing-framework-double-transmission.json#s1`）
   - リクエスト単体テストでは、テストショットの `LIST_MAP` に `isValidToken` カラムがあり、`false` を指定すればエラー発生で二重サブミット防止機能の動作を確認できる。

**注意点**:

- クライアント側／サーバ側は**併用**すべき。クライアント側のみだとリクエスト重複処理の恐れ、サーバ側のみだとダブルクリック時に二重サブミットエラーがユーザに返る恐れがある（`libraries-tag.json#s21`）。
- `@OnDoubleSubmission` と `BasicDoubleSubmissionHandler` の**どちらにも path の指定がない場合はシステムエラー**になる。サーバ側二重サブミット防止を使うアプリケーションでは必ずどちらかで path を指定すること（`handlers-on-double-submission.json#s4`）。
- サーバ側のトークンはセッションに保持されるため、同一ユーザでサーバ側二重サブミット防止を行う画面遷移（登録確認→登録完了など）を**複数ウィンドウ／複数タブで並行実行できない**。後から確認画面に遷移した側のみ継続でき、先に遷移した側は古いトークンで二重サブミットエラーになる（`libraries-tag.json#s21`）。
- 更新完了後はブラウザ更新での再実行を防ぐため、レスポンスをリダイレクトする運用が推奨されている（`web-application-getting-started-project-update.json#s2`）。

参照:
- `component/libraries/libraries-tag.json#s21`, `#s22`, `#s44`, `#s45`
- `component/handlers/handlers-use-token.json#s3`
- `component/handlers/handlers-on-double-submission.json#s4`
- `processing-pattern/web-application/web-application-getting-started-project-update.json#s1`, `#s2`
- `processing-pattern/web-application/web-application-getting-started-project-upload.json#s2`
- `processing-pattern/web-application/web-application-getting-started-project-bulk-update.json#s1`
- `processing-pattern/web-application/web-application-feature-details.json#s8`
- `development-tools/testing-framework/testing-framework-double-transmission.json#s1`
