# HTTPアクセスログ（RESTfulウェブサービス用）ハンドラ

<details>
<summary>keywords</summary>

アクセスログ出力内容切り替え, ログ設定, jaxrs_access_log, log

</details>

HTTPアクセスログ（RESTfulウェブサービス用） を出力するハンドラ。

本ハンドラでは、以下の処理を行う。

* リクエスト処理開始時のアクセスログを出力する
* リクエスト処理完了時のアクセスログを出力する

処理の流れは以下のとおり。

![](../../../knowledge/assets/handlers-jaxrs-access-log-handler/flow.png)

## ハンドラクラス名

* `nablarch.fw.jaxrs.JaxRsAccessLogHandler`

<details>
<summary>keywords</summary>

HTTPアクセスログ, RESTfulウェブサービス, アクセスログ出力タイミング, リクエスト処理開始, リクエスト処理完了

</details>

## モジュール一覧

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-jaxrs</artifactId>
</dependency>
```

<details>
<summary>keywords</summary>

JaxRsAccessLogHandler, nablarch.fw.jaxrs.JaxRsAccessLogHandler, HTTPアクセスログハンドラ, RESTfulウェブサービス

</details>

## 制約

スレッドコンテキスト変数管理ハンドラ より後ろに配置すること
このハンドラから呼ばれるログ出力の処理内では、通常 `ThreadContext` に保持する内容が必要となる。
このため、 スレッドコンテキスト変数管理ハンドラ より後ろに配置する必要がある。

HTTPエラー制御ハンドラ より前に配置すること
また、完了時のログ出力にはエラーコードが必要となるため、 HTTPエラー制御ハンドラ より前に配置する必要がある。

セッションストアIDを出力する場合は セッション変数保存ハンドラ より後ろに配置すること
詳細は セッションストアIDについて を参照。

<details>
<summary>keywords</summary>

nablarch-fw-jaxrs, com.nablarch.framework, Mavenモジュール, 依存関係

</details>

## アクセスログ出力内容の切り替え

アクセスログの出力内容の切り替え方法は、 ログ出力 および HTTPアクセスログ（RESTfulウェブサービス用）の出力 を参照すること。

<details>
<summary>keywords</summary>

ハンドラ配置順序, ThreadContext, nablarch.core.ThreadContext, エラーコード, セッションストアID, thread_context_handler, http_error_handler, session_store_handler

</details>
