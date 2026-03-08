# リクエスト単体テストの実施方法（応答不要メッセージ送信処理）

## 概要

> **重要**: アクションクラスに対する条件網羅や限界値テストは実施不要。

**テスト対象の成果物:**
- 電文のレイアウトを定義したフォーマット定義ファイル
- 電文送信テーブルから未送信データを取得するSELECT文
- 電文送信後に該当データのステータスを処理済みに更新するUPDATE文
- 電文送信失敗時に該当データのステータスをエラーに更新するUPDATE文

## テストクラスの書き方

テストクラス作成ルール:
1. テスト対象機能と同一パッケージ
2. クラス名は`<電文のリクエストID>RequestTest`
3. **クラス**: `nablarch.test.core.batch.BatchRequestTestSupport` を継承

## テストデータの書き方

応答不要メッセージ送信処理では応答電文が存在しないため、:ref:`message_sendSyncMessage_test` と比較して以下の設定は不要:

- testShots内の `responseMessage` 定義
- `RESPONSE_HEADER_MESSAGES` テーブル定義
- `RESPONSE_BODY_MESSAGES` テーブル定義

## 正常系のテスト

testShotsの定義に `KEY=messageRequestId`、`VALUE=メッセージのリクエストID` を追加する必要がある。

![正常系テストのtestShots設定](../../knowledge/development-tools/testing-framework/assets/testing-framework-delayed_send/delayed_send.png)

## 異常系のテスト(障害系のテスト)

testShotsの定義に `KEY=errorCase`、`VALUE=true` を設定する。異常系ケースでは電文が送信されないため送信電文の期待値設定は不要。

> **補足**: 異常系テストを実施する場合、応答不要メッセージ送信処理用共通アクションをテスト用アクションに切り替える必要がある。

本番設定:
```xml
<component name="requestPathJavaPackageMapping" class="nablarch.fw.handler.RequestPathJavaPackageMapping">
  <property name="basePackage" value="nablarch.fw.messaging.action.AsyncMessageSendAction" />
  <property name="immediate" value="false" />
</component>
```

テスト設定:
```xml
<component name="requestPathJavaPackageMapping" class="nablarch.fw.handler.RequestPathJavaPackageMapping">
  <property name="basePackage" value="nablarch.test.core.messaging.AsyncMessageSendActionForUt" />
  <property name="immediate" value="false" />
</component>
```
