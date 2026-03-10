# HTTPアクセスログハンドラ

**公式ドキュメント**: [1](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/handlers/web/http_access_log_handler.html) [2](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/core/ThreadContext.html)

## ハンドラクラス名

:ref:`HTTPアクセスログ <http_access_log>` を出力するハンドラ。リクエスト処理開始時と完了時にアクセスログを出力する。

**クラス名**: `nablarch.common.web.handler.HttpAccessLogHandler`

*キーワード: HttpAccessLogHandler, nablarch.common.web.handler.HttpAccessLogHandler, HTTPアクセスログ, アクセスログ出力, リクエスト処理*

## モジュール一覧

**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-web</artifactId>
</dependency>
```

*キーワード: nablarch-fw-web, com.nablarch.framework, モジュール, 依存関係*

## 制約

- :ref:`thread_context_handler` より後ろに配置すること。ログ出力処理で `ThreadContext` の内容が必要なため。
- :ref:`http_error_handler` より前に配置すること。完了時ログにエラーコードが必要なため。
- セッションストアIDを出力する場合は :ref:`session_store_handler` より後ろに配置すること。詳細は :ref:`http_access_log-session_store_id` を参照。

*キーワード: ThreadContext, nablarch.core.ThreadContext, 配置順序, ハンドラ制約, スレッドコンテキスト, セッションストアID*

## アクセスログ出力内容の切り替え

出力内容の切り替え方法は :ref:`log` および :ref:`http_access_log` を参照すること。

*キーワード: アクセスログ切り替え, 出力内容設定, ログ設定*
