# リクエスト単体テスト（ウェブアプリケーション）

<details>
<summary>keywords</summary>

HttpRequestTestSupport, HttpResponse, execute, システムリポジトリ再初期化, コンポーネント設定ファイル, バックアップ復元, テスト連続実行

</details>

## 概要

リクエスト単体テスト(ウェブアプリケーション)では、内蔵サーバを使用してテストを行う。\
ここでは、リクエスト単体テストのテスト補助クラスと内蔵サーバの使用方法を記載する。

## 全体像

![](../../../knowledge/assets/testing-framework-02-RequestUnitTest/request_unit_test_structure.png)

## 主なクラス, リソース

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
  <td>テストクラス</td>
  <td>テストロジックを実装する。</td>
  <td>テスト対象クラス(Action)につき１つ作成</td>
</tr>
<tr>
  <td>テストデータ（Excelファイル）</td>
  <td>テーブルに格納する準備データや期待する結果、\</td>
  <td>テストクラスにつき１つ作成</td>
</tr>
<tr>
  <td></td>
  <td>HTTPパラメータなど、テストデータを記載する。</td>
  <td></td>
</tr>
<tr>
  <td>テスト対象クラス(Action)</td>
  <td>テスト対象のクラス</td>
  <td>取引につき1クラス作成</td>
</tr>
<tr>
  <td></td>
  <td>(Action以降の業務ロジックを実装する各クラスを含む)</td>
  <td></td>
</tr>
<tr>
  <td>DbAccessTestSupport</td>
  <td>準備データ投入などデータベースを使用するテストに\</td>
  <td>\－</td>
</tr>
<tr>
  <td></td>
  <td>必要な機能を提供する。</td>
  <td></td>
</tr>
<tr>
  <td>HttpServer</td>
  <td>内蔵サーバ。サーブレットコンテナとして動作し、\</td>
  <td>\－</td>
</tr>
<tr>
  <td></td>
  <td>HTTPレスポンスをファイル出力する機能を持つ。</td>
  <td></td>
</tr>
<tr>
  <td>HttpRequestTestSupport</td>
  <td>内蔵サーバの起動やリクエスト単体テストで必要とな\</td>
  <td>\－</td>
</tr>
<tr>
  <td></td>
  <td>る各種アサートを提供する。</td>
  <td></td>
</tr>
<tr>
  <td>AbstractHttpReqestTestSupport</td>
  <td>br</td>
  <td></td>
  <td>リクエスト単体テストをテンプレート化するクラス。リ</td>
  <td>\－</td>
</tr>
<tr>
  <td>BasicHttpReqestTestSupport</td>
  <td>クエスト単体テストのテストソース、テストデータを定</td>
  <td></td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>型化する</td>
  <td></td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>TestCaseInfo</td>
  <td>データシートに定義されたテストケース情報を格納する</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>クラス。</td>
  <td></td>
</tr>
</tbody>
</table>


上記のクラス群は、内蔵サーバも含め全て同一のJVM上で動作する。\
このため、リクエストやセッション等のサーバ側のオブジェクトを加工できる。\

## 前提事項

内蔵サーバを使用してHTMLダンプを出力するというリクエスト単体テストは、\
１リクエスト１画面遷移のシンクライアント型ウェブアプリケーションを対象としている。\
Ajaxやリッチクライアントを利用したアプリケーションの場合、\
HTMLダンプによるレイアウト確認は使用できない。

> **Tip:** 本書ではViewテクノロジにJSPを用いているが、\ サーブレットコンテナ上で画面全体をレンダリングする方式であれば、\ JSP以外のViewテクノロジでもHTMLダンプの出力が可能である。

## 構造

## BasicHttpRequestTestTemplate

各テストクラスのスーパクラス。\
本クラスを使用することで、リクエスト単体テストのテストソース、テストデータを定型化でき、\
テストソース記述量を大きく削減できる。

具体的な使用方法は、\ ../05_UnitTestGuide/02_RequestUnitTest/index\ を参照。

## AbstractHttpRequestTestTemplate

アプリケーションプログラマが直接使用することはない。\
テストデータの書き方を変えたい場合など、自動テストフレームワークを拡張する際に用いる。\

## TestCaseInfo

データシートに定義されたテストケース情報を格納するクラス。\
テストデータの書き方を変えたい場合は、本クラス及び前述のAbstractHttpRequestTestTemplateを継承する。

## HttpRequestTestSupport

リクエスト単体テスト用に用意されたスーパクラス。リクエスト単体テスト用のメソッドを用意している。


#### データベース関連機能

データベースに関する機能は、DbAccessTestSupportクラスに委譲することで実現している。
詳細は、\ 02_DbAccessTest\ を参照。

ただし、DbAccessTestSupportのうち以下のメソッドは、\
リクエスト単体テストでは不要であり、アプリケーションプログラマに誤解を与えないよう、\
意図的に委譲していない。

* public void beginTransactions()
* public void commitTransactions()
* public void endTransactions()
* public void setThreadContextValues(String sheetName, String id)


#### 事前準備補助機能

内蔵サーバへのリクエスト送信には、HttpRequestとExecutionContextのインスタンスが必要となる。\
HttpRequestTestSupportクラスでは、これらのオブジェクトを簡単に作成できるようメソッドを用意している。\


##### HttpRequest

```java
HttpRequest createHttpRequest(String requestUri, Map<String, String[]> params)
```
引数には、以下の値を引き渡す。

* テスト対象となるリクエストURI
* 上記で取得したリクエストパラメータ

本メソッドでは、受け取ったリクエストURIとリクエストパラメータを元に\
HttpRequestインスタンスを生成し、HTTPメソッドをPOSTに設定した上で返却する。\
HttpRequestにリクエストパラメータやURI以外のデータを設定したい場合は、\
本メソッド呼び出しにより取得したインスタンスに対してデータを設定するとよい。


##### ExecutionContext

ExecutionContextインスタンスを生成する。


```java
ExecutionContext createExecutionContext(String userId)
```
引数にはユーザIDを指定する。指定したユーザIDはセッションに格納される。\
これにより、そのユーザIDでログインしている状態となる。\






##### トークン発行

2重サブミット防止を施しているURIに対するテストを行うには、\
テスト実行前にトークンを発行しセッションに設定しておく必要がある。\
HttpRequestTestSupportにある下記のメソッドを呼び出すことで、\
トークンの発行およびセッションへの格納が行われる。

```java
void setValidToken(HttpRequest request, ExecutionContext context)
```
リクエスト単体実行時に、テストデータ上でトークンを設定するか否かを制御したい場合は、
以下のメソッドを使用する。

```java
void setToken(HttpRequest request, ExecutionContext context, boolean valid)
```
第3引数がbooleanになっており、真の場合は前述のsetValidTokenと同じ動作となる。
偽の場合は、セッションからトークン情報が除去される。以下のように使用することで、
テストクラスにトークンを設定するかどうかの分岐処理を書かなくてすむ。


```java
// 【説明】テストデータから取得したものとする。
String isTokenValid; 

// 【説明】"true"の場合はトークンが設定される。
setToken(req, ctx, Boolean.parseBoolean(isTokenValid)));
```

## 実行

HttpRequestTestSupportにある下記のメソッドを呼び出すことで、\
内蔵サーバが起動されリクエストが送信される。

```java
HttpResponse execute(String caseName, HttpRequest req, ExecutionContext ctx) 
```
引数には以下の値を引き渡す。

* テストケース説明
* HttpRequest
* ExectionContext

テストケース説明は、HTMLダンプ出力時のファイル名に使用される。
詳細は
HTMLダンプ出力ディレクトリ
を参照。



#### システムリポジトリの初期化

executeメソッド内部では、システムリポジトリの再初期化を行っている。\
これにより、クラス単体テストとリクエスト単体テストで設定を分けずに連続実行できる。

* 現在のシステムリポジトリの状態をバックアップ
* テスト対象のウェブアプリケーションのコンポーネント設定ファイルを用いてシステムリポジトリを再初期化
* executeメソッド終了時に、バックアップしたシステムリポジトリを復元する。


テスト対象のウェブアプリケーションに関する設定については、\
各種設定値\
を参照。

## 結果確認

#### メッセージ

HttpRequestTestSupportにある下記のメソッドを呼び出すことで、\
アプリケーション例外に格納されたメッセージが想定通りであることを確認する。

```java
void assertApplicationMessageId(String expectedCommaSeparated, ExecutionContext actual);
```
引数には、以下の値を引き渡す。

* 期待するメッセージ（複数ある場合はカンマ区切りで指定する。）
* 先に作成したExectionContext


例外が発生しなかった場合や、アプリケーション例外以外の例外が発生した場合は、\
アサート失敗となる。


> **Tip:** メッセージIDの比較はIDをソートした状態で行うので、テストデータを記載する際に 順序を気にする必要はない。

## HTMLダンプ出力

#### HTMLダンプ出力ディレクトリ

テストを実行すると、テスト用プロジェクトのルートディレクトリにtmp/html_dumpディレクトリが作成される。
その配下にテストクラス毎に同名のディレクトリが作成され、
そのテストクラスで実行されたテストケース説明と同名のHTMLダンプファイルが出力される。

また、HTMLダンプファイルが参照するHTMLリソース（スタイルシートや画像などのリソース）についても
このディレクトリに出力されるので、このディレクトリを保存することで、どの環境でもHTMLを同じように参照できる。

* html_dumpディレクトリが既に存在する場合は、html_dump_bkという名前でバックアップされる。


![](../../../knowledge/assets/testing-framework-02-RequestUnitTest/htmlDumpDir.png)

## 各種設定値

環境設定に依存する設定値については、コンポーネント設定ファイルで変更できる。\
設定可能な項目を以下に示す。

## コンポーネント設定ファイル設定項目一覧

<table>
<thead>
<tr>
  <th>設定項目名</th>
  <th>説明</th>
  <th>デフォルト値</th>
</tr>
</thead>
<tbody>
<tr>
  <td>htmlDumpDir</td>
  <td>HTMLダンプファイルを出力するディレクトリを指定する。</td>
  <td>./tmp/html_dump</td>
</tr>
<tr>
  <td>webBaseDir</td>
  <td>ウェブアプリケーションのルートディレクトリ\ [#]_\</td>
  <td>../main/web</td>
</tr>
<tr>
  <td>xmlComponentFile</td>
  <td>リクエスト単体テスト実行時に使用するコンポーネント設定ファイル\ [#]_\</td>
  <td>（なし）</td>
</tr>
<tr>
  <td>userIdSessionKey</td>
  <td>ログイン中ユーザIDを格納するセッションキー</td>
  <td>user.id</td>
</tr>
<tr>
  <td>exceptionRequestVarKey</td>
  <td>ApplicationExceptionが格納されるリクエストスコープのキー</td>
  <td>nablarch_application_error</td>
</tr>
<tr>
  <td>dumpFileExtension</td>
  <td>ダンプファイルの拡張子</td>
  <td>html</td>
</tr>
<tr>
  <td>httpHeader</td>
  <td>HttpRequestにHTTPリクエストヘッダとして格納される値</td>
  <td>Content-Type : application/x-www-form-urlencoded</td>
</tr>
<tr>
  <td></td>
  <td></td>
  <td>Accept-Language : ja JP</td>
</tr>
<tr>
  <td>sessionInfo</td>
  <td>セッションに格納される値</td>
  <td>（なし）</td>
</tr>
<tr>
  <td>htmlResourcesExtensionList</td>
  <td>ダンプディレクトリへコピーされるHTMLリソースの拡張子</td>
  <td>css、jpg、js</td>
</tr>
<tr>
  <td>jsTestResourceDir</td>
  <td>javascriptの自動テスト実行時に使用するリソースのコピー先ディレクトリ名</td>
  <td>../test/web</td>
</tr>
<tr>
  <td>backup</td>
  <td>ダンプディレクトリのバックアップOn/Off</td>
  <td>true</td>
</tr>
<tr>
  <td>htmlResourcesCharset</td>
  <td>CSSファイル(スタイルシート)の文字コード</td>
  <td>UTF-8</td>
</tr>
<tr>
  <td>checkHtml</td>
  <td>HTMLチェックの実施On/Off</td>
  <td>true</td>
</tr>
<tr>
  <td>htmlChecker</td>
  <td>HTMLチェックを行うオブジェクトを指定する。</td>
  <td>br</td>
  <td></td>
  <td>nablarch.test.tool.htmlcheck.Html4HtmlChecker</td>
</tr>
<tr>
  <td></td>
  <td>オブジェクトは nablarch.test.tool.htmlcheck.HtmlChecker</td>
  <td>クラスのインスタンス。</td>
  <td>br</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>インタフェースを実装している必要がある。</td>
  <td>br</td>
  <td></td>
  <td>クラスには htmlCheckerConfig で設定した設定</td>
</tr>
<tr>
  <td></td>
  <td>詳細は customize_html_check を参照。</td>
  <td>ファイルが適用される。</td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>htmlCheckerConfig</td>
  <td>HTMLチェックツールの設定ファイルパス。</td>
  <td>br</td>
  <td></td>
  <td>test/resources/httprequesttest/html-check-config.csv</td>
</tr>
<tr>
  <td></td>
  <td>htmlChecker を設定しなかった場合のみ有効。</td>
  <td></td>
  <td></td>
  <td></td>
</tr>
<tr>
  <td>ignoreHtmlResourceDirectory</td>
  <td>HTMLリソースの中でコピー対象外とするディレクトリ名のLIST</td>
  <td>（なし）</td>
</tr>
<tr>
  <td></td>
  <td>.. tip::</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>バージョン管理用のディレクトリ(.svnや.git)を対象外と設定すると</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>HTMLリソースコピー時のパフォーマンスが向上する。</td>
  <td></td>
</tr>
<tr>
  <td>tempDirectory</td>
  <td>JSPのコンパイル先ディレクトリ</td>
  <td>jettyのデフォルト動作に依存</td>
</tr>
<tr>
  <td></td>
  <td></td>
  <td>.. tip ::</td>
</tr>
<tr>
  <td></td>
  <td></td>
  <td>jettyのデフォルト動作では、.「/work」</td>
</tr>
<tr>
  <td></td>
  <td></td>
  <td>がコンパイル先ディレクトリとなる。</td>
</tr>
<tr>
  <td></td>
  <td></td>
  <td>「./work」が存在しない場合は、</td>
</tr>
<tr>
  <td></td>
  <td></td>
  <td>Tempフォルダ(Windownの場合は、ユーザのホーム</td>
</tr>
<tr>
  <td></td>
  <td></td>
  <td>ディレクトリ/Local Settings/Temp)が</td>
</tr>
<tr>
  <td></td>
  <td></td>
  <td>出力先となる。</td>
</tr>
<tr>
  <td>uploadTmpDirectory</td>
  <td>アップロードファイルを一時的に格納するディレクトリ。</td>
  <td>./tmp</td>
</tr>
<tr>
  <td></td>
  <td>テスト時に準備した、アップロード対象のファイルは本ディレクトリに</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>コピー後に処理される。</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>これにより、アクションでファイルを移動した場合でも、</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>本ディレクトリ配下のファイルが移動されるだけであり、</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>実態が移動されることを防ぐことができる。</td>
  <td></td>
</tr>
<tr>
  <td>dumpVariableItem</td>
  <td>HTMLダンプファイル出力時に可変項目を出力するか否かを設定する。</td>
  <td>false</td>
</tr>
<tr>
  <td></td>
  <td>ここでの可変項目とは以下の2種類を指す。</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>* JSESSIONID</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>* 2重サブミット防止用のトークン</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>これらの項目は、テスト実行毎に異なる値が設定される。</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>HTMLダンプ結果を毎回同じ結果にしたい場合は、本項目をOFF</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>(false)に設定する。（前回実行結果と差異がないことを確認したい場合等）</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>可変項目をそのままHTMLに出力する場合は、本項目をON</td>
  <td></td>
</tr>
<tr>
  <td></td>
  <td>(true)に設定する。</td>
  <td></td>
</tr>
</tbody>
</table>


.. [#]
PJ共通のwebモジュールが存在する場合、このプロパティにカンマ区切りでディレクトリを設定する。
複数指定された場合、先頭から順にリソースが読み込まれる。

以下に例を示す。

```xml
<component name="httpTestConfiguration" class="nablarch.test.core.http.HttpTestConfiguration">
  <property name="webBaseDir" value="/path/to/web-a/,/path/to/web-common"/>
```
この場合、web-a、web-commonの順にリソースが探索される。

.. [#]
この項目を設定した場合は、リクエスト送信直前に指定されたコンポーネント設定ファイルで初期化が行われる。\
通常は設定する必要はない。\
クラス単体テストとリクエスト単体テストとで設定を変える必要がある場合のみ、この項目を設定する。\

## コンポーネント設定ファイルの記述例

コンポーネント設定ファイル記述例を記載する。
設定値には、上記のデフォルト値に加え、セッション(sessionInfo)に以下の値を設定している。


<table>
<thead>
<tr>
  <th>キー</th>
  <th>値</th>
  <th>説明</th>
</tr>
</thead>
<tbody>
<tr>
  <td>commonHeaderLoginUserName</td>
  <td>"リクエスト単体テストユーザ"</td>
  <td>共通ヘッダ領域に表示するログインユーザ名</td>
</tr>
<tr>
  <td>commonHeaderLoginDate</td>
  <td>"20100914"</td>
  <td>共通ヘッダ領域に表示するログイン日時</td>
</tr>
</tbody>
</table>

```xml
<component name="httpTestConfiguration" class="nablarch.test.core.http.HttpTestConfiguration">
    <property name="htmlDumpDir" value="./tmp/html_dump"/>
    <property name="webBaseDir" value="../main/web"/>
    <property name="xmlComponentFile" value="http-request-test.xml"/>
    <property name="userIdSessionKey" value="user.id"/>
    <property name="httpHeader">
        <map>
            <entry key="Content-Type" value="application/x-www-form-urlencoded"/>
            <entry key="Accept-Language" value="ja JP"/>
        </map>
    </property>
    <property name="sessionInfo">
        <map>
            <entry key="commonHeaderLoginUserName" value="リクエスト単体テストユーザ"/>
            <entry key="commonHeaderLoginDate" value="20100914" />
        </map>
    </property>
    <property name="htmlResourcesExtensionList">
        <list>
            <value>css</value>
            <value>jpg</value>
            <value>js</value>
        </list>
    </property>
    <property name="backup" value="true" />
    <property name="htmlResourcesCharset" value="UTF-8" />    
    <property name="ignoreHtmlResourceDirectory">
        <list>
            <value>.svn</value>
        </list>
    </property>
    <property name="tempDirectory" value="webTemp" />
    <property name="htmlCheckerConfig"
      value="test/resources/httprequesttest/html-check-config.csv" />
</component>
```

## その他の設定

性能が高くないPCで開発をしており、リクエスト単体テスト実行速度を向上させたい場合は、\
以下の設定をすることで実行速度の改善が見込まれる。

> **Tip:** Pentium4、Pentinum Dual-Core等の処理性能が低いCPUを搭載したPCに効果がある。\ 逆に、これら以降のCPUを搭載したマシンでは、それほど効果的ではないので無理に設定する必要はない。
#### JVMオプションの指定

最大ヒープサイズと最小ヒープサイズを同一の値にすることで、\
ヒープサイズ拡張のオーバヘッドを回避できる。

-Xms256m -Xmx256m


また、クラスファイルの検証を省略することで実行速度が向上する。

-Xverfiy:none


Eclipseでの設定方法は以下のとおり。

* メニューバーより「実行」→「実行構成」を選択する。

* 「実行構成」ウィンドウが表示されるので、「引数」タブをクリックし、「VM引数」欄に前述のオプションを指定する。

![](../../../knowledge/assets/testing-framework-02-RequestUnitTest/vmoptions.png)
また、実行構成を変更しなくても、以下の方法でデフォルトのVM引数を設定できる。

* メニューバーより「ウィンドウ」→「設定」を選択する。 「設定」ウィンドウが表示されるので、「インストール済みのJRE」をする。

* インストール済みのJREの一覧が表示されるので、使用するJREを選択し「編集」ボタンを押下する。

![](../../../knowledge/assets/testing-framework-02-RequestUnitTest/installed_jre.png)
* 「VM引数」欄に前述のオプションを指定する。

![](../../../knowledge/assets/testing-framework-02-RequestUnitTest/edit_jre.png)
#### HTMLリソースコピーの抑止

リクエスト単体実行時に、以下のシステムプロパティを指定すると、 HTMLダンプ出力 時に、HTMLリソースコピーを抑止できる。

-Dnablarch.test.skip-resource-copy=true




CSSや画像ファイルなど静的なHTMLリソースを頻繁に編集しない場合は、
テスト実行の度にHTMLリソースをコピーする必要はないので、
このシステムプロパティを設定してもよい。


> **Important:** 本システムプロパティを指定した場合、HTMLリソースのコピーが行われなくなるので、 CSSなどのHTMLリソースを編集しても\ HTMLダンプ出力\ に反映されない。
> **Tip:** HTMLリソースディレクトリが存在しない場合は、システムプロパティの設定有無に関わらず、\ HTMLリソースのコピーが実行される。
Eclipseでの設定方法は以下のとおり。

* メニューバーより「実行」→「実行構成」を選択する。

* 「実行構成」ウィンドウが表示されるので、「引数」タブをクリックし、「VM引数」欄に前述のオプションを指定する。

![](../../../knowledge/assets/testing-framework-02-RequestUnitTest/skip_resource_copy.png)
.. |br| raw:: html

<br />
