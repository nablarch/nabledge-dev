# リクエスト単体テスト（メッセージ受信処理）

## 概要

# 概要

リクエスト単体テスト（メッセージ受信処理)では、
要求電文1件を受信したときの動作を擬似的に再現し、テストを行う。

## 全体像

![](../../../knowledge/assets/testing-framework-RequestUnitTest-real/real_request_test_class.png)
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
  <td>テーブルに格納する準備データや期待する結果、\</td>
  <td>テストクラスにつき１つ作成</td>
</tr>
<tr>
  <td>（テストデータ）</td>
  <td>入力ファイルなど、テストデータを記載する。</td>
  <td></td>
</tr>
<tr>
  <td>StandaloneTest\</td>
  <td>バッチやメッセージング処理などコンテナ外で動作する\</td>
  <td>\－</td>
</tr>
<tr>
  <td>SupportTemplate</td>
  <td>処理のテスト実行環境を提供する。</td>
  <td></td>
</tr>
<tr>
  <td>MessagingRequest\</td>
  <td>同期応答メッセージ受信処理のリクエスト単体\</td>
  <td>\－</td>
</tr>
<tr>
  <td>TestSupport</td>
  <td>テストで必要となるテスト準備機能、\</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>各種アサートを提供する。</td>
  <td></td>
</tr>
<tr>
  <td>MessagingReceive\</td>
  <td>応答不要メッセージ受信処理のリクエスト単体テストで\</td>
  <td>\－</td>
</tr>
<tr>
  <td>TestSupport</td>
  <td>必要となるテスト準備機能、各種アサートを提供する。</td>
  <td></td>
</tr>
<tr>
  <td>TestShot</td>
  <td>データシートに定義されたテストケース1件分の情報を\</td>
  <td>\－</td>
</tr>
<tr>
  <td></td>
  <td>格納するクラス。</td>
  <td></td>
</tr>
<tr>
  <td>MainForRequestTesting</td>
  <td>テスト用メインクラス。テスト実行時の差分を吸収する。</td>
  <td>\－</td>
</tr>
<tr>
  <td>DbAccessTestSupport</td>
  <td>DB準備データ投入などデータベースを使用するテストに\</td>
  <td>\－</td>
</tr>
<tr>
  <td></td>
  <td>必要な機能を提供する。</td>
  <td></td>
</tr>
<tr>
  <td>MQSupport</td>
  <td>電文作成などメッセージングのテストに\</td>
  <td>\－</td>
</tr>
<tr>
  <td></td>
  <td>必要な機能を提供する。</td>
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

バッチやメッセージング処理などコンテナ外で動作する処理のテスト実行環境を提供する。
テストデータを読み取り、全テストショット(\ TestShot \ )を実行する。

## TestShot

1テストショットの情報保持とテストショットを実行する。\
テストショットは以下の要素で成り立っている。

* 入力データの準備
* メインクラス起動
* 出力結果の確認

バッチやメッセージング処理などコンテナ外で動作する処理のテストにおいて
共通の準備処理、結果確認機能を提供する。

<table>
<thead>
<tr>
  <th>準備処理</th>
  <th>結果確認</th>
</tr>
</thead>
<tbody>
<tr>
  <td>データベースのセットアップ</td>
  <td>データベース更新内容確認</td>
</tr>
<tr>
  <td></td>
  <td>ログ出力結果確認</td>
</tr>
<tr>
  <td></td>
  <td>ステータスコード確認</td>
</tr>
</tbody>
</table>


入力データ準備や結果確認ロジックはバッチや各種メッセージング処理ごとに異なるので\
方式に応じたカスタマイズが可能となっている。

## MessagingRequestTestSupport

同期応答メッセージ受信処理テスト用のスーパクラス。\
アプリケーションプログラマは本クラスを継承してテストクラスを作成する。

本クラスは、\ TestShot \が提供する準備処理、結果確認に以下の機能を追加する。

<table>
<thead>
<tr>
  <th>準備処理</th>
  <th>結果確認</th>
</tr>
</thead>
<tbody>
<tr>
  <td>要求電文の作成</td>
  <td>応答電文の内容確認</td>
</tr>
</tbody>
</table>


本クラスを使用することで、リクエスト単体テストのテストソース、テストデータを定型化でき、\
テストソース記述量を大きく削減できる。

具体的な使用方法は、\ ../05_UnitTestGuide/02_RequestUnitTest/real\ を参照。

> **Tip:** 本クラスは、入力データをキューにPUTする用途で、main側のコンポーネント設定ファイルを読み込む。 その際、\ `nablarch.fw.messaging.FwHeaderDefinition`\ 実装クラスは、 \ `fwHeaderDefinition`\ という名前で登録されていなければならない。 これ以外の名称を使用する場合は、本クラスのgetFwHeaderDefinitionName()をオーバライドすることにより 本クラスが使用するFwHeaderDefinitionコンポーネント名を変更できる。

## MessagingReceiveTestSupport

応答不要メッセージ処理テスト用のスーパクラス。\
アプリケーションプログラマは本クラスを継承してテストクラスを作成する。

本クラスは、\ TestShot \が提供する準備処理、結果確認に以下の機能を追加する。

<table>
<thead>
<tr>
  <th>準備処理</th>
</tr>
</thead>
<tbody>
<tr>
  <td>要求電文の作成</td>
</tr>
</tbody>
</table>

本クラスを使用することで、リクエスト単体テストのテストソース、テストデータを定型化でき、\
テストソース記述量を大きく削減できる。

具体的な使用方法は、\ ../05_UnitTestGuide/02_RequestUnitTest/delayed_receive\ を参照。

## MainForRequestTesting

リクエスト単体テスト用のメインクラス。\
本番用メインクラスとの主な差異は以下の通り。

* テスト用のコンポーネント設定ファイルからシステムリポジトリを初期化する。
* 常駐化機能を無効化する。

## MQSupport

メッセージに関する操作を提供するクラス。
主に以下の機能を提供する。

* テストデータから要求電文を作成し、受信キューにPUTする。
* 応答電文を送信キューからGETし、テストデータの期待値と内容を比較する。

## TestDataConvertor

Excelから読み込んだテストデータを編集するためのインタフェース。
必要に応じてXMLやJSONなどのデータ種別ごとにアーキテクトが実装する。

実装クラスでは以下の機能を実装する。

* Excelから読み込んだデータに対して任意で編集する。
* 編集したデータを読み込むためのレイアウト定義データを動的に生成する。

本インタフェースを実装することで、例えばExcelに日本語で記述されたデータをURLエンコーディングする等の処理を追加可能である。

実装クラスは "TestDataConverter_<データ種別>" というキー名でテスト用のコンポーネント設定ファイルに登録する必要がある。


# テストデータ

メッセージング処理固有のテストデータについて説明する。

## メッセージ

基本的な記述方法は、\
../05_UnitTestGuide/02_RequestUnitTest/real
を参照。

> **Tip:** パディングおよびバイナリデータの扱いは、\ about_fixed_length_file\ と同様である。
