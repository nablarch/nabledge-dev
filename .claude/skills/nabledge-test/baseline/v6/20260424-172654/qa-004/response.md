**結論**: Nablarch 6 の二重サブミット防止は、**クライアント側**と**サーバ側**の2つの方法を併用して実装します。クライアント側は JavaScript により2回目以降のサブミットを防止し（カスタムタグの `allowDoubleSubmission="false"` 属性）、サーバ側はセッションで管理するトークンを使い、`@UseToken` で発行・`@OnDoubleSubmission` でチェックする仕組みを使用します。

**根拠**:

1. **クライアント側の二重サブミット防止**（JSPのカスタムタグで実装）
   - 対応タグ: `submit` / `button` / `submitLink` / `downloadSubmit` / `downloadButton` / `downloadLink`
   - 各タグの `allowDoubleSubmission="false"` で防止対象を指定
   ```jsp
   <n:submit type="button" name="back" value="戻る" uri="./back" />
   <n:submit type="button" name="register" value="登録" uri="./register"
             allowDoubleSubmission="false" />
   ```

2. **サーバ側の二重サブミット防止**（トークン方式）
   - **トークン設定（JSPの場合）**: `formタグ` の `useToken` 属性を指定
   ```jsp
   <n:form useToken="true">
   ```
   - **トークン設定（JSP以外 / Thymeleaf などテンプレートエンジン）**: アクションメソッドに `@UseToken` アノテーションを付与し、フォームに hidden でトークンを埋め込む
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
   - **トークンチェック**: チェック対象のアクションメソッドに `@OnDoubleSubmission` アノテーションを付与し、二重サブミット検出時の遷移先を `path` 属性で指定
   ```java
   @OnDoubleSubmission(path = "/WEB-INF/view/error/userError.jsp")
   public HttpResponse register(HttpRequest req, ExecutionContext ctx) {
       // 省略
   }
   ```
   - **デフォルト値の集約設定**: `BasicDoubleSubmissionHandler` を `doubleSubmissionHandler` という名前でコンポーネント定義に追加し、`path` / `messageId` / `statusCode` を設定可能
   ```xml
   <component name="doubleSubmissionHandler"
              class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
     <property name="path" value="/WEB-INF/view/error/userError.jsp" />
     <property name="messageId" value="DOUBLE_SUBMISSION_ERROR" />
     <property name="statusCode" value="200" />
   </component>
   ```
   - **トークンの各種キー（セッションキー/リクエストキー/name属性）変更**: `nablarch.common.web.WebConfig` のプロパティ（`doubleSubmissionTokenSessionAttributeName` など）で変更可能
   - **トークン発行処理の変更**: `TokenGenerator` インタフェースを実装し、`tokenGenerator` という名前でコンポーネント定義に追加（デフォルトは UUIDV4TokenGenerator）

**注意点**:
- クライアント側とサーバ側はどちらか一方ではなく **両方併用** が推奨。クライアント側のみだと重複処理の恐れ、サーバ側のみだとダブルクリック時にユーザへ結果が返らない恐れがある。
- `@OnDoubleSubmission` と `BasicDoubleSubmissionHandler` の**どちらも path を指定していない場合**はシステムエラーになるので、必ずどちらかを指定すること。
- サーバ側のトークンはセッションで管理されるため、同一ユーザが **複数ウィンドウ/複数タブで並行して** 二重サブミット防止対象の画面遷移を行うことはできない（後に確認画面に遷移した方のみ処理継続可能）。
- サーバ側防止は「データベースにコミットを伴う処理を要求する画面」で使用する。
- クライアント側防止では、サブミット後にサーバ側からレスポンスが返らず中止ボタンを押した場合、ボタンは disabled のままになるため、別のボタン/リンクで継続する必要がある。

参照:
- libraries-tag.json#s21 (クライアント側/サーバ側の二重サブミット防止の全体像)
- handlers-use-token.json#s3 (UseToken インターセプタ)
- handlers-on-double-submission.json#s3 (OnDoubleSubmission インターセプタ)
- handlers-on-double-submission.json#s4 (BasicDoubleSubmissionHandler のデフォルト設定)
- libraries-tag-reference.json#s6 (formタグの useToken 属性)
- libraries-tag.json#s45 (TokenGenerator による発行処理変更)
