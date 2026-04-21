# 電文応答制御ハンドラ

本ハンドラでは、後続ハンドラの処理結果である `ResponseMessage` オブジェクトの内容をもとに、
応答電文を作成し接続先システムに返却(送信)する。

本ハンドラでは、以下の処理を行う。

* 応答電文の送信処理を行う

処理の流れは以下のとおり。

![](../../../knowledge/assets/handlers-message-reply-handler/flow.png)

## ハンドラクラス名

* `nablarch.fw.messaging.handler.MessageReplyHandler`

<details>
<summary>keywords</summary>

MessageReplyHandler, nablarch.fw.messaging.handler.MessageReplyHandler, ResponseMessage, 電文応答制御ハンドラ, 応答電文送信

</details>

## モジュール一覧

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-fw-messaging</artifactId>
</dependency>
```

<details>
<summary>keywords</summary>

nablarch-fw-messaging, com.nablarch.framework, Mavenモジュール, 依存関係設定

</details>

## 制約

メッセージングコンテキスト管理ハンドラ よりも後ろに設定すること
本ハンドラは、応答電文を送信(メッセージキューへのプット)する。
このため、MQへの接続を確立する メッセージングコンテキスト管理ハンドラ より後ろに本ハンドラを設定する必要がある。

トランザクション制御ハンドラ との位置関係について
トランザクション制御ハンドラ との位置関係は、2相コミットを使用するか否かで変わる。

2相コミットを使用する場合
データベースのトランザクションとメッセージキュー(Jakarta Messaging)のトランザクションを、トランザクションマネージャで纏めてコミットする。
このため、トランザクション制御前に応答電文を送信する必要があり、 トランザクション制御ハンドラ より後ろに本ハンドラを設定する必要がある。

2相コミットを使用しない場合
本ハンドラが応答を送信する前に業務処理の結果を確定させる必要がある。
このため、 トランザクション制御ハンドラ は、本ハンドラより後ろに設定する必要がある。

<details>
<summary>keywords</summary>

messaging_context_handler, transaction_management_handler, ハンドラ配置順序, 2相コミット, トランザクション制御, メッセージキュー配置制約

</details>

## フレームワーク制御ヘッダの設定

応答電文内のフレームワーク制御ヘッダの定義を変更する場合には、プロジェクトで拡張したフレームワーク制御ヘッダの定義を設定する必要がある。
設定しない場合は、デフォルトの `StandardFwHeaderDefinition` が使用される。

フレームワーク制御ヘッダの詳細は、 フレームワーク制御ヘッダ を参照。

以下に設定例を示す。

```xml
<component class="nablarch.fw.messaging.handler.MessageReplyHandler">
  <!-- フレームワーク制御ヘッダの設定 -->
  <property name="fwHeaderDefinition">
    <component class="sample.SampleFwHeaderDefinition" />
  </property>
</component> 
```

<details>
<summary>keywords</summary>

StandardFwHeaderDefinition, nablarch.fw.messaging.StandardFwHeaderDefinition, fwHeaderDefinition, フレームワーク制御ヘッダ, カスタマイズ, mom_system_messaging-fw_header

</details>
