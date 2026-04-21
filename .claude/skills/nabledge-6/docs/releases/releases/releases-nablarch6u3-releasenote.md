# 

<details>
<summary>keywords</summary>

6u3, リリースノート, EntityResponse, 型パラメータ, BeanUtil, OffsetDateTime, マルチパート, BodyConverter, JSON読み取り, BeanValidationStrategy, sortMessages, Nablarch OpenAPI Generator, nablarch-openapi-generator, 使用不許可APIチェック, Java21, Tomcat脆弱性, Base64Util, RFC4648, JaxRsHandlerListFactory, nablarch-fw-jaxrs, nablarch-core-beans, nablarch-core-dataformat, nablarch-fw-web, nablarch-unpublished-api-checker, ResumeDataReader, ResumePointManager, FastTableIdGenerator, TableIdGenerator, Published, nablarch-router-adaptor, nablarch-fw-batch, nablarch-common-idgenerator-jdbc, nablarch-common-dao, nablarch-common-databind, sql-executor, jQuery, Bootstrap, nablarch-jaxrs-adaptor, nablarch-jersey-adaptor, nablarch-resteasy-adaptor, nablarch-jackson-adaptor, @Path, gsp-dba-maven-plugin, nablarch-core, nablarch-biz-sample-all, バージョンアップ, nablarch-bom, pom.xml, dependencyManagement, Mavenビルド, multipart, JerseyJaxRsHandlerListFactory, ResteasyJaxRsHandlerListFactory, multipartHandler, rest-component-configuration.xml, ファイルアップロード, filepath-for-webui.xml, multipart.xml, contentLengthLimit, uploadFileTmpDir, RESTfulウェブサービス, 6u2からのバージョンアップ, autoCleaning, webFrontController, nablarch.filePathSetting.basePathSettings.output

</details>

■Nablarch 6u3 リリースノート
6u2からの変更点を記載しています。
コンテンツ  No.  分類  リリース
区分  タイトル  概要  修正後のバージョン
（※1）  不具合の起因バージョン
（※2）  システムへの
影響の可能性
（※3）  システムへの影響の可能性の内容と対処  参照先  JIRA issue
(※4)
モジュール  Nablarch
アプリケーションフレームワーク
オブジェクトコード、ソースコード  1  RESTfulウェブサービス  変更  親クラス・インタフェースでのリソース定義に対応
(No.24.OpenAPI対応に伴う変更)  OpenAPIドキュメントから生成したインタフェースを使用してアクションクラスを実装できるように、インターフェースや親クラスでのリソース定義を引き継ぐように対応しました。

@PathなどのJakarta RESTful Web Servicesのアノテーションを使ってアクションクラスを実装している場合に、以下の条件でアクションクラスが実装しているインターフェースや親クラスのリソース定義を引き継ぎます。
　・アクションクラスが親クラスを継承またはインターフェースを実装している
　・親クラスまたはインターフェースに@Pathアノテーションが注釈されている
　・親クラスまたはインターフェースにHTTPメソッドが定義されている

また、本対応にはルーティングアダプタも修正する必要があったため、合わせて対応しました。  nablarch-fw-jaxrs 2.2.0
nablarch-router-adaptor 2.2.0  なし  https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/web_service/rest/feature_details/resource_signature.html  NAB-618
https://nablarch.github.io/docs/6u3/doc/application_framework/adaptors/router_adaptor.html
2  RESTfulウェブサービス  変更  EntityResponseの型パラメータ追加
(No.24.OpenAPI対応に伴う変更)  OpenAPIドキュメントとのマッピングに対応するため、EntityResponseに型パラメータを追加しました。
これにより、どのようなエンティティの型をレスポンスとしているかをより明確に表現できるようになりました。  nablarch-fw-jaxrs 2.2.0  あり(開発)  すでにEntityResponseを使用している個所については型を指定していない状態になるため、コンパイル時に以下のメッセージが出力されるようになります。また、設定によってはIDEで同様の警告が出力されるようになります。

[INFO] (該当クラス)の操作は、未チェックまたは安全ではありません。

解消しなくても動作に影響はありませんが、EntityResponseを使用している個所で明示的に型を指定すると、メッセージおよび警告は解消されます。  https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/web_service/rest/feature_details/resource_signature.html  NAB-619
3  BeanUtil  変更  Date and Time APIサポート拡充
(No.24.OpenAPI対応に伴う変更)  OpenAPIドキュメントとのマッピングに対応するため、Date and Time APIのサポートを拡充し、OffsetDateTimeのサポートを追加しました。  nablarch-core-beans 2.3.0  なし  https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/libraries/bean_util.html  NAB-620
4  RESTfulウェブサービス  変更  マルチパート用のBodyConverter追加
(No.24.OpenAPI対応に伴う変更)  OpenAPIドキュメントとのマッピングに対応するため、Content-Typeがmultipart/form-dataのリクエストに対応するBodyConverterを追加しました。  nablarch-fw-jaxrs 2.2.0  なし  https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/web_service/rest/feature_details/resource_signature.html  NAB-621
5  BeanUtil  変更  MapからBeanへ移送するメソッドのパフォーマンス改善  MapからBeanへ移送する際、ネストしたオブジェクト数が多い場合に処理が遅くなる事象が発生していたので、修正しました。  nablarch-core-beans 2.3.0  なし  https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/libraries/bean_util.html  NAB-634
6  汎用データフォーマット  不具合  JSONの読み取りに失敗する問題を修正  JSON内に含まれる値（""で囲われた項目）がJSON構文で意味を持つ区切り文字（:、[、{、, の4つ）のみで、かつその後にデータが続く場合、値とJSON構文の区切り文字の区別ができずに失敗していました。

①NGになる例（":"の後にデータが続く）：
  {"key1": ":", "key2": "value2"}

②OKになる例（":"の後にデータが続かない）：
  {"key1": ":"}

NGになっていた例も、正常に値として解析できるように修正しました。  nablarch-core-dataformat 2.0.3  1.3.1  5u19  あり(本番)  概要の①のようにJSONの区切り文字のみが値になるデータを解析できるようになります。
本来は値として解析できることが正しい挙動であるため影響が無い想定ですが、もしこのようなJSONを読み込めるようになることでシステム影響がある場合、値の確認をして受け入れないようにするなどの修正を行ってください。  https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/libraries/data_io/data_format.html  NAB-639
7  Bean Validation  変更  BeanValidationStrategyのバリデーション処理をカスタマイズできるように修正  BeanValidationStrategyをカスタマイズしやすくなるよう、公開APIを見直しました。
それに伴い、バリデーションエラーのメッセージをソートするsortMessagesメソッドをオーバーライド可能にするため、static修飾子を除去しました。  nablarch-fw-web 2.3.0  なし  https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/libraries/validation/bean_validation.html  NAB-640
8  公開API  変更  公開APIの追加  解説書で継承を案内しているAPIの中で公開APIになっていないものがあったため、公開APIを追加しました。  nablarch-common-dao 2.3.0
nablarch-common-databind 2.1.0  なし  -  NAB-641
APIドキュメント  9  Nablarchバッチアプリケーション  変更  ResumeDataReaderのJavadoc改善  ResumeDataReaderが内部的に使用するResumePointManagerは初期化が必要ですが、
この点をResumeDataReaderに関する説明から読み取りづらかったため、ResumeDataReaderのJavadocに追記しました。  nablarch-fw-batch 2.0.1  なし  https://nablarch.github.io/docs/6u3/javadoc/nablarch/fw/reader/ResumeDataReader.html  NAB-629
10  サロゲートキーの採番  変更  TableIdGeneratorのJavadoc改善  採番の際に独立したトランザクションを用いるFastTableIdGeneratorは初期化が必要ですが、Javadoc上でそれがわからなかったため、その旨を追記しました。
また類似のコンポーネントであるTableIdGeneratorのJavadocにも、記述を合わせるため同様の更新を行っています。  nablarch-common-idgenerator-jdbc 2.0.1  なし  https://nablarch.github.io/docs/6u3/javadoc/nablarch/common/idgenerator/FastTableIdGenerator.html  NAB-629
11  汎用ユーティリティ  変更  Base64UtilのJavadoc・解説書改善  Base64UtilはRFC4648の「4. Base 64 Encoding」に準拠していますが、Javadoc上で明記できていなかったため、その旨を追記しました。

また、Java8以降ではBase64エンコーディングを行う標準APIが提供されており、Base64Utilを使用せずとも同様の処理を行えます。
Base64Utilを使用する必要性が小さくなったため、Javadocで標準APIを案内し、Base64Utilは後方互換性のための位置付けとしました。
そのため、Base64Utilは後方互換のために存在していることを解説書に追記しました。
※現在Base64Utilを使用している個所を標準APIに置換する必要はありません。  nablarch-core-2.2.1  なし  https://nablarch.github.io/docs/6u3/javadoc/nablarch/core/util/Base64Util.html  NAB-626
https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/libraries/utility.html
12  公開API  変更  PublishedアノテーションのJavadoc改善  PublishedアノテーションのJavadocで、オーバーライド可能なメソッドは公開APIとしていることについて追記しました。  nablarch-core-2.2.1  なし  https://nablarch.github.io/docs/6u3/javadoc/nablarch/core/util/annotation/Published.html  NAB-640
解説書  13  コンポーネントの初期化  変更  初期化が必要なコンポーネントに対する説明の改善  コンポーネントとして使用することを想定して提供しているクラスのうち、初期化が必要であるにも関わらず解説書への記載がないものがあったので、初期化が必要な旨や設定例を追記しました。

・Nablarchが提供するライブラリ
　・コード管理
　・サロゲートキーの採番
　・日付管理
　・メール送信
　・サービス提供可否チェック
・Nablarchの提供する標準ハンドラ
　・プロセス停止制御ハンドラ
・アダプタ
　・IBM MQアダプタ  nablarch-document 6u3  なし  -  NAB-629
ブランクプロジェクト  14  RESTfulウェブサービス  変更  マルチパートリクエストのサポート  No.4およびNo.19で対応したマルチパートリクエストのサポートを取り込み、マルチパートリクエストに対応しました。  nablarch-single-module-archetype 6u3  なし  -  NAB-621
15  ウェブアプリケーション
RESTfulウェブサービス  変更  Tomcatベースイメージの更新  10.1.33以前のApache Tomcatに脆弱性が検出されたため、ブランクプロジェクトのデフォルトのTomcatのベースイメージを以下に更新しました。

　tomcat:10.1.34-jdk17-temurin  nablarch-single-module-archetype 6u3  なし  https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerWeb.html  NAB-627
16  全般  変更  gsp-dba-maven-pluginのバージョン更新  以下のMavenプラグインを記載のバージョンに更新しました。
・gsp-dba-maven-plugin：5.2.0  nablarch-single-module-archetype 6u3  なし  -  NAB-636
17  全般  変更  使用不許可APIツールのバージョン更新  No.26の対応に伴い、使用不許可APIツールのバージョンを以下に更新しました。
・nablarch-unpublished-api-checker 1.0.1  nablarch-single-module-archetype 6u3  なし  -  NAB-630
アダプタ
オブジェクトコード、ソースコード  18  Jakarta RESTful Web Servicesアダプタ  変更  Date and Time APIのサポート
(No.24.OpenAPI対応に伴う変更)  OpenAPIドキュメントとのマッピングに対応するため、Jackson Java 8 Date/timeモジュールを追加してDate and Time APIを扱えるようになりました。

※JaxRsHandlerListFactory を独自に実装している場合、バージョンアップだけでは本機能は使用できません。本機能を使用したい場合は、nablarch-jersey-adaptorおよびnablarch-resteasy-adaptorの実装を参考にしてください。  nablarch-jaxrs-adaptor 2.2.0
nablarch-jersey-adaptor 2.2.0
nablarch-resteasy-adaptor 2.2.0
nablarch-jackson-adaptor 2.2.0  なし  https://nablarch.github.io/docs/6u3/doc/application_framework/adaptors/jaxrs_adaptor.html  NAB-620
19  Jakarta RESTful Web Servicesアダプタ  変更  マルチパートリクエストのサポート
(No.24.OpenAPI対応に伴う変更)  No.4で追加したマルチパート用のBodyConverterをnablarch-jersey-adaptorおよびnablarch-resteasy-adaptorに追加しました。  nablarch-jaxrs-adaptor 2.2.0
nablarch-jersey-adaptor 2.2.0
nablarch-resteasy-adaptor 2.2.0
nablarch-jackson-adaptor 2.2.0  あり  6u2以前からのバージョンアップで本機能を使用する場合は、設定変更が必要になります。詳しくは「マルチパートリクエストのサポート対応」シートを参照してください。  https://nablarch.github.io/docs/6u3/doc/application_framework/adaptors/jaxrs_adaptor.html  NAB-621
Example
オブジェクトコード、ソースコード  20  ウェブアプリケーション (JSP)  変更  jQuery、Bootstrapのバージョンアップ  jQueryおよびjQeuryに依存していたライブラリのバージョンを以下の通り更新しました。
・jQuery 3.7.1
・jQuery UI 1.14
・Bootstrap 5.3.3
また、Bootstrapのバージョンアップに伴ってMaterial Design for Bootstrapの使用を廃止し、画面デザインを調整しました。  nablarch-example-web 6u3  -  -  なし  -  https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/web/index.html  NAB-616
21  RESTfulウェブサービス  変更  マルチパートリクエストのサポート
(No.24.OpenAPI対応に伴う変更)  No.4およびNo.19で対応したnablarch-fw-jaxrsおよびnablarch-jaxrs-adaptorの変更内容を取り込み、マルチパートリクエストに対応しました。  nablarch-example-rest 6u3  なし  -  NAB-621
22  全般  変更  gsp-dba-maven-pluginのバージョン更新  以下のMavenプラグインを記載のバージョンに更新しました。
・gsp-dba-maven-plugin：5.2.0  nablarch-example-web  6u3
nablarch-example-thymeleaf-web  6u3
nablarch-example-rest  6u3
nablarch-example-batch  6u3
nablarch-example-batch-ee  6u3
nablarch-example-http-messaging  6u3
nablarch-example-http-messaging-send  6u3
nablarch-example-db-queue  6u3
nablarch-example-mom-delayed-receive  6u3
nablarch-example-mom-delayed-send  6u3
nablarch-example-mom-sync-receive  6u3
nablarch-example-mom-sync-send-batch  6u3  なし  -  NAB-636
実装サンプル集
オブジェクトコード、ソースコード  23  検索結果の一覧表示  変更  タグファイルのスタイル適用設定修正  ページングの現在表示中のページ番号部分に対して、カスタムタグで指定したスタイルが適用されていなかったため、表示中かどうかに関わらず設定したCSSが適用されるように修正しました。  nablarch-biz-sample-all 3.1.0  -  -  なし  -  https://nablarch.github.io/docs/6u3/doc/biz_samples/03/index.html  NAB-616
Nablarch開発標準
開発プロセス支援ツール  24  Nablarch OpenAPI Generator  追加  Nablarch OpenAPI Generatorのリリース  OpenAPIドキュメントからアプリケーションのコード生成をサポートするツールである Nablarch OpenAPI Generator をリリースしました。  nablarch-openapi-generator 1.0.0  -  -  なし  -  https://nablarch.github.io/docs/6u3/doc/development_tools/toolbox/NablarchOpenApiGenerator/NablarchOpenApiGenerator.html  NAB-624
25  SQL Executor  変更  解説書の手順と実際のモジュールの構成差異を修正  ツールの提供状態として設定すべき項目に不足があり、また解説書で案内している設定ファイル名と実際のファイル名に乖離がありました。
このため解説書どおりに実行しても起動できないという問題が発生しており、解説書記載の手順で実行できるように設定ファイルの見直しを行いました。  sql-executor 1.3.1  -  -  なし  -  https://nablarch.github.io/docs/6u3/doc/development_tools/toolbox/SqlExecutor/SqlExecutor.html  NAB-637
26  使用不許可APIチェックツール  不具合  Java21でjava.lang.Objectのメソッドが許可できない場合がある問題に対応  Java21でバイトコードが変わったことにより、インタフェースからjava.lang.Objectのメソッドを呼んでいる場合、設定ファイルで指定しても許可されないという不具合があったため対応しました。

例) 
■使用不許可APIツールの設定ファイル
java.lang.Object

■解析対象のjavaファイル
// toStringメソッドは本来許可されるはずだが不許可になる
Map<String, String> headers = request.headers();
headers.toString();  nablarch-unpublished-api-checker 1.0.1  1.0.0  -  なし  -  https://nablarch.github.io/docs/LATEST/doc/development_tools/java_static_analysis/index.html#id6  NAB-630
■バージョンアップ手順
本リリースの適用手順は、次の通りです。
No  適用手順
1  pom.xmlの<dependencyManagement>セクションに指定されているnablarch-bomのバージョンを6u3に書き換える
2  mavenのビルドを再実行する
■Jakarta RESTful Web Servicesアダプタでマルチパートリクエストを扱うための設定変更手順
【本手順の適用対象となるシステム】
本手順は、以下の条件をすべて満たすシステムを対象としています。
・Nablarch 6u2以前からのバージョンアップであること
・Jakarta RESTful Web ServicesアダプタのJerseyJaxRsHandlerListFactoryまたはResteasyJaxRsHandlerListFactoryを使用していること
※RESTfulウェブサービスのブランクプロジェクトは、デフォルトでJerseyJaxRsHandlerListFactoryを使用するように構成されています
・Nablarchの標準機能を使用して、RESTfulウェブサービスでマルチパートリクエストを扱いたい
【変更内容の概要】
Nablarch 6u3では、RESTfulウェブサービスでマルチパートリクエストを扱えるようにするためにマルチパート用のBodyConverterを追加しています。
それに伴いJakarta RESTful Web ServicesアダプタのJerseyJaxRsHandlerListFactoryおよびResteasyJaxRsHandlerListFactoryに
該当のBodyConverterを追加していますが、マルチパートをリクエストを扱うためにはさらに以下の対応を行う必要があります。
・コンポーネント定義ファイルへのファイルパス設定、ファイルアップロード機能設定の追加
・ハンドラキューへのマルチパートリクエストハンドラの追加
・ファイルアップロード用の一時ディレクトリやアップロードサイズの上限などのプロパティの設定
これらの変更を行うことにより、RESTfulウェブサービスでマルチパートリクエストが扱えるようになり、ファイルアップロードが可能になります。
【変更手順】
【コンポーネント定義ファイルへのファイルパス設定、ファイルアップロード機能設定の追加】
src/main/resources/rest-component-configuration.xml に以下の設定を追加します。
<!-- ファイルパス設置 -->
<import file="nablarch/webui/filepath-for-webui.xml" />
<!-- ファイルアップロード機能設定 -->
<import file="nablarch/webui/multipart.xml" />
【ハンドラキューへのマルチパートリクエストハンドラの追加】
src/main/resources/rest-component-configuration.xml のハンドラキュー(webFrontController)に以下の定義を追加してください。
<component-ref name="multipartHandler"/>
追加位置は、セッション変数保存ハンドラおよびCSRFトークン検証ハンドラの制約事項を確認して決定してください。
https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/handlers/web/SessionStoreHandler.html#session-store-handler-constraint
https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/handlers/web/csrf_token_verification_handler.html#id4
また、環境ごとにハンドラキューを上書きしている場合は、そちらのハンドラキュー定義にも反映してください。
【ファイルアップロード用の一時ディレクトリやアップロードサイズの上限などのプロパティの設定】
ファイルパス設定を追加したことにより、以下のプロパティを定義する必要があります。
src/main/resources/common.properties
nablarch.uploadSettings.contentLengthLimit
src/env/[環境別]/resources/env.properties
nablarch.filePathSetting.basePathSettings.format
nablarch.filePathSetting.basePathSettings.output
nablarch.uploadSettings.autoCleaning
nablarch.filePathSetting.basePathSettings.uploadFileTmpDir
設定内容は、マルチパートリクエストハンドラを確認してください。
https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/handlers/web/multipart_handler.html
「nablarch.filePathSetting.basePathSettings.format」は汎用データフォーマットのフォーマット定義ファイル用のパス設定ですが、
汎用データフォーマットを使用しないのであればダミー値でかまいません。
