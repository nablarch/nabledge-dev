**結論**: Nablarch に「監査ログ」という専用機能はないが、**HTTPアクセスログハンドラ**がその代替として設計されており、「誰が・いつ・何を」の要件を満たせる場合はアクセスログと証跡ログを兼用することが公式に想定されている。

**根拠**:

1. **Webアプリ（従来型）向け**: `http_access_log_handler` を使うと、リクエスト開始時・終了時にログを出力できる。フォーマットには `$userId$`（誰が）、`$startTime$` / `$endTime$`（いつ）、`$url$` / `$method$` / `$parameters$`（何を）のプレースホルダが用意されている。ドキュメントには「リクエストパラメータを含むリクエスト情報を出力することで証跡ログの要件を満たせる場合は、HTTPアクセスログと証跡ログを兼用できる」と明記されている。(`component/libraries/libraries-http_access_log.json:s1`)

2. **JAX-RS（REST API）向け**: `jaxrs_access_log_handler` も同様の仕組みを持ち、「リクエストパラメータを含めたリクエスト情報を出力することで、個別アプリケーションの証跡ログの要件を満たせる場合は、HTTPアクセスログと証跡ログを兼用することも想定している」とされている。さらに `$requestBody$` / `$responseBody$` プレースホルダでリクエスト／レスポンスのボディも記録できる。(`component/libraries/libraries-jaxrs_access_log.json:s1`, `component/libraries/libraries-jaxrs_access_log.json:s2`)

3. **ユーザID取得の前提条件**: `$userId$` の値は `ThreadContext` から取得されるため、ハンドラ構成に `thread_context_handler` が含まれており、かつアプリ側でセッションにユーザIDを設定している必要がある。(`component/libraries/libraries-http_access_log.json:s1`, `component/libraries/libraries-jaxrs_access_log.json:s2`)

**注意点**:
- 専用の「監査ログAPI」や「操作履歴テーブルへの自動書き込み」機能はない。あくまでHTTPアクセスログをファイルに出力する仕組みの転用である。
- アプリ固有の業務操作（例: 「〇〇レコードを更新した」）を細粒度で記録したい場合は、アクセスログでは不十分なことがあり、アプリ層での実装が別途必要になる。
- パスワード等の機密パラメータは `maskingPatterns` でマスク設定が必要。
- JAX-RSのデフォルトボディマスク (`JaxRsBodyMaskingFilter`) はJSON形式のみサポート。(`component/libraries/libraries-jaxrs_access_log.json:s2`)

参照: component/libraries/libraries-http_access_log.json:s1, component/libraries/libraries-jaxrs_access_log.json:s1, component/libraries/libraries-jaxrs_access_log.json:s2