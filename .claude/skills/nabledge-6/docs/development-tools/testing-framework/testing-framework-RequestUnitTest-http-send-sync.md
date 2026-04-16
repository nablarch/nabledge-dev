# リクエスト単体テスト（HTTP同期応答メッセージ送信処理）

## 概要

リクエスト単体テストのテスト方法は、\ RequestUnitTest_send_sync\ を参照すること。

本項では、\ RequestUnitTest_send_sync\ と異なる箇所を解説する。

ただし、以下のように読み替えること。

<table>
<thead>
<tr>
  <th>同期応答メッセージ送信</th>
  <th>HTTP同期応答メッセージ送信</th>
</tr>
</thead>
<tbody>
<tr>
  <td>MockMessagingContext</td>
  <td>MockMessagingClient</td>
</tr>
<tr>
  <td>RequestTestingMessagingProvider</td>
  <td>RequestTestingMessagingClient</td>
</tr>
</tbody>
</table>

> **Tip:** リクエスト単体テストそのものの概要については、 `message_httpSendSyncMessage_test` を参照。
