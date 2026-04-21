# リクエスト単体テスト（同期応答メッセージ送信処理）

## 概要

# 概要

リクエスト単体テスト（同期応答メッセージ送信処理)では、
要求電文1件をキューに送信し、結果を同期的に受信する際の動作を擬似的に再現し、テストを行う。


> **Tip:** リクエスト単体テストそのものの概要については、 message_sendSyncMessage_test を参照。

## 全体像

バッチ処理の中で同期応答メッセージ送信処理を行う場合について、以下に全体像を示す。

![](../../../knowledge/assets/testing-framework-RequestUnitTest-send-sync/send_sync.png)
> **Tip:** 同期応答メッセージ送信処理のリクエスト単体テストを行う場合、テストケースの親クラスは以下の２クラスのうちのいずれかを継承しておく必要がある。 * StandaloneTestSupportTemplate * AbstractHttpRequestTestTemplate
# 主なクラス, リソース

<table>
<thead>
<tr>
  <th>名称</th>
  <th>役割</th>
  <th>作成単位</th>
</tr>
</thead>
<tbody>
<tr>
  <td>リクエスト単体\</td>
  <td>テストロジックを実装する。</td>
  <td>テスト対象クラス(Action)につき１つ作成</td>
</tr>
<tr>
  <td>テストクラス</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>Excelファイル\</td>
  <td>要求電文の期待値および応答電文などの</td>
  <td>テストクラスにつき１つ作成</td>
</tr>
<tr>
  <td>（テストデータ）</td>
  <td>テストデータを記載する。\</td>
  <td></td>
</tr>
<tr>
  <td>StandaloneTest\</td>
  <td>Action実行後に、MockMessagingContextを用いて</td>
  <td>\－</td>
</tr>
<tr>
  <td>SupportTemplate</td>
  <td>要求電文のアサートを実行する。</td>
  <td></td>
</tr>
<tr>
  <td>AbstractHttpRequest\</td>
  <td>Action実行後に、MockMessagingContextを用いて</td>
  <td>\－</td>
</tr>
<tr>
  <td>TestTemplate</td>
  <td>要求電文のアサートを実行する。</td>
  <td></td>
</tr>
<tr>
  <td>MessageSender</td>
  <td>同期応答メッセージ送信処理を行う際に\</td>
  <td>\－</td>
</tr>
<tr>
  <td></td>
  <td>使用するコンポーネント。</td>
  <td></td>
</tr>
<tr>
  <td>RequestTestingMessagingProvider</td>
  <td>リクエスト単体テストにおいて、\</td>
  <td>\－</td>
</tr>
<tr>
  <td></td>
  <td>要求電文のアサート機能および\</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>応答電文の生成・返却機能を提供する。</td>
  <td></td>
</tr>
<tr>
  <td>TestDataConvertor</td>
  <td>Excelから読み込んだテストデータを編集するための\</td>
  <td>\－</td>
</tr>
<tr>
  <td></td>
  <td>インタフェース。</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>必要に応じてデータ種別ごとにアーキテクトが実装する。</td>
  <td></td>
</tr>
</tbody>
</table>


# 構造

## StandaloneTestSupportTemplate

Action実行後に、MockMessagingContextを用いて、要求電文のアサートを行う機能。

同期応答メッセージ送信処理のリクエスト単体テストを行う場合は、処理の形態に合わせて
本クラスもしくはAbstractHttpRequestTestTemplateを実装したテストケースを使用する必要がある。

## AbstractHttpRequestTestTemplate

Action実行後に、MockMessagingContextを用いて、要求電文のアサートを行う機能。

同期応答メッセージ送信処理のリクエスト単体テストを行う場合は、処理の形態に合わせて
本クラスもしくはStandaloneTestSupportTemplateを実装したテストケースを使用する必要がある。

## RequestTestingMessagingProvider

要求電文のアサートおよび、応答電文の生成・返却する機能を提供するクラス。

また、Excelに記載された要求電文の期待値と、応答電文の読み込みも実行する。

本クラスは、以下の準備処理、結果確認機能を提供する。

<table>
<thead>
<tr>
  <th>準備処理</th>
  <th>結果確認</th>
</tr>
</thead>
<tbody>
<tr>
  <td>応答電文の生成</td>
  <td>要求電文のアサート</td>
</tr>
</tbody>
</table>

> **Tip:** 要求電文のアサートは、要求電文が送信されるたびに行うのではなく、Action実行後に一括で行う。

## MessageSender

同期応答メッセージ送信処理で使用するコンポーネント。

主に以下の機能を提供する。

* Actionなどの呼び出し元から渡されたパラメータから、要求電文を生成する。
* 要求電文を元にMockMessagingContextを実行する。
* MockMessagingContextから返却された応答電文をパースする。
* パース結果のオブジェクトを呼び出し元に返却する。

## TestDataConvertor

Excelから読み込んだテストデータを編集するためのインタフェース。
必要に応じてXMLやJSONなどのデータ種別ごとにアーキテクトが実装する。

実装クラスでは以下の機能を実装する。

* Excelから読み込んだデータを任意の値に編集する。
* 編集したデータを読み込むためのレイアウト定義データを動的に生成する。

本インタフェースを実装することで、例えばExcelに日本語で記述されたデータをURLエンコーディングする等の処理を追加可能である。

実装クラスは "TestDataConverter_<データ種別>" というキー名でテスト用のコンポーネント設定ファイルに登録する必要がある。


# テストデータ

同期応答メッセージ送信処理固有のテストデータについて説明する。

## 同期応答メッセージ送信処理

基本的な記述方法は、\
\ send_sync_request_write_test_data\
を参照。

> **Tip:** パディングおよびバイナリデータの扱いは、\ about_fixed_length_file\ と同様である。
