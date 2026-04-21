# リクエスト単体テストの実施方法（HTTP同期応答メッセージ受信処理）

## 概要

リクエスト単体テストの実施方法は、\ real_request_test\ を参照すること。

本項では、\ real_request_test\ と記述方法が異なる箇所を解説する。

## テストデータの書き方

# テストショット一覧

LIST_MAPのデータタイプで１テストメソッド分のテストショット表を記載する。IDは、\ **testShots**\ とする。

HTTP同期応答メッセージ受信処理特有の内容について以下に示す。

| カラム名           説明 | 必須 |  |
|---|---|---|
| diConfig | HTTP同期応答メッセージ受信リクエスト単体テスト用のコンポーネント設定ファイルへのパスを記載する 必須 \|br\| (例：http-messaging-test-component-configuration.xml)。 |  |
| expectedStatusCode | JSON及びXMLデータ形式使用時は空欄にする。                                                      必須 |  |
| requestPath | アクションを実行するためのURLから、ホスト名を抜いた部分。                                      必須 \|br\| 例えばアクション実行のURLが「http://127.0.0.1/msgaction/ss11AC/RM11AC0102」であれば、 \|br\| 「/msgaction/ss11AC/RM11AC0102」となる。 |  |
| userId | 認証認可チェックに使用するユーザID                                                                     必須 |  |

> **Tip:** JSON及びXMLデータ形式使用時は、ステータスコードの比較も、Excelファイルのメッセージボディとの比較で行う。フレームワーク制御ヘッダもメッセージボディに含まれるためである。
# 各種準備データ

テスト実施に際して必要となる各種準備データの記述方法を説明する。
バッチでは、データベース、リクエストメッセージを準備する。

## リクエストメッセージ

テストの入力データとなる要求電文を記載する。以下に例を示す。

-----

MESSAGE=setUpMessages

// 共通情報（ディレクティブ、フレームワーク制御ヘッダ）

<table>
<tbody>
<tr>
  <td>text-encoding</td>
  <td>Windows-31J</td>
  <td></td>
</tr>
<tr>
  <td>requestId</td>
  <td>RM11AC0102</td>
  <td></td>
</tr>
</tbody>
</table>

// メッセージボディ

【XML】

<table>
<tbody>
<tr>
  <td>no</td>
  <td>XML1</td>
  <td>XML2</td>
  <td>XML3</td>
</tr>
<tr>
  <td></td>
  <td>全半角</td>
  <td>全半角</td>
  <td>全半角</td>
</tr>
</tbody>
<thead>
<tr>
  <th></th>
  <th>32767</th>
  <th>32767</th>
  <th>32767</th>
</tr>
</thead>
<tbody>
<tr>
  <td>1</td>
  <td><?xml version="1.0" encoding="UTF-8"?></td>
  <td>br</td>
  <td></td>
  <td><userId>0000000101</userId></td>
  <td>br</td>
  <td></td>
  <td></request></td>
</tr>
<tr>
  <td></td>
  <td><request></td>
  <td><resendFlag>0</resendFlag></td>
  <td>br</td>
  <td></td>
  <td></td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td></td>
  <td><dataKbn>0</dataKbn></td>
  <td></td>
  <td></td>
  <td></td>
  <td></td>
  <td></td>
</tr>
</tbody>
</table>

【JSON】

<table>
<tbody>
<tr>
  <td>no</td>
  <td>JSON</td>
</tr>
<tr>
  <td></td>
  <td>全半角</td>
</tr>
</tbody>
<thead>
<tr>
  <th></th>
  <th>32767</th>
</tr>
</thead>
<tbody>
<tr>
  <td>1</td>
  <td>{</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>"userId" : "0000000101",</td>
  <td>br</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>"resendFlag" : "0",</td>
  <td>br</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>"dataKbn" : "0",</td>
  <td>br</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>}</td>
  <td></td>
  <td></td>
</tr>
</tbody>
</table>

------

1. 先頭行

テスト対象リクエストに対する要求電文を準備する。名前は、\ `MESSAGE=setUpMessages`\ 固定とする。

2. 共通情報

名前の次行以降には以下の情報を記載する。これらの値は、リクエストメッセージの全メッセージで共通の値となる。

* ディレクティブ
* フレームワーク制御ヘッダ

書式は、key-value形式である。

<table>
<tbody>
<tr>
  <td>キー</td>
  <td>値</td>
</tr>
</tbody>
</table>

> **Important:** フレームワーク制御ヘッダの項目をPJで変更している場合、 以下のようにpropertiesファイルに `reader.fwHeaderfields` というキーでフレームワーク制御ヘッダ名を指定する必要がある。 .. code-block:: properties # フレームワーク制御ヘッダ名をカンマ区切りで指定する。 reader.fwHeaderfields=requestId,addHeader
3. メッセージボディ

フレームワーク制御ヘッダ以降のメッセージを記載する。


<table>
<thead>
<tr>
  <th>行</th>
  <th>記述内容</th>
  <th>備考</th>
</tr>
</thead>
<tbody>
<tr>
  <td>1行目</td>
  <td>フィールド名称</td>
  <td>先頭セルは"no"とする。</td>
</tr>
<tr>
  <td>2行目</td>
  <td>データタイプ</td>
  <td>先頭セルは空白</td>
</tr>
<tr>
  <td>3行目</td>
  <td>フィールド長</td>
  <td>先頭セルは空白</td>
</tr>
<tr>
  <td>4行目以降</td>
  <td>XMLデータ</td>
  <td>br</td>
  <td></td>
  <td>先頭セルは1からの通番</td>
  <td>br</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>および</td>
  <td>br</td>
  <td></td>
  <td>フィールドを跨いで記載することも可能</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>JSONデータ</td>
  <td></td>
  <td></td>
  <td></td>
  <td></td>
  <td></td>
</tr>
</tbody>
</table>

> **Tip:** JSON及びXMLデータ形式使用時は、1Excelシートに1テストケースのみ記述すること。 これはメッセージボディについて、Excelの各行の文字列長が同一であることを期待しているというNTFの制約によるものである。JSON及びXMLデータ形式は、要求電文の長さがリクエスト毎に異なるのが一般的なので、事実上1テストケースしか記述できない。
> **Important:** フィールド名称に\ **重複した名称は許容されない**\ 。 例えば、「氏名」というフィールドが2つ以上存在してはならない。 （通常、このような場合は「本会員氏名」と「家族会員氏名」のようにユニークなフィールド名称が付与される）
# 各種期待値

## レスポンスメッセージ

\ リクエストメッセージ\ と同じ。

ただし、名前が\ `MESSAGE=expectedMessages`\ となる。

応答電文のフィールド長は"-"(ハイフン)を設定する。

![](../../../knowledge/assets/testing-framework-http-real/http_real_test_data.png)
.. |br| raw:: html

<br />
