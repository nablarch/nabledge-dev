# メッセージングコンテキスト管理ハンドラ

**公式ドキュメント**: [1](https://nablarch.github.io/docs/LATEST/doc/application_framework/application_framework/handlers/mom_messaging/messaging_context_handler.html) [2](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/fw/messaging/handler/MessagingContextHandler.html) [3](https://nablarch.github.io/docs/LATEST/javadoc/nablarch/fw/messaging/MessagingProvider.html)

## ハンドラクラス名

後続のハンドラ及びライブラリで使用するためのMQ接続をスレッド上で管理するハンドラ。

処理:
1. MQ接続の取得
2. MQ接続の解放

**クラス**: `MessagingContextHandler`

<small>キーワード: MessagingContextHandler, nablarch.fw.messaging.handler.MessagingContextHandler, MOMメッセージング, MQ接続管理, スレッド管理</small>

## モジュール一覧

**モジュール**:
```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-messaging</artifactId>
</dependency>
```

<small>キーワード: nablarch-fw-messaging, com.nablarch.framework, モジュール, 依存関係</small>

## 制約

なし。

<small>キーワード: 制約, なし</small>

## MQの接続先を設定する

`messagingProvider` プロパティに `MessagingProvider` 実装クラスを設定してMQ接続を取得する。

```xml
<component class="nablarch.fw.messaging.handler.MessagingContextHandler">
  <property name="messagingProvider" ref="messagingProvider" />
</component>

<component name="messagingProvider"
    class="nablarch.fw.messaging.provider.JmsMessagingProvider">
</component>
```

<small>キーワード: MessagingProvider, nablarch.fw.messaging.MessagingProvider, JmsMessagingProvider, nablarch.fw.messaging.provider.JmsMessagingProvider, messagingProvider, MQ接続設定, プロバイダクラス設定</small>
