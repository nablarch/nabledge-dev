**結論**: Nablarch には `CsrfTokenVerificationHandler` という標準のCSRF対策ハンドラが用意されている。セッションに保存したCSRFトークンをリクエストと照合することで、外部サイトからの不正POSTを防ぐ。

**根拠**:

1. **ハンドラの追加**: `webFrontController` のハンドラキューに `csrfTokenVerificationHandler` を登録する。`sessionStoreHandler` および `nablarchTagHandler` より後に置くこと。
   ```xml
   <component name="webFrontController" class="nablarch.fw.web.servlet.WebFrontController">
     <property name="handlerQueue">
       <list>
         <component-ref name="sessionStoreHandler" />
         <component-ref name="nablarchTagHandler"/>
         <component-ref name="csrfTokenVerificationHandler"/>
       </list>
     </property>
   </component>
   <component name="csrfTokenVerificationHandler"
              class="nablarch.fw.web.handler.CsrfTokenVerificationHandler" />
   ```
   （`component/handlers/handlers-csrf_token_verification_handler.json:s4`）

2. **デフォルト動作**: トークンは UUID v4 で生成され、セッションストアに `nablarch_csrf-token` という名前で保存される。検証対象は `POST`/`PUT` 等（`GET`/`HEAD`/`TRACE`/`OPTIONS` は対象外）。クライアントはHTTPヘッダ `X-CSRF-TOKEN` またはHTTPパラメータ `csrf-token` でトークンを送信する。検証失敗時は HTTP 400 (BadRequest) を返す。（`component/handlers/handlers-csrf_token_verification_handler.json:s4`）

3. **ログイン時のトークン再生成**: ログイン処理でセッションストアを破棄・再生成しない場合は、`CsrfTokenUtil.regenerateCsrfToken` を呼び出してCSRFトークンを明示的に再生成すること。これを怠ると、ログイン前のトークンを悪用した攻撃が可能になる。（`component/handlers/handlers-csrf_token_verification_handler.json:s5`）

4. **RESTfulウェブサービスへの対応**: REST APIの場合は `CsrfTokenUtil` でトークンを取得し、プロジェクトのアーキテクチャに合わせてクライアントに渡す実装を別途行う。（`component/handlers/handlers-csrf_token_verification_handler.json:s4`）

**注意点**:
- リクエスト単体テスト時は正しい画面遷移を経由しないためCSRFトークン検証が失敗する。テスト環境ではハンドラを `NopHandler` に差し替えて無効化すること。
- トークンのヘッダ名・パラメータ名・セッションストア格納名は `nablarch.common.web.WebConfig` のプロパティで変更可能。
- ログイン時にセッションIDのみ再生成する実装では、CSRFトークンも必ず再生成すること。

参照: component/handlers/handlers-csrf_token_verification_handler.json:s4, component/handlers/handlers-csrf_token_verification_handler.json:s5, processing-pattern/web-application/web-application-feature_details.json:s19