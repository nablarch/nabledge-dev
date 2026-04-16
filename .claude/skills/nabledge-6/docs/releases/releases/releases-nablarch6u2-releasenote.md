# Nablarch 6u2 リリースノート

## No.1 Jakarta EE 10対応

**リリース区分**: 変更  **分類**: 全般

Jakarta EE 10に対応しました。
これにより、Jakarta EE 10に対応しているアプリケーションサーバ上で動作するようになりました。

参照先: https://nablarch.github.io/docs/6u2/doc/migration/index.html

## No.2 Java EEの仕様名等をJakarta EEのものに変更

**リリース区分**: 変更  **分類**: 全般

Jakarta EE 10対応に伴い、Java EEの仕様名及び関連する記載を、Jakarta EEのものに変更しました。

## No.3 必要Javaバージョンの変更

**リリース区分**: 変更  **分類**: 稼働環境

No.1 の対応に伴い、動作に必要なJavaのバージョンを 17 に変更しました。

## No.4 公開APIの追加

**リリース区分**: 変更  **分類**: 公開API

解説書で案内しているAPIの中で公開APIになっていないものがあったため、公開APIを追加しました。

## No.5 システム日時をLocalDateTime型で取得できる機能を追加

**リリース区分**: 変更  **分類**: システム日時

SystemTimeUtilを用いたシステム日時の取得で、従来の Date 型に加え、Java 8で導入されたDate and Time APIの LocalDateTime型での取得に対応しました。

参照先: https://nablarch.github.io/docs/6u2/publishedApi/nablarch-all/publishedApiDoc/programmer/nablarch/core/date/SystemTimeUtil.html

## No.6 ユニバーサルDAOのエンティティ生成機能をDate and Time APIに対応

**リリース区分**: 変更  **分類**: ユニバーサルDAO

ユニバーサルDAOで検索結果をマッピングするBeanに使用できるデータタイプとして、Java 8で導入されたDate and Time APIの LocalDateTime型とLocalDate型に対応しました。

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/application_framework/libraries/database/universal_dao.html#id43

## No.7 BeanUtilをレコードに対応

**リリース区分**: 変更  **分類**: BeanUtil

BeanUtilの対象として、Java 16で導入されたレコードを使用できるように対応しました。これにより、レコードオブジェクトの生成や、レコードオブジェクトからの値のコピーができるようになります。

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/application_framework/libraries/bean_util.html

## No.8 JSR310アダプタの標準機能への取り込み

**リリース区分**: 変更  **分類**: BeanUtil

JSR310(Date and Time API)アダプタで提供されている機能をフレームワーク本体に取り込みました。これにより、JSR310アダプタを使用せずとも、BeanUtilでJSR310を使用可能になりました。
JSR310アダプタは後方互換を維持するために残しており、処理は本体へ委譲するように変更しています。JSR310アダプタを使用している場合でも設定変更なく今まで通り使用できますので、影響はありません。

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/application_framework/libraries/bean_util.html

## No.9 業務画面JSP検証ツールの削除

**リリース区分**: 削除  **分類**: Toolbox

UI開発基盤はNablarch 6では提供しない方針であるため、UI開発基盤に依存する業務画面JSP検証ツールを削除しました。

## No.10 Jettyの一時ディレクトリのデフォルト値を変更

**リリース区分**: 変更  **分類**: デフォルト設定一覧

JettyがJSPをコンパイルする際などに使用する一時ディレクトリは nablarch.httpTestConfiguration.tempDirectory プロパティで設定します。このプロパティのデフォルト値を「work」から「target/tmp」に変更しました。
この一時ディレクトリに出力される内容は利用者が気にすべきものではないため、Mavenのcleanで削除されるようにtargetディレクトリ配下としています。

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/application_framework/configuration/index.html

## No.11 Java標準APIのJavadocリンク先をJava 17のJavadocに変更

**リリース区分**: 変更  **分類**: 全般

解説書内にあるJava標準APIのJavadocリンク先を、稼働環境にあわせてJava 17のJavadocに変更しました。

参照先: https://nablarch.github.io/docs/6u2/doc/index.html

## No.12 テスト環境のアプリケーションサーバを更新

**リリース区分**: 変更  **分類**: 稼動環境

テスト環境のアプリケーションサーバを以下の通り更新しました。赤字部分が変更箇所になります。
・WebSphere Application Server Liberty 24.0.0.8
・Open Liberty 24.0.0.8
・Red Hat JBoss Enterprise Application Platform 8.0.0
・WildFly 33.0.0.Final
・Apache Tomcat 10.1.17

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/application_framework/nablarch/platform.html

## No.13 分散トレーシングの依存ライブラリのバージョンを変更

**リリース区分**: 変更  **分類**: AWSにおける分散トレーシング

AWSにおける分散トレーシングの実装例として案内している依存ライブラリ（AWS X-Ray SDK、Jersey）がJakarta EE未対応のバージョンだったため、Jakarta EE対応済のバージョンに修正し、あわせてコード例の修正を行いました。
修正後のバージョンは以下の通りです。
AWS X-Ray SDK：2.15.0
Jersey：3.1.1

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/application_framework/cloud_native/distributed_tracing/aws_distributed_tracing.html

## No.14 ウェブ、RESTfulウェブサービスプロジェクトの疎通確認で不要な手順を削除

**リリース区分**: 変更  **分類**: ブランクプロジェクト

ウェブプロジェクト、RESTfulウェブサービスプロジェクトの疎通確認では、"compile"を実行後、"jetty:run"を実行するよう案内していました。
"compile"は"jetty:run"を実行する際に合わせて実行され、明示的に実行する必要がないため、削除しました。

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/application_framework/blank_project/setup_blankProject/setup_Web.html

## No.15 静的解析ツールのバージョン更新

**リリース区分**: 変更  **分類**: 全般

SpotBugsのバージョンを 4.8.6 に、FindSecurityBugsのバージョンを 1.13.0 に更新しました。

## No.16 デフォルトのTomcat 10のコンテナイメージの更新

**リリース区分**: 変更  **分類**: 全般

デフォルトで指定しているTomcat 10のコンテナイメージを 10.1.28-jdk17-temurin に更新しました。

## No.17 Mavenプラグインのバージョン更新

**リリース区分**: 変更  **分類**: 全般

以下のMavenプラグインを記載のバージョンに更新しました。
・maven-source-plugin：3.3.1
・maven-javadoc-plugin：3.10.0
・maven-gpg-plugin：3.2.5
・maven-compilier-plugin：3.13.0
・maven-surefire-plugin：3.5.0
・maven-antrun-plugin：3.1.0
・maven-war-plugin：3.4.0
・maven-assembly-plugin：3.7.1
・maven-jar-plugin：3.4.2
・maven-resources-plugin：3.3.1
・maven-release-plugin：3.1.1
・maven-deploy-plugin：3.1.3
・maven-install-plugin：3.1.3
・jacoco-maven-plugin：0.8.12
・build-helper-maven-plugin：3.6.0
・jib-maven-plugin：3.4.3
・jetty-ee10-maven-plugin：12.0.12

## No.18 不要なMavenプラグイン設定の削除

**リリース区分**: 変更  **分類**: 全般

以下のMavenプラグインは使用しないため、設定を削除しました。
・maven-failsafe-plugin
・maven-dependency-plugin
・wagon-webdav-jackrabbit

## No.19 Maven Archetype Plugin 3.xに対応

**リリース区分**: 変更  **分類**: 全般

これまでブランクプロジェクト作成時に警告が出力されていましたが、使用するMaven Archetype Pluginのバージョンを 3.2.1 に更新し、警告が出力されないように対応しました。

これにより、ブランクプロジェクト作成時に過去のバージョンのMaven Archetype Pluginを指定する必要がなくなったため、ブランクプロジェクト作成用のバッチファイルは削除しました。

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/application_framework/blank_project/setup_blankProject/setup_Web.html
※その他のブランクプロジェクトの初期セットアップ手順も同様

## No.20 maven-clean-plugin 設定の削除

**リリース区分**: 削除  **分類**: ウェブアプリケーション

No.10の変更に伴い、maven-clean-plugin による work/jsp 削除が不要になったため、maven-clean-pluginの設定を削除しました。

## No.21 Jacksonのバージョン更新

**リリース区分**: 変更  **分類**: RESTfulウェブサービス

Jacksonのバージョンを 2.17.1 に更新しました。

## No.22 Logback、SLF4Jのバージョン更新

**リリース区分**: 変更  **分類**: Jakarta Batchに準拠したバッチアプリケーション

Logbackのバージョンを 1.5.6 に、SLF4Jのバージョンを 2.0.11 に更新しました。
また、あわせて以下の不要な依存関係を削除しました。
・slf4j-nablarch-adaptor
・nablarch-jboss-logging-adaptor

## No.23 JBeretに関連するライブラリのバージョン更新

**リリース区分**: 変更  **分類**: Jakarta Batchに準拠したバッチアプリケーション

JBeretのバージョンを 2.1.4.Final に更新しました。
また、JBeretに必要なライブラリが不足していたため、合わせて依存関係の定義を修正しました。

## No.24 Nablarch 6 対応

**リリース区分**: 変更  **分類**: 全般

Nablarch 6と組み合わせて使用できるように依存関係を変更しました。

## No.25 SLF4Jのバージョン更新

**リリース区分**: 変更  **分類**: SLF4Jアダプタ

SLF4Jは 2.0 からロギング実装を検索する仕組みが変更されており、SLF4Jアダプタはこの仕組みに対応していないため、SLF4J 2.0以降のバージョンではログ出力ができませんでした。
SLF4Jの2.0以降でもSL4Jアダプタが使用できるように、依存するSLF4Jのバージョンを 2.0.11 に更新しました。

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/adaptors/slf4j_adaptor.html

## No.26 SLF4Jのバージョン更新

**リリース区分**: 変更  **分類**: logアダプタ

SLF4Jが2.0以降でもlogアダプタが使用できるように、依存するSLF4Jのバージョンを 2.0.11 に更新しました。

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/adaptors/log_adaptor.html

## No.27 JBoss Loggingのバージョン更新

**リリース区分**: 変更  **分類**: logアダプタ

JBoss Loggingのバージョンを 3.6.0.Final に更新しました。

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/adaptors/log_adaptor.html

## No.28 Domaのバージョン更新

**リリース区分**: 変更  **分類**: Domaアダプタ

Java 17以降をサポートするにあたり、Domaのバージョンを 2.66.0 に更新しました。
これに伴い、Doma 2.44.0 より以下のAPIが非推奨になったため、解説書で案内している実装例を変更しました。
・Daoアノテーションのconfig属性
・SingletonConfigアノテーション
（以前に案内していた、上記の非推奨となったAPIを使用した実装も引き続き利用できます）

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/adaptors/doma_adaptor.html

## No.29 Jacksonのバージョン更新

**リリース区分**: 変更  **分類**: Jakarta RESTful Web Servicesアダプタ

Jacksonのバージョンを 2.17.1 に更新しました。

参照先: https://nablarch.github.io/docs/6u2/doc/application_framework/adaptors/jaxrs_adaptor.html

## No.30 Nablarch 6 対応

**リリース区分**: 変更  **分類**: 全般

Nablarch 6を使用するように修正しました。

## No.31 Jersey、Jacksonのバージョン更新

**リリース区分**: 変更  **分類**: RESTfulウェブサービス

Jerseyのバージョンを 3.1.8 に、Jacksonのバージョン 2.17.1 に更新しました。

## No.32 ActiveMQ Artemisのバージョン更新

**リリース区分**: 変更  **分類**: MOMによるメッセージング

ActiveMQ Artemisのバージョンを 2.37.0 に更新しました。
また、 nablarch-example-mom-testing-common で使用していたActiveMQ ArtemisのAPIが非推奨になったため、代替APIを使うように変更しました。

## No.33 解説書からの削除

**リリース区分**: 削除  **分類**: 全般

ETL基盤はNablarch 6では提供しない方針であるため、解説書から削除しました。

## No.34 解説書からの削除

**リリース区分**: 削除  **分類**: 全般

帳票ライブラリはNablarch 6では提供しない方針であるため、解説書から削除しました。

## No.35 解説書からの削除

**リリース区分**: 削除  **分類**: 全般

ワークフローライブラリはNablarch 6では提供しない方針であるため、解説書から削除しました。

## No.36 解説書からの削除

**リリース区分**: 削除  **分類**: 全般

UI開発基盤はNablarch 6では提供しない方針であるため、解説書から削除しました。

## No.37 Nablarch 6 対応

**リリース区分**: 変更  **分類**: 全般

Nablarch 6で開発したアプリケーションのテストに対応しました。
これに伴い、Jetty 12を使用するように変更しました。

## No.38 Junit 5のバージョン更新

**リリース区分**: 変更  **分類**: 全般

JUnit 5のバージョンを 5.11.0 に更新しました。

## No.39 Nablarch 6 対応

**リリース区分**: 変更  **分類**: 全般

Nablarch 6 を使用するように修正しました。
合わせて、ソースコードの公開先を nablarch-biz-sample-all リポジトリに集約しました。

参照先: https://nablarch.github.io/docs/6u2/doc/examples/index.html

## No.40 Jakarta EE 10対応による修正

**リリース区分**: 追加  **分類**: 全般

Jakarta EE 10対応に伴い、Java EEの仕様名や関連する記載をJakarta EEのものに変更しました。変更しない方が望ましいと判断した箇所については、Jakarta EEにおける仕様の省略名の読み替えを追記しました。

## No.41 JSP自動生成ツールの記載削除

**リリース区分**: 削除  **分類**: 標準WBS

UI開発基盤はNablarch 6では提供しない方針であるため、UI開発基盤の使用が前提であるJSP自動生成ツールの記載を削除しました。

## No.42 Bean Validationを使用する記載に修正

**リリース区分**: 変更  **分類**: ドメイン定義書サンプル

「2.1. Nablarch標準提供バリデーション」にはNablarch Validationを記載していましたが、現在の推奨であるBean Validationに変更しました。

## No.43 業務画面JSP検証ツールの記載削除

**リリース区分**: 削除  **分類**: 開発プロセス支援ツール

No.9 の変更に伴い、業務画面JSP検証ツールの記載を削除しました。
