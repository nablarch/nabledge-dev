# HTTPメッセージングレスポンス変換ハンドラ

## ハンドラクラス名

**クラス名**: `nablarch.fw.messaging.handler.HttpMessagingResponseBuildingHandler`

## モジュール一覧

**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-messaging-http</artifactId>
</dependency>
```

## 制約

- :ref:`http_response_handler` よりも後ろに設定すること。:ref:`http_response_handler` がこのハンドラで生成した `HTTPレスポンスオブジェクト` をクライアントに返却するため。

## レスポンスヘッダに設定される値

後続ハンドラで作成された応答電文オブジェクトをもとに以下のレスポンスヘッダを設定する。

| ヘッダ名 | 設定値 |
|---|---|
| Status-Code | 応答電文オブジェクトのステータスコード |
| Content-Type | フォーマッタのMIMEとcharsetを組み合わせた値（例: `application/json;charset=utf-8`） |
| X-Correlation-Id | 応答電文オブジェクトのヘッダに設定された `CorrelationId` の値 |

Content-TypeはフォーマッタのMIME（`DataRecordFormatterSupport#getMimeType()`）とcharset（`DataRecordFormatterSupport#getDefaultEncoding()`）から生成される。取得元は `InterSystemMessage.getFormatter()`。

> **重要**: このハンドラでは上記に記載のないレスポンスヘッダを設定できない。上記以外のレスポンスヘッダが必要な場合はプロジェクトでハンドラを作成すること。

## フレームワーク制御ヘッダのレイアウトを変更する

応答電文内のフレームワーク制御ヘッダの定義を変更する場合、`fwHeaderDefinition` プロパティにプロジェクトで拡張したフレームワーク制御ヘッダ定義を設定する。未設定時はデフォルトの `StructuredFwHeaderDefinition` が使用される。

フレームワーク制御ヘッダの詳細は :ref:`フレームワーク制御ヘッダ <http_system_messaging-fw_header>` を参照。

```xml
<component class="nablarch.fw.messaging.handler.HttpMessagingResponseBuildingHandler">
  <property name="fwHeaderDefinition">
    <component class="sample.SampleFwHeaderDefinition" />
  </property>
</component>
```
