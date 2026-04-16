# Nablarch 6u3 リリースノート

## No.1 親クラス・インタフェースでのリソース定義に対応
(No.24.OpenAPI対応に伴う変更)

**リリース区分**: 変更  **分類**: RESTfulウェブサービス

OpenAPIドキュメントから生成したインタフェースを使用してアクションクラスを実装できるように、インターフェースや親クラスでのリソース定義を引き継ぐように対応しました。

@PathなどのJakarta RESTful Web Servicesのアノテーションを使ってアクションクラスを実装している場合に、以下の条件でアクションクラスが実装しているインターフェースや親クラスのリソース定義を引き継ぎます。
　・アクションクラスが親クラスを継承またはインターフェースを実装している
　・親クラスまたはインターフェースに@Pathアノテーションが注釈されている
　・親クラスまたはインターフェースにHTTPメソッドが定義されている

また、本対応にはルーティングアダプタも修正する必要があったため、合わせて対応しました。

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/web_service/rest/feature_details/resource_signature.html

## No.2 EntityResponseの型パラメータ追加
(No.24.OpenAPI対応に伴う変更)

**リリース区分**: 変更  **分類**: RESTfulウェブサービス

OpenAPIドキュメントとのマッピングに対応するため、EntityResponseに型パラメータを追加しました。
これにより、どのようなエンティティの型をレスポンスとしているかをより明確に表現できるようになりました。

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/web_service/rest/feature_details/resource_signature.html

## No.3 Date and Time APIサポート拡充
(No.24.OpenAPI対応に伴う変更)

**リリース区分**: 変更  **分類**: BeanUtil

OpenAPIドキュメントとのマッピングに対応するため、Date and Time APIのサポートを拡充し、OffsetDateTimeのサポートを追加しました。

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/libraries/bean_util.html

## No.4 マルチパート用のBodyConverter追加
(No.24.OpenAPI対応に伴う変更)

**リリース区分**: 変更  **分類**: RESTfulウェブサービス

OpenAPIドキュメントとのマッピングに対応するため、Content-Typeがmultipart/form-dataのリクエストに対応するBodyConverterを追加しました。

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/web_service/rest/feature_details/resource_signature.html

## No.5 MapからBeanへ移送するメソッドのパフォーマンス改善

**リリース区分**: 変更  **分類**: BeanUtil

MapからBeanへ移送する際、ネストしたオブジェクト数が多い場合に処理が遅くなる事象が発生していたので、修正しました。

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/libraries/bean_util.html

## No.6 JSONの読み取りに失敗する問題を修正

**リリース区分**: 不具合  **分類**: 汎用データフォーマット

JSON内に含まれる値（""で囲われた項目）がJSON構文で意味を持つ区切り文字（:、[、{、, の4つ）のみで、かつその後にデータが続く場合、値とJSON構文の区切り文字の区別ができずに失敗していました。

①NGになる例（":"の後にデータが続く）：
  {"key1": ":", "key2": "value2"}

②OKになる例（":"の後にデータが続かない）：
  {"key1": ":"}

NGになっていた例も、正常に値として解析できるように修正しました。

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/libraries/data_io/data_format.html

## No.7 BeanValidationStrategyのバリデーション処理をカスタマイズできるように修正

**リリース区分**: 変更  **分類**: Bean Validation

BeanValidationStrategyをカスタマイズしやすくなるよう、公開APIを見直しました。
それに伴い、バリデーションエラーのメッセージをソートするsortMessagesメソッドをオーバーライド可能にするため、static修飾子を除去しました。

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/libraries/validation/bean_validation.html

## No.8 公開APIの追加

**リリース区分**: 変更  **分類**: 公開API

解説書で継承を案内しているAPIの中で公開APIになっていないものがあったため、公開APIを追加しました。

## No.9 ResumeDataReaderのJavadoc改善

**リリース区分**: 変更  **分類**: Nablarchバッチアプリケーション

ResumeDataReaderが内部的に使用するResumePointManagerは初期化が必要ですが、
この点をResumeDataReaderに関する説明から読み取りづらかったため、ResumeDataReaderのJavadocに追記しました。

参照先: https://nablarch.github.io/docs/6u3/javadoc/nablarch/fw/reader/ResumeDataReader.html

## No.10 TableIdGeneratorのJavadoc改善

**リリース区分**: 変更  **分類**: サロゲートキーの採番

採番の際に独立したトランザクションを用いるFastTableIdGeneratorは初期化が必要ですが、Javadoc上でそれがわからなかったため、その旨を追記しました。
また類似のコンポーネントであるTableIdGeneratorのJavadocにも、記述を合わせるため同様の更新を行っています。

参照先: https://nablarch.github.io/docs/6u3/javadoc/nablarch/common/idgenerator/FastTableIdGenerator.html

## No.11 Base64UtilのJavadoc・解説書改善

**リリース区分**: 変更  **分類**: 汎用ユーティリティ

Base64UtilはRFC4648の「4. Base 64 Encoding」に準拠していますが、Javadoc上で明記できていなかったため、その旨を追記しました。

また、Java8以降ではBase64エンコーディングを行う標準APIが提供されており、Base64Utilを使用せずとも同様の処理を行えます。
Base64Utilを使用する必要性が小さくなったため、Javadocで標準APIを案内し、Base64Utilは後方互換性のための位置付けとしました。
そのため、Base64Utilは後方互換のために存在していることを解説書に追記しました。
※現在Base64Utilを使用している個所を標準APIに置換する必要はありません。

参照先: https://nablarch.github.io/docs/6u3/javadoc/nablarch/core/util/Base64Util.html

## No.12 PublishedアノテーションのJavadoc改善

**リリース区分**: 変更  **分類**: 公開API

PublishedアノテーションのJavadocで、オーバーライド可能なメソッドは公開APIとしていることについて追記しました。

参照先: https://nablarch.github.io/docs/6u3/javadoc/nablarch/core/util/annotation/Published.html

## No.13 初期化が必要なコンポーネントに対する説明の改善

**リリース区分**: 変更  **分類**: コンポーネントの初期化

コンポーネントとして使用することを想定して提供しているクラスのうち、初期化が必要であるにも関わらず解説書への記載がないものがあったので、初期化が必要な旨や設定例を追記しました。

・Nablarchが提供するライブラリ
　・コード管理
　・サロゲートキーの採番
　・日付管理
　・メール送信
　・サービス提供可否チェック
・Nablarchの提供する標準ハンドラ
　・プロセス停止制御ハンドラ
・アダプタ
　・IBM MQアダプタ

## No.14 マルチパートリクエストのサポート

**リリース区分**: 変更  **分類**: RESTfulウェブサービス

No.4およびNo.19で対応したマルチパートリクエストのサポートを取り込み、マルチパートリクエストに対応しました。

## No.15 Tomcatベースイメージの更新

**リリース区分**: 変更  **分類**: ウェブアプリケーション
RESTfulウェブサービス

10.1.33以前のApache Tomcatに脆弱性が検出されたため、ブランクプロジェクトのデフォルトのTomcatのベースイメージを以下に更新しました。

　tomcat:10.1.34-jdk17-temurin

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/blank_project/setup_containerBlankProject/setup_ContainerWeb.html

## No.16 gsp-dba-maven-pluginのバージョン更新

**リリース区分**: 変更  **分類**: 全般

以下のMavenプラグインを記載のバージョンに更新しました。
・gsp-dba-maven-plugin：5.2.0

## No.17 使用不許可APIツールのバージョン更新

**リリース区分**: 変更  **分類**: 全般

No.26の対応に伴い、使用不許可APIツールのバージョンを以下に更新しました。
・nablarch-unpublished-api-checker 1.0.1

## No.18 Date and Time APIのサポート
(No.24.OpenAPI対応に伴う変更)

**リリース区分**: 変更  **分類**: Jakarta RESTful Web Servicesアダプタ

OpenAPIドキュメントとのマッピングに対応するため、Jackson Java 8 Date/timeモジュールを追加してDate and Time APIを扱えるようになりました。

※JaxRsHandlerListFactory を独自に実装している場合、バージョンアップだけでは本機能は使用できません。本機能を使用したい場合は、nablarch-jersey-adaptorおよびnablarch-resteasy-adaptorの実装を参考にしてください。

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/adaptors/jaxrs_adaptor.html

## No.19 マルチパートリクエストのサポート
(No.24.OpenAPI対応に伴う変更)

**リリース区分**: 変更  **分類**: Jakarta RESTful Web Servicesアダプタ

No.4で追加したマルチパート用のBodyConverterをnablarch-jersey-adaptorおよびnablarch-resteasy-adaptorに追加しました。

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/adaptors/jaxrs_adaptor.html

## No.20 jQuery、Bootstrapのバージョンアップ

**リリース区分**: 変更  **分類**: ウェブアプリケーション (JSP)

jQueryおよびjQeuryに依存していたライブラリのバージョンを以下の通り更新しました。
・jQuery 3.7.1
・jQuery UI 1.14
・Bootstrap 5.3.3
また、Bootstrapのバージョンアップに伴ってMaterial Design for Bootstrapの使用を廃止し、画面デザインを調整しました。

参照先: https://nablarch.github.io/docs/6u3/doc/application_framework/application_framework/web/index.html

## No.21 マルチパートリクエストのサポート
(No.24.OpenAPI対応に伴う変更)

**リリース区分**: 変更  **分類**: RESTfulウェブサービス

No.4およびNo.19で対応したnablarch-fw-jaxrsおよびnablarch-jaxrs-adaptorの変更内容を取り込み、マルチパートリクエストに対応しました。

## No.22 gsp-dba-maven-pluginのバージョン更新

**リリース区分**: 変更  **分類**: 全般

以下のMavenプラグインを記載のバージョンに更新しました。
・gsp-dba-maven-plugin：5.2.0

## No.23 タグファイルのスタイル適用設定修正

**リリース区分**: 変更  **分類**: 検索結果の一覧表示

ページングの現在表示中のページ番号部分に対して、カスタムタグで指定したスタイルが適用されていなかったため、表示中かどうかに関わらず設定したCSSが適用されるように修正しました。

参照先: https://nablarch.github.io/docs/6u3/doc/biz_samples/03/index.html

## No.24 Nablarch OpenAPI Generatorのリリース

**リリース区分**: 追加  **分類**: Nablarch OpenAPI Generator

OpenAPIドキュメントからアプリケーションのコード生成をサポートするツールである Nablarch OpenAPI Generator をリリースしました。

参照先: https://nablarch.github.io/docs/6u3/doc/development_tools/toolbox/NablarchOpenApiGenerator/NablarchOpenApiGenerator.html

## No.25 解説書の手順と実際のモジュールの構成差異を修正

**リリース区分**: 変更  **分類**: SQL Executor

ツールの提供状態として設定すべき項目に不足があり、また解説書で案内している設定ファイル名と実際のファイル名に乖離がありました。
このため解説書どおりに実行しても起動できないという問題が発生しており、解説書記載の手順で実行できるように設定ファイルの見直しを行いました。

参照先: https://nablarch.github.io/docs/6u3/doc/development_tools/toolbox/SqlExecutor/SqlExecutor.html

## No.26 Java21でjava.lang.Objectのメソッドが許可できない場合がある問題に対応

**リリース区分**: 不具合  **分類**: 使用不許可APIチェックツール

Java21でバイトコードが変わったことにより、インタフェースからjava.lang.Objectのメソッドを呼んでいる場合、設定ファイルで指定しても許可されないという不具合があったため対応しました。

例) 
■使用不許可APIツールの設定ファイル
java.lang.Object

■解析対象のjavaファイル
// toStringメソッドは本来許可されるはずだが不許可になる
Map<String, String> headers = request.headers();
headers.toString();

参照先: https://nablarch.github.io/docs/LATEST/doc/development_tools/java_static_analysis/index.html#id6
