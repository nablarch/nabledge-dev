**結論**: Nablarch 6での二重サブミット防止は、**クライアント側**(JavaScriptでボタンの再クリックを抑止)と**サーバ側**(トークンによる重複リクエストの検出)の2つの方法があり、データベースにコミットを伴う画面では**両方を併用する**のが原則です。

**根拠**:

1. **クライアント側の二重サブミット防止**（カスタムタグの `allowDoubleSubmission` 属性）
   - `<n:submit>` / `<n:button>` / `<n:submitLink>` / `<n:downloadSubmit>` などのタグで `allowDoubleSubmission="false"` を指定すると、そのボタン/リンクについて1回目のサブミット以降はリクエストを送信しない（onclick書き換え + disabled属性）。
   ```jsp
   <n:submit type="button" name="register" value="登録" uri="./register"
             allowDoubleSubmission="false" />
   ```
   （参照: `libraries-tag.json#s21`）

2. **サーバ側の二重サブミット防止**（トークン方式）
   - **トークンの設定**（2通りの方法）:
     - JSP使用時は `<n:form>` の `useToken="true"` 属性を指定（入力画面と確認画面を共通化している場合は、確認画面ではデフォルトで `true`）。
     - JSP以外のテンプレートエンジン(Thymeleaf等)を使用している場合は、アクションメソッドに `@UseToken` アノテーションを付与し、フォームにhidden項目として埋め込む。
       ```java
       @UseToken
       public HttpResponse confirm(HttpRequest req, ExecutionContext ctx) { ... }
       ```
       ```html
       <form th:action="@{/path/to/action}" method="post">
         <input type="hidden" name="nablarch_token" th:value="${nablarch_request_token}" />
       ```
   - **トークンのチェック**: 処理を行うアクションメソッドに `@OnDoubleSubmission` アノテーションを付与する。`path` 属性で二重サブミット検出時の遷移先を指定する。
     ```java
     @OnDoubleSubmission(path = "/WEB-INF/view/error/userError.jsp")
     public HttpResponse register(HttpRequest req, ExecutionContext ctx) { ... }
     ```
   - **デフォルト値の設定**: アプリ全体のデフォルトを設定したい場合は `BasicDoubleSubmissionHandler` をコンポーネント定義に `doubleSubmissionHandler` という名前で追加し、`path` / `messageId` / `statusCode` を指定する。
     ```xml
     <component name="doubleSubmissionHandler"
                class="nablarch.common.web.token.BasicDoubleSubmissionHandler">
       <property name="path" value="/WEB-INF/view/error/userError.jsp" />
       <property name="messageId" value="DOUBLE_SUBMISSION_ERROR" />
       <property name="statusCode" value="200" />
     </component>
     ```
   （参照: `libraries-tag.json#s21`、`handlers-use-token.json#s3`、`handlers-on-double-submission.json#s3,s4`）

3. **単体テスト**
   - リクエスト単体テストでは、テストショットの `LIST_MAP` に `isValidToken` カラムを設け、`false` に設定することでサーバ側の二重サブミット防止機能の動作確認ができる。
   （参照: `testing-framework-double-transmission.json#s1`）

**注意点**:
- クライアント側のみだとリクエストが重複処理される恐れがあり、サーバ側のみだとダブルクリック時にユーザにエラーが返る恐れがあるため、**両方併用**する。
- `@OnDoubleSubmission` と `BasicDoubleSubmissionHandler` のどちらにも `path` 指定がない場合、二重サブミット判定時に遷移先不明でシステムエラーとなるため、必ずどちらかに `path` を指定する。
- サーバ側はトークンをセッションに格納するため、同一ユーザで複数ウィンドウ/タブから並行して「確認→完了」の画面遷移を行うことはできない（先に確認画面へ遷移した方は古いトークンになり二重サブミットエラーになる）。
- トークンのセッションキー(`/nablarch_session_token`)、リクエストスコープキー(`nablarch_request_token`)、hidden項目のname属性(`nablarch_token`)は、`WebConfig` コンポーネント設定で変更可能。
- トークンの発行処理をカスタマイズしたい場合は、`TokenGenerator` インタフェースを実装したクラスを `tokenGenerator` の名前でコンポーネント定義に登録する（デフォルトは `UUIDV4TokenGenerator`、36文字のランダム文字列）。
- クライアント側で二重サブミット発生時の振る舞いを追加したい場合は、JavaScriptで `nablarch_handleDoubleSubmission(element)` コールバック関数を実装する。

参照:
- `component/libraries/libraries-tag.json#s21` (クライアント/サーバ側の二重サブミット防止全体)
- `component/libraries/libraries-tag.json#s44` (クライアント側コールバック)
- `component/libraries/libraries-tag.json#s45` (TokenGeneratorのカスタマイズ)
- `component/handlers/handlers-use-token.json#s3` (@UseToken の使い方)
- `component/handlers/handlers-on-double-submission.json#s3` (@OnDoubleSubmission の使い方)
- `component/handlers/handlers-on-double-submission.json#s4` (BasicDoubleSubmissionHandler の設定)
- `development-tools/testing-framework/testing-framework-double-transmission.json#s1` (リクエスト単体テストでの検証)
