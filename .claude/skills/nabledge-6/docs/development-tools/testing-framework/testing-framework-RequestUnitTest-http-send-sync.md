# リクエスト単体テスト（HTTP同期応答メッセージ送信処理）

リクエスト単体テストのテスト方法は、\ RequestUnitTest_send_sync\ を参照すること。

本項では、\ RequestUnitTest_send_sync\ と異なる箇所を解説する。

ただし、以下のように読み替えること。

| 同期応答メッセージ送信 | HTTP同期応答メッセージ送信 |
|---|---|
| MockMessagingContext | MockMessagingClient |
| RequestTestingMessagingProvider | RequestTestingMessagingClient |

> **Tip:** リクエスト単体テストそのものの概要については、 message_httpSendSyncMessage_test を参照。
