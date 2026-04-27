**結論**: Nablarch には二重サブミット防止の標準機能がある。アクションメソッドに `@OnDoubleSubmission` アノテーションを付与することで、同一トークンによる2回目以降のリクエストを検知して指定の遷移先へリダイレクトできる。

**根拠**:

1. **`@OnDoubleSubmission` アノテーション**（サーバ側で二重サブミットを検知）  
   アクションメソッドに `@OnDoubleSubmission(path = "/WEB-INF/view/error/userError.jsp")` を付与する。二重サブミットと判定された場合、`path` 属性で指定した画面へ遷移する。(`component/handlers/handlers-on_double_submission.json:s3`)

2. **JSP以外のテンプレートエンジン（Thymeleaf など）を使用する場合**  
   `@UseToken` アノテーションをアクションメソッドへ付与し、入力フォームに `<input type="hidden" name="nablarch_token" th:value="${nablarch_request_token}" />` を明示的に埋め込む必要がある。(`component/handlers/handlers-use_token.json:s3`)

3. **アプリケーションサーバをスケールアウトする場合**  
   通常のHTTPセッションベースのトークン管理ではスティッキーセッションやセッションレプリケーションが必要になる。DBにトークンを保存するライブラリを使うと、特別な設定なしに複数サーバ間でトークンを共有できる。(`component/libraries/libraries-db_double_submit.json:s1`)

**注意点**:
- DBトークン方式はユーザを識別せずにトークンを格納するため、**CSRF対策には使用できない**。DBトークン方式を採用する場合は、CSRF対策として別途 `csrf_token_verification_handler` を組み合わせる必要がある。(`component/libraries/libraries-db_double_submit.json:s1`)
- ブラウザを閉じるなどの操作でDBにトークンが残ることがあるため、期限切れトークンの定期削除が必要。(`component/libraries/libraries-db_double_submit.json:s1`)
- Thymeleaf などを使う場合は `@UseToken` による明示的なトークン埋め込みも必要。(`component/handlers/handlers-use_token.json:s3`)

参照: processing-pattern/web-application/web-application-feature_details.json:s8, component/handlers/handlers-on_double_submission.json:s3, component/handlers/handlers-use_token.json:s3, component/libraries/libraries-db_double_submit.json:s1