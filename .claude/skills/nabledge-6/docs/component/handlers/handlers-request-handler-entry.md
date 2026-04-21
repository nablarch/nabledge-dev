# リクエストハンドラエントリ

## 概要

本ハンドラは、特定のリクエストパスのみ委譲先のハンドラを呼び出す特殊なハンドラである。
本ハンドラを使用することで、「ウェブアプリケーションで特定のURLのみハンドラの処理を行う」といった機能を、
ハンドラを修正することなく実現できる。

本ハンドラの主な用途は、 リソースマッピングハンドラ を使用した、「静的コンテンツのダウンロードを一括処理する」機能の実現である。
その他にも、 データベース接続管理ハンドラ や トランザクション制御ハンドラ と同時に使用することで
「特定のURLのみ使用するデータベース接続を変える」といった用途にも使用できる。

本ハンドラでは、以下の処理を行う。

* リクエストパスがマッチするか判定し、対象であれば委譲先のハンドラを呼び出す。


処理の流れは以下のとおり。

![](../../../knowledge/assets/handlers-request-handler-entry/flow.png)

## ハンドラクラス名

* `nablarch.fw.RequestHandlerEntry`

<details>
<summary>keywords</summary>

RequestHandlerEntry, nablarch.fw.RequestHandlerEntry, リクエストパスフィルタリング, 条件付きハンドラ呼び出し, 特定URLハンドラ

</details>

## モジュール一覧

```xml
<dependency>
  <groupId>com.nablarch.framework</groupId>
  <artifactId>nablarch-core</artifactId>
</dependency>
```

<details>
<summary>keywords</summary>

nablarch-core, com.nablarch.framework, モジュール依存関係

</details>

## 制約

なし。

<details>
<summary>keywords</summary>

制約なし

</details>

## 本ハンドラの使用例

本ハンドラを使用する際は、処理対象とするリクエストパスを指定する `requestPattern` プロパティと、
委譲先のハンドラを指定する `handler` プロパティを設定する。

リソースマッピングハンドラ を使用して、JPEGファイルの静的コンテンツをダウンロードする設定例を以下に示す。

```xml
<!-- 画像ファイルの静的リソースダウンロードを行うハンドラ -->
<component name="imgMapping"
           class="nablarch.fw.web.handler.ResourceMapping">
  <property name="baseUri" value="/"/>
  <property name="basePath" value="servlet:///"/>
</component>

<!-- ハンドラキュー構成 -->
<component name="webFrontController"
           class="nablarch.fw.web.servlet.WebFrontController">

  <property name="handlerQueue">
    <list>

      <component class="nablarch.fw.handler.GlobalErrorHandler"/>
      <component class="nablarch.fw.web.handler.HttpCharacterEncodingHandler"/>
      <component class="nablarch.common.io.FileRecordWriterDisposeHandler" />
      <component class="nablarch.fw.web.handler.HttpResponseHandler"/>

      <!-- 拡張子が ".jpg" である静的JPGファイルのダウンロードを行う設定 -->
      <component class="nablarch.fw.RequestHandlerEntry">
        <property name="requestPattern" value="//*.jpg"/>
        <property name="handler" ref="imgMapping"/>
      </component>

      <!--
        "*.jpg" で終わるJPEGファイルのダウンロード以外のリクエストでは、
        以下のハンドラの呼び出しが行われる
        -->
      <component-ref name="multipartHandler"/>
      <component-ref name="sessionStoreHandler" />
```

<details>
<summary>keywords</summary>

requestPattern, handler, ResourceMapping, WebFrontController, 静的コンテンツダウンロード, JPEGファイルダウンロード

</details>

## リクエストパターン指定のバリエーション

本ハンドラの使用例 の設定例からわかるとおり、本ハンドラに指定する `requestPattern` プロパティ
には、 `//*.jpg` のようなGlob式に似た書式での設定が行える。

ワイルドカードの設定例を以下に示す。


<table>
<thead>
<tr>
  <th>requestPattern</th>
  <th>リクエストパス</th>
  <th>結果</th>
</tr>
</thead>
<tbody>
<tr>
  <td>/</td>
  <td>/</td>
  <td>呼ばれる</td>
</tr>
<tr>
  <td></td>
  <td>/index.jsp</td>
  <td>呼ばれない</td>
</tr>
<tr>
  <td>/*</td>
  <td>/</td>
  <td>呼ばれる</td>
</tr>
<tr>
  <td></td>
  <td>/app</td>
  <td>呼ばれる</td>
</tr>
<tr>
  <td></td>
  <td>/app/</td>
  <td>呼ばれない (* は'/'にはマッチしない)</td>
</tr>
<tr>
  <td></td>
  <td>/index.jsp</td>
  <td>呼ばれない (* は'.'にはマッチしない)</td>
</tr>
<tr>
  <td>/app/\*.jsp</td>
  <td>/app/index.jsp</td>
  <td>呼ばれる</td>
</tr>
<tr>
  <td></td>
  <td>/app/admin</td>
  <td>呼ばれない</td>
</tr>
<tr>
  <td>/app/\*/test</td>
  <td>/app/admin/test</td>
  <td>呼ばれる</td>
</tr>
<tr>
  <td></td>
  <td>/app/test/</td>
  <td>呼ばれない</td>
</tr>
</tbody>
</table>


また、最後尾の’/’が’//’と重ねられていた場合、それ以前の文字列について前方一致すればマッチ成功と判定する記法も使用できる。

以下に設定例を示す。


<table>
<thead>
<tr>
  <th>requestPattern</th>
  <th>リクエストパス</th>
  <th>結果</th>
</tr>
</thead>
<tbody>
<tr>
  <td>/app//</td>
  <td>/</td>
  <td>呼ばれない</td>
</tr>
<tr>
  <td></td>
  <td>/app/</td>
  <td>呼ばれる</td>
</tr>
<tr>
  <td></td>
  <td>/app/admin/</td>
  <td>呼ばれる</td>
</tr>
<tr>
  <td></td>
  <td>/app/admin/index.jsp</td>
  <td>呼ばれる</td>
</tr>
<tr>
  <td>//\*.jsp</td>
  <td>/app/index.jsp</td>
  <td>呼ばれる</td>
</tr>
<tr>
  <td></td>
  <td>/app/admin/index.jsp</td>
  <td>呼ばれる</td>
</tr>
<tr>
  <td></td>
  <td>/app/index.html</td>
  <td>呼ばれない('\*.jsp'がマッチしない)</td>
</tr>
</tbody>
</table>

<details>
<summary>keywords</summary>

requestPattern, ワイルドカード, Glob式, 前方一致, パターンマッチング

</details>
